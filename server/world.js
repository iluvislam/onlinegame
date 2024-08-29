
class World {
  constructor(network, worlds_map, items_map, player) {
    this.network = network;
    this.worlds_map = worlds_map;
    this.items_map = items_map;
    this.player = player;
  };
  
  change_weather(worldname, weather){
    let theworld = this.worlds_map.get(worldname)
    theworld.weather = [weather[0], weather[1], weather[2]]
    let data = [`weather_${weather[0]}_${weather[1]}_${weather[2]}`];
    this.player.broadcast('all_in_world', null, data, worldname);
  };
  
  get_weather(worldname){
    let theworld = this.worlds_map.get(worldname)
    if(!theworld) return [0, 0, 0];
    return [theworld.weather[0], theworld.weather[1], theworld.weather[2]];
  };
  
  world_edit(mouse_data, peer){
    let world = this.worlds_map.get(peer.c_world);
    let obj = JSON.parse(mouse_data);
    let wr = world.world;
	  let x = obj[0];
	  let y = obj[1];
	  let w = obj[2];
	  let h = obj[3];
	  let mousetype = obj[4];
    for (let i = 0; i < wr.length; i++) {
      if (x<wr[i][0]+wr[i][2] && x+w>wr[i][0] && y<wr[i][1]+wr[i][3] && y+h>wr[i][1]){
        if(mousetype == 1 && wr[i][4] > 0){
          this.item_break_handler(peer.c_world, i);
          break;
        }else if (mousetype == 3 && wr[i][4] < 1 && Object.keys(peer.inventory).length){
          let index_inv = obj[5];
          this.item_place_handler(peer, peer.c_world, i, index_inv);
          break;
        };
      };
    };
  };
  
  item_place_handler(peer, worldname, i, inv_i){
    let world = this.worlds_map.get(worldname);
    if(world){
      let worldi = world.world[i]; //[x,y,w,h,id]
      let peerinvlist = Object.entries(peer.inventory);
      if(peerinvlist && peerinvlist[inv_i]){
        let item = this.items_map.get(parseInt(peerinvlist[inv_i][0]));
        if(item){
          if(item.type == 1 && !(peer.x<world.world[i][0]+world.world[i][2] && peer.x+peer.w>world.world[i][0] && peer.y<world.world[i][1]+world.world[i][3] && peer.y+peer.h>world.world[i][1])){
            world.world[i] = [worldi[0], worldi[1], worldi[2], worldi[3], peerinvlist[inv_i][0]];
            let data = [`worlde_set_[${worldi[0]}, ${worldi[1]}, ${worldi[2]}, ${worldi[3]}, ${peerinvlist[inv_i][0]}]_${i}`]
            this.player.inventory_manager('pop', peer, peerinvlist[inv_i][0], 1);
            this.player.broadcast('all_in_world', null, data, worldname);
          }else if(item.type == 2 && peer.x<world.world[i][0]+world.world[i][2] && peer.x+peer.w>world.world[i][0] && peer.y<world.world[i][1]+world.world[i][3] && peer.y+peer.h>world.world[i][1]){
            this.player.wear_item(peer, item);
          };
        };
      };
    };
  };
  
  item_break_handler(worldname, i){
    let world = this.worlds_map.get(worldname);
    if(world){
      let worldi = world.world[i]; //[x,y,w,h,id]
      let item = this.items_map.get(parseInt(worldi[4]));
      if(item){
        world.world[i] = [worldi[0], worldi[1], worldi[2], worldi[3], 0];
        let data = [`particle_[${worldi[0]},${worldi[1]},20,15,[129,31,0]]`, `worlde_set_[${worldi[0]}, ${worldi[1]}, ${worldi[2]}, ${worldi[3]}, 0]_${i}`]
        this.player.broadcast('all_in_world', null, data, worldname);
      };
    };
  };
  
  world_gen(name, wx = 50, wy = 50){
    if(!this.check_world_name(name) && !this.worlds_map.get(name)){
		  let d = new worldinfo();
		  d.world = this.generate_world(wx,wy,20); //if the world is 50 width that means its 1000 pixels
		  d.name = name;
		  d.maxp_x = wx*20;
		  d.maxp_y = wy*20;
      d.sp_x = d.maxp_x/2-10;
      d.sp_y = d.maxp_y/2-10;
		  this.worlds_map.set(d.name, d);
      return true;
	  };    
  };
  
