class Chatbox {
  constructor(network, world, player) {
    this.network = network;
    this.world = world;
    this.player = player;
    this.commands = {}
  };
  
  handler(text, peer){
    text = this.math_solve(text);
    if (text.charAt(0) === '/') {
      let t = text.slice(1);
      let cmd = t.split(' ')[0];
      this.network.peer_send(`chatbox_${text}`, peer.address.address,peer.address.port);
      if(typeof this.commands[cmd] == 'function'){
        this.commands[cmd](t, peer);
      };
    }else{
      this.player.broadcast('all_in_world', peer, ["chatbox_"+`<${peer.name}> ${text}`]);
    };
  };
  
  math_solve(text) {
    const regex = /{math\((.*?)\)}/g;
    let match;
    while ((match = regex.exec(text)) !== null) {
      const equation = match[1];
        try {
          const result = eval(equation);
          text = text.replace(match[0], result);
        } catch (error) {
            
        };
    };
    return text;
  };
  
  init_commands(){
    this.commands['help'] = (text, peer) => {
      this.network.peer_send(`chatbox_available commands: ${Object.keys(this.commands)}`, peer.address.address,peer.address.port);
    };

    this.commands['msg'] = (text, peer) => {
      let args = text.split(' ');
      if(!args[0] || !args[1] || !args[2]){
        this.network.peer_send("chatbox_usage of msg: /msg hasan hello babygrill", peer.address.address,peer.address.port);
      }else{
        this.player.broadcast('msg', peer, [args[1], text.slice(4)]);
      };
    };
    
    this.commands['tp'] = (text, peer) => {
      let args = text.split(' ');
      if(!args[0] || !args[1] || !args[2]){
        this.network.peer_send("chatbox_usage of tp: /tp x y", peer.address.address,peer.address.port);
      }else{
        this.network.peer_send(`ppset_[${args[1]},${args[2]}]`, peer.address.address,peer.address.port);
      };
    };
    
    this.commands['get'] = (text, peer) => {
      let args = text.split(' ');
      if(!args[0] || !args[1] || !args[2]){
        this.network.peer_send("chatbox_usage of get: /get 1 200", peer.address.address,peer.address.port);
      }else{
        this.player.inventory_manager('push', peer, args[1], args[2]);
      };
    };
    
    this.commands['weather'] = (text, peer) => {
      let args = text.split(' ')[1];
      let cmd_s = args.split(',');
      if(!cmd_s[0] || !cmd_s[1] || !cmd_s[2]){
        this.network.peer_send("chatbox_usage of weather: /weather 255,0,0", peer.address.address,peer.address.port);
      }else{
        this.world.change_weather(peer.c_world, [cmd_s[0], cmd_s[1], cmd_s[2]]);
      };   
    };
    
    this.commands['wrap'] = (text, peer) => {
      let cmd_s = text.split(' ');
      if(!cmd_s[1]){
        this.network.peer_send("chatbox_usage of wrap: /wrap start", peer.address.address,peer.address.port);
      }else{
        this.world.world_enter(cmd_s[1], peer);
      };  
    };
    
    this.commands['wgen'] = (text, peer) => {
      let cmd_s = text.split(' ');
      if(!cmd_s){
        this.network.peer_send("chatbox_usage of wgen: /wgen dadd 50 50", peer.address.address,peer.address.port);
      }else{
        this.world.world_gen(cmd_s[1], cmd_s[2], cmd_s[3]);
        this.network.peer_send("chatbox_ok", peer.address.address,peer.address.port);
      };  
    };    

    this.commands['proxy'] = (text, peer) => {
      let cmd_s = text.split(' ');
      if(!cmd_s){
        this.network.peer_send("chatbox_just type /save you fucking retarded", peer.address.address,peer.address.port);
      }else{
        this.network.peer_send("proxy_"+cmd_s[1], peer.address.address,peer.address.port);
      };  
    };  
    
  this.commands['spawn'] = (text, peer) => {
    let cmd_s = text.split(' ');
    if (!cmd_s || cmd_s.length < 2) {
        this.network.peer_send("chatbox_usage of nsend: /spawn 1", peer.address.address, peer.address.port);
    } else {
        // Define the number of items to spawn and the distance from the player
        const numItems = parseInt(cmd_s[2]) // Number of items to spawn
        const distance = 50; // Distance from the player
        
        // Calculate the angle between each item
        const angleIncrement = (2 * Math.PI) / numItems;

        // Spawn items around the player in a cube shape
        for (let i = 0; i < numItems; i++) {
            // Calculate the angle for this item
            const angle = i * angleIncrement;

            // Calculate the position relative to the player
            const xOffset = distance * Math.cos(angle);
            const yOffset = distance * Math.sin(angle);

            // Spawn the item at the calculated position
            this.world.drop_manager('push', peer.c_world, 0, parseInt(cmd_s[1]), 1, peer.x + xOffset, peer.y + yOffset);
        };
    };
  };
    
    this.commands['nsend'] = (text, peer) => {
      let cmd_s = text.split(' ');
      if(!cmd_s){
        this.network.peer_send("chatbox_usage of nsend: /nsend itemdrop_id|x|y|w|h|", peer.address.address,peer.address.port);
      }else{
        this.network.peer_send(cmd_s[1], peer.address.address,peer.address.port);
      };  
    };      
  };
};
module.exports = Chatbox;