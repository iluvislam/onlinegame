class Player {
  constructor(network, items_map, players_map, worlds_map) {
    this.items_map = items_map;
    this.players_map = players_map;
    this.worlds_map = worlds_map;
    this.network = network;
  };

  broadcast(type, peer, data = '', worldname = ''){
    let wn;
    if(peer){
      wn = peer.c_world;
    }else{
      wn = worldname;
    };
    let theworld = this.worlds_map.get(wn);
    if(!theworld) return;
  if(type == 'msg'){
    console.log(data);
    let otherpeer = this.players_map.get(data[0]);
    if(!otherpeer) return;
    this.network.peer_send(`chatbox_<MSG from ${peer.name}> ${data[1]}`, otherpeer.address.address,otherpeer.address.port);
    return;
   }
   for (let key in theworld.peers) {
      let otherpeer = theworld.peers[key];
      if(type == 'world_enter'){
        this.network.peer_send(`chatbox_<${peer.name} entered the world>`, otherpeer.address.address,otherpeer.address.port);
        if(peer.name === otherpeer.name){
          this.network.peer_send(`wearable_0_${this.get_player_wearable(peer)}`, otherpeer.address.address, otherpeer.address.port);
        }if(Object.keys(theworld.peers).length > 1 && peer.name !== otherpeer.name){
          this.network.peer_send(`worldenter_${peer.name}|${peer.x}|${peer.y}|${peer.w}|${peer.h}|${peer.flp}|${this.get_player_wearable(peer)}`, otherpeer.address.address, otherpeer.address.port);
          this.network.peer_send(`worldplayer_${otherpeer.name}|${otherpeer.x}|${otherpeer.y}|${otherpeer.w}|${otherpeer.h}|${otherpeer.flp}|${this.get_player_wearable(otherpeer)}`, peer.address.address, peer.address.port);
        };
      }else if(type == 'move'){
        if(Object.keys(theworld.peers).length > 1 && peer.name !== otherpeer.name){
        this.network.peer_send(`move_${peer.name}|${peer.x}|${peer.y}|${peer.w}|${peer.h}|${peer.flp}|${this.get_player_wearable(peer)}`, otherpeer.address.address,otherpeer.address.port);
        };
      }else if(type == 'wearable'){
        //sound effect tho this.network.peer_send(`chatbox_<${peer.name} entered the world>`, otherpeer.address.address,otherpeer.address.port);
        if(Object.keys(theworld.peers).length > 1 && peer.name !== otherpeer.name){
          this.network.peer_send(`wearable_1_${peer.name}_${data}`, otherpeer.address.address, otherpeer.address.port);
        }else if(peer.name === otherpeer.name){
          this.network.peer_send(`wearable_0_${data}`, peer.address.address, peer.address.port);
        };
      }else if(type == 'world_exit'){
        this.network.peer_send(`chatbox_<${peer.name} left the world>`, otherpeer.address.address,otherpeer.address.port);
        if(peer.name === otherpeer.name && data){
          this.network.peer_send(`worldexit_y_${data}`, peer.address.address, peer.address.port);
        }else if(Object.keys(theworld.peers).length > 1 && peer.name !== otherpeer.name){
        this.network.peer_send(`worldexit_n_${peer.name}`, otherpeer.address.address, otherpeer.address.port);
        };
      }else if(type == 'all_in_world'){
        data.forEach((v) => {
          this.network.peer_send(v, otherpeer.address.address, otherpeer.address.port);
        });
      };
    };
  };
  
  wear_item(peer, item){
    if (peer.c_head === item.id || 
        peer.c_neck === item.id || 
        peer.c_face === item.id || 
        peer.c_body === item.id || 
        peer.c_back === item.id || 
        peer.c_hand === item.id || 
        peer.c_legs === item.id || 
        peer.c_feet === item.id) {
        return; // Item is already worn by the player
    };
    if (item.bodylocation == 1) {
      peer.c_head = item.id;
    } else if (item.bodylocation == 2) {
      peer.c_neck = item.id;
    } else if (item.bodylocation == 3) {
      peer.c_face = item.id;
    } else if (item.bodylocation == 4) {
      peer.c_body = item.id;
    } else if (item.bodylocation == 5) {
      peer.c_back = item.id;
    } else if (item.bodylocation == 6) {
      peer.c_hand = item.id;
    } else if (item.bodylocation == 7) {
      peer.c_legs = item.id;
    } else if (item.bodylocation == 8) {
      peer.c_feet = item.id;
    };
    this.broadcast('wearable', peer, item.id);
  };
  
  send_inventory(peer){
    if(Object.keys(peer.inventory).length === 0) return;
    for (let key in peer.inventory) {
      let value = peer.inventory[key];
      this.network.peer_send(`inventory_set_[${key}, ${value}]`, peer.address.address, peer.address.port);
    };
  };
  
  player_logout(name){
    let peer = this.players_map.get(name);
    let world = this.worlds_map.get(peer.c_world);
    console.log(peer);
    console.log(world);
    if(peer){
      if(world){
        this.broadcast('world_exit', peer, 'exit');
        delete this.worlds_map.get(peer.c_world).peers[peer.name];
      };
      peer.on = false;
      peer.address = {};
      peer.x = 0;
      peer.y = 0;
      peer.ping = 0;
      peer.c_world = "";
    };
  };
  
  player_login(name, pass, client){
    let peer = this.players_map.get(name);
    if(peer){
      if(peer.pass !== pass){
        this.network.peer_send(`chatbox_incorrect name or password`, client.address.address,client.address.port);
        this.network.peer_disconnect(client.address.address,client.address.port);
      }else{
        this.network.peer_send(`welcome_1`, client.address.address,client.address.port);       
        if(peer.on === true){
          this.network.peer_disconnect(peer.address.address,peer.address.port);
          this.network.peer_send(`chatbox_this account was already online, if you were playing before this is nothing to worry about.`, client.address.address,client.address.port);
        };
        peer.address = client.address;
        peer.on = true;
      };  
    }else {
      this.create_account(name, pass, client.address)
      this.network.peer_send(`welcome_1`, client.address.address,client.address.port);
    };
  };
  
  delete_account(name){
    this.players_map.delete(name);
  };
  
  create_account(name, pass, address){
    let peer = new playerinfo();
    peer.name = name;
    peer.pass = pass;
    peer.address = address;
    peer.on = true;
    this.players_map.set(name, peer);
  };
  
  get_player_wearable(peer) {
    let data = "";
    if (peer.c_head > 0) {
      let it = this.items_map.get(peer.c_head);
      data += `${peer.c_head},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_neck > 0) {
      let it = this.items_map.get(peer.c_neck);
      data += `${peer.c_neck},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_face > 0) {
      let it = this.items_map.get(peer.c_face);
      data += `${peer.c_face},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_body > 0) {
      let it = this.items_map.get(peer.c_body);
      data += `${peer.c_body},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_back > 0) {
      let it = this.items_map.get(peer.c_back);
      data += `${peer.c_back},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_hand > 0) {
      let it = this.items_map.get(peer.c_hand);
      data += `${peer.c_hand},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_legs > 0) {
      let it = this.items_map.get(peer.c_legs);
      data += `${peer.c_legs},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    if (peer.c_feet > 0) {
      let it = this.items_map.get(peer.c_feet);
      data += `${peer.c_feet},${it.offsetx1},${it.offsetx2},${it.offsety1}\n`;
    };
    return data;
  };  
  
  inventory_manager(type, peer, itemid, itemc){
    itemc = parseInt(itemc, 10);
    itemid = parseInt(itemid, 10);
    let bt = peer.inventory[itemid];
    if(type == 'push'){
      if(bt){
        peer.inventory[itemid] = itemc+bt;
      }else{
        peer.inventory[itemid] = itemc;
      };
    }else if(type == 'pop'){
      if(bt){
        if(itemc == -1 || bt - itemc <= 0){
        delete peer.inventory[itemid];
        }else{
          peer.inventory[itemid] = bt-itemc;
        };
      };
    };
    let bb = peer.inventory[itemid];
    if(bb){
      this.network.peer_send(`inventory_set_[${itemid}, ${bb}]`, peer.address.address, peer.address.port);
    }else{
      this.network.peer_send(`inventory_pop_${itemid}`, peer.address.address, peer.address.port);
    };
  };
};
class playerinfo {
  constructor() {
    this.name = "";
    this.pass = "";
    this.c_world = "";
    this.on = false;
    this.is_muted = false;
    this.is_banned = false;
    this.ban_date = null;
    this.xp = 0;
    this.c_head = 0; // 1
    this.c_neck = 0; // 2 
    this.c_face = 0; // 3
    this.c_body = 0; // 4
    this.c_back = 0; // 5
    this.c_hand = 0; // 6
    this.c_legs = 0; // 7
    this.c_feet = 0; // 8
    this.x = 0;
    this.y = 0;
    this.w = 0;
    this.h = 0;
    this.flp = 0;
    this.ping = 0;
    this.adminlvl = 0;
    this.health = 0;
    this.level = 0;
    this.strength = 0;
    this.testosterone = 0;
    this.energy = 0;
    this.weight = 0;
    this.skills = {};
    this.inventory = {};
    this.address = {};
  }
};
module.exports = Player;