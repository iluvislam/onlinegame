let fs = require('fs');
let Network = require('./network.js');
let Events = require('./events.js');

let players_map = new Map();
let worlds_map = new Map();

let network = new Network();
network.init(6003);

let events = new Events(network, players_map, worlds_map);
events.chatbox.init_commands();
events.load_server();
events.init_items();

network.message_handler((data, client) => {

  console.log(data);
  
  if(data[0] == 'info'){
    let d = data[1].split('_');
    let name = d[0];
    let pass = d[1];
    events.info_handler(client, name, pass);
  }else if (data[0] === 'saveserver') {
    events.save_server();
  }else if (data[0] === 'status') {
    let dataToSend = {
      players_map: Array.from(players_map.entries()).map(([playerkey, playerv]) => ({
        name: playerkey,
        world: playerv,
        playerinv: Array.from(playerv.inventory),
      })),   
      clients_map: Array.from(network.clients_map.entries()),
      worlds_map: Array.from(worlds_map.entries()).map(([worldKey, worldValue]) => ({
        name: worldValue.name,
        world: worldValue,
        peers: Array.from(worldValue.peers),
      })),
        pps: network.status['pps'],
        dps: network.status['dps'],
  };  
    network.peer_send(JSON.stringify(dataToSend), client.address.address, client.address.port);
  };
  let peer = players_map.get(client.name); 
  if(!peer || !peer.name || !peer.address || !peer.on || peer.address !== client.address) return;
  
  if(data[0] == 'items'){
    events.items_handler(peer); 
  }else if(data[0] == 'world'){
	  events.world.world_enter(data[1], peer);
  }else if(data[0] == 'move'){
    events.movement_handler(data[1], peer);
  }else if(data[0] == 'weather'){
    events.weather_handler(peer);
  }else if(data[0] == 'store'){
    events.store_handler(peer);
  }else if(data[0] == 'chatbox'){
    events.chatbox.handler(data[1], peer);
  }else if(data[0] == 'worlde'){
    events.world.world_edit(data[1], peer);
  };
  
});

network.disconnect_handler((data) => {
  console.log(data);
  if(data.client){
    network.pop_client(data.ip, data.port);
    if(data.client.name){
      let bt = players_map.get(data.client.name);
      if(bt && bt.on === true && data.ip === bt.address.address && data.port === bt.address.port){ 
        events.player.player_logout(data.client.name);
      };
    };
  };
});