  world_enter(name, peer){
    name = name.toLowerCase();
    if(name === 'exit'){
      this.player.player_logout(peer.name);
    }else if(this.check_world_name(name)){
      this.network.peer_send(`chatbox_${this.check_world_name(name)}`, peer.address.address,peer.address.port);
    }else{
      if(this.worlds_map.get(peer.c_world)){
        this.player.broadcast('world_exit', peer);
        delete this.worlds_map.get(peer.c_world).peers[peer.name];
      };
      this.world_gen(name);
      let world = this.worlds_map.get(name);
      if(world){
        if(!world.peers[peer.name]){
          world.peers[peer.name] = peer;
        }else{
          delete world.peers[peer.name];
          world.peers[peer.name] = peer;
        };
        peer.c_world = world.name;  
        this.network.peer_send(`world_${JSON.stringify(world.world)}_${world.name}_${world.maxp_x}_${world.maxp_y}_${peer.name}_${world.sp_x}_${world.sp_y}`, peer.address.address,peer.address.port);
        let dropped_items = this.dropped_data(world.name);
        if(dropped_items){
          this.network.peer_send(`itemdrop_set_${dropped_items}`, peer.address.address,peer.address.port);
        };
        this.player.broadcast('world_enter', peer);
      };
    };
  };
  
  dropped_data(wn){
    let theworld = this.worlds_map.get(wn);
    if(!theworld) return;
    if(!theworld.dropped) return; 
    return theworld.dropped.join('|');
  };
  
  dropped_colli(peer){
    let theworld = this.worlds_map.get(peer.c_world);
    if(!theworld) return;
    if(!theworld.dropped) return;
    for(let i = 0;i < theworld.dropped.length;i++){
      let rect = theworld.dropped[i];
      if (rect[1]<peer.x+peer.w && rect[1]+rect[3]>peer.x && rect[2]<peer.y+peer.h && rect[2]+rect[4]>peer.y){
        this.drop_collect(peer, i);
      };
    };
  };
  
  drop_collect(peer, i){
    let theworld = this.worlds_map.get(peer.c_world);
    if(!theworld) return;
    if(!theworld.dropped) return;
    this.player.inventory_manager('push', peer, theworld.dropped[i][0], theworld.dropped[i][5]); 
    this.drop_manager('pop', peer.c_world, i);
  };
  
  drop_manager(type, worldname, i=0, itemid = 0, itemc = 0, x = 0, y = 0){
    let world = this.worlds_map.get(worldname);
    if(!world) return;
    i = parseInt(i);
    itemid = parseInt(itemid);
    itemc = parseInt(itemc);
    x = parseInt(x);
    y = parseInt(y);    
    let data = '';
    if(type == 'push'){
      let w = 10;
      let h = 10;
      world.dropped.push([itemid, x, y, w, h, itemc]);
      data = [`itemdrop_set_${itemid},${x},${y},${w},${h},${itemc}`];
    }else if(type == 'pop'){
      data = [`itemdrop_pop_${i}`];
      world.dropped.splice(i, 1);
    };
    this.player.broadcast('all_in_world', null, data, worldname);
  };
  
  check_world_name(name){
    if(name.length > 10)return"world is too long";
    if(name.length < 0)return"where do you want to go?";
    if(!/^[a-zA-Z0-9]+$/.test(name))return"incorrect name, only alphabet letters";
    return false;      
  };
  
  generate_world(width, height, tilesize){
    let cdata = this.generate_tiles(width,height);
    let tiles = cdata.split('\n');
    let tile_rects = [];
    for (let y = 0; y < tiles.length; y++) {
      let line = tiles[y];
      for (let x = 0; x < line.length; x++) {
        let tile = line[x];
        tile_rects.push([x*tilesize,y*tilesize,tilesize,tilesize, parseInt(tile)]);
      };
    };
  return tile_rects;
  };
  
  generate_tiles(w, h){
    let worldString = "";
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        if (y == h - 1) {
          worldString += "4";
        }else if (y == h/2) {
          worldString += "2";
        }else if (y > h/2) {
          if(Math.random() < 0.05){
            worldString += "3";
          }else{
          worldString += "1";
          };
        }else{        
          worldString += "0";
        };
      };    
      worldString += "\n";
    };  
    return worldString;
  };
  
};
class worldinfo {
  constructor() {
    this.width = 10;
    this.height = 10;
    this.world;
    this.dropped = [];
    this.name = "";
    this.nuked = false;
    this.peers = {};
    this.maxp_x = 0;
    this.maxp_y = 0;
    this.sp_x = 0;
    this.sp_y = 0;
    this.weather = [146,244,255]
    this.level_limit = 0;
  }
};
module.exports = World;