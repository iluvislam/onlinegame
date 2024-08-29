let fs = require('fs');
let World = require('./world.js');
let Player = require('./player.js');
let Chatbox = require('./chatbox.js');

class Events {
  constructor(network, players_map, worlds_map) {
    this.network = network;
    this.players_map = players_map;
    this.worlds_map = worlds_map;
    this.items_map = new Map();
    this.player = new Player(network, this.items_map, this.players_map, this.worlds_map);
    this.world = new World(network, this.worlds_map, this.items_map, this.player);
    this.chatbox = new Chatbox(network, this.world, this.player);
  };

  store_handler(peer){
    let store = [0.3, 0.5, {'button_1': ['go2', 'dialog_lol', 11.059200000000002] }]
    let dd = `dialog_storedialog_${JSON.stringify(store)}`;
    this.network.peer_send(dd, peer.address.address,peer.address.port);
  };
  
  weather_handler(peer){
    let wname = peer.c_world;
    let wt = this.world.get_weather(wname);
    this.network.peer_send(`weather_${wt[0]}_${wt[1]}_${wt[2]}`, peer.address.address,peer.address.port);
    this.player.send_inventory(peer);
  };
  
  movement_handler(data, peer){
    let obj = JSON.parse(data);
	  peer.x = obj[0];
	  peer.y = obj[1];
	  peer.w = obj[2];
	  peer.h = obj[3];
	  peer.flp = obj[4];
    this.player.broadcast('move', peer);
    this.world.dropped_colli(peer);
  };
  
  items_handler(peer) {
    let base = 'items_';
    let items = fs.readFileSync('items').toString().split('\n'); // Splitting the file content by lines
    items = items.filter(line => !line.startsWith('#')); // Filtering out lines starting with "/"
    items = items.join('\n'); 
    this.network.peer_send(`${base}${items}`, peer.address.address, peer.address.port);
  };
  
  info_handler(client, name, pass){
    let infoname = name.toLowerCase();
    let infopass = pass.toLowerCase();
    client.name = infoname;
    this.player.player_login(infoname,infopass,client);
  };
  
  init_items(){
    let itemdata = fs.readFileSync('items').toString();
    if(itemdata){
      let isplit = itemdata.split('\n');
      isplit.forEach((key) => {
        if (key.charAt(0) === '#') return;
        //value = [id,name,path,rarity,type,w,h,offsetx1,offsetx2,offsety1]
        let value = key.split('|');
        let ipeer = new iteminfo();
        ipeer.id = parseInt(value[0]);
        ipeer.name = value[1];
        ipeer.path = value[2];
        ipeer.rar = parseInt(value[3]);
        ipeer.type = parseInt(value[4]);
        ipeer.width = parseInt(value[5]);
        ipeer.height = parseInt(value[6]);
        ipeer.offsetx1 = parseInt(value[7]);
        ipeer.offsetx2 = parseInt(value[8]);
        ipeer.offsety1 = parseInt(value[9]);
        ipeer.bodylocation = parseInt(value[10]);
        this.items_map.set(ipeer.id, ipeer);
      });
    };
    return this.items_map;
  };
  
  load_server(){
    try {
      if (fs.existsSync('players_map.json')) {
        let fileData = fs.readFileSync(fileName).toString();
        if (!fileData) {
          return false;
        };
        this.players_map =  new Map(JSON.parse(fileData));
      };
      if (fs.existsSync('worlds_map.json')) {
        let fileData = fs.readFileSync(fileName).toString();
        if (!fileData) {
          return false;
        };
        this.worlds_map =  new Map(JSON.parse(fileData));
      };      
    } catch (e) {
      console.log(e);
      return false;
    };    
  };
  
  save_server(){
    let pmap = new Map(this.players_map);
    for (const [key, p] of pmap) {
      p.on = false;
      p.address = {};
      p.c_world = '';
      p.x = 0;
      p.y = 0;
      p.w = 0;
      p.h = 0;
      p.flp = 0;
    };
    let player_data = JSON.stringify(pmap, (key, value) => {
      if (Array.isArray(value) || value instanceof Map) {
        return [...value];
      };
      return value;
    });
    pmap.clear();
    pmap = null;
    let world_data = JSON.stringify(this.worlds_map, (key, value) => {
      if (Array.isArray(value) || value instanceof Map) {
        return [...value];
      };
      return value;
    });    
    fs.writeFileSync('players_map.json', player_data, (err) => {console.log(err);});
    fs.writeFileSync('worlds_map.json', world_data, (err) => {console.log(err);});
  };
};

class iteminfo {
  constructor() {
    this.name = "";
    this.path = "";
    this.width = 0;
    this.height = 0;
    this.type = 0;
    this.offsetx1 = 0;
    this.offsetx2 = 0;
    this.offsety1 = 0;
    this.rar = 0;
    this.bodylocation = 0;
    this.id;
  }
};

module.exports = Events;