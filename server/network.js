const dgram = require('dgram');
const zlib = require('zlib');

class Network {
  constructor() {
    this.server = null;
    this.dcallback = null;
    this.status = {};
    this.clients_map = new Map();
  };
  
  init(port){
    this.server = dgram.createSocket('udp4');
    this.server.bind(port);
    this.status['pps'] = 0;
    this.status['dps'] = 0;
    console.log(`udp server running on port ${port}`);
  };
  
  decompress_udp_data(data){
    return zlib.inflateSync(data).toString('utf-8');
  };
  
  compress_udp_data(data){
    return zlib.deflateSync(data.toString());
  };
  
  security_check(str){
    if(!str.toString()) return false;
    return true;    
  };
  
  message_handler(handler) {
    this.server.on('message', (udp_data, rinfo) => {
      this.status['pps'] += 1;
      this.status['dps'] += udp_data.length;
            
      let message = this.decompress_udp_data(udp_data);

      if(!this.security_check(message)) return;
      let client = this.clients_map.get(`${rinfo.address}:${rinfo.port}`);
      let data = [message.substring(0, message.indexOf('_')), message.substring(message.indexOf('_') + 1)]
      
      if(data[0] == 'ACK'){
        if (!client) {
          client = new clientinfo();
          client.in = true
          client.address = rinfo;
          this.clients_map.set(`${rinfo.address}:${rinfo.port}`, client);
          this.peer_send(`ACK_ok`, client.address.address,client.address.port);
        };
        return;
      };

      if(!client || !client.in || !client.address) return;
      
      client.lastack = Date.now(); 
      this.ack_handler(client.address.address, client.address.port, client);
      handler(data, client);
    });
  };
  
  pop_client(ip, port){
    if(this.clients_map.get(`${ip}:${port}`)) {
      this.clients_map.delete(`${ip}:${port}`);
    };
  };
  
  disconnect_handler(callback){
    this.dcallback = callback;
  };
  
  peer_disconnect(ip,port){
    let client = null;
    let cl = this.clients_map.get(`${ip}:${port}`);
    if(cl) {
      client = cl;
    };
    if (typeof this.dcallback === 'function') {
      this.dcallback({ ip, port, client });
    };
  };
  
  ack_handler(ip, port, client){
    setTimeout(() => {
    if(Date.now() - client.lastack > 8000){
      this.peer_disconnect(ip,port);
      }
    }, 9000);
  };
  
  peer_send(str, ip, port) {
    if (this.clients_map.get(`${ip}:${port}`)) {
      if (str.length > 2000) {
        const chunks = [];
          for (let i = 0; i < str.length; i += 2000) {
            chunks.push(str.slice(i, i + 2000));
          };
        this.send_chunk(ip, port, chunks[0], 2);
        if (chunks.length === 2) {
          this.send_chunk(ip, port, chunks[1], 4);
        } else {
          // Send all chunks except the first and last one with type 3
          for (let i = 1; i < chunks.length - 1; i++) {
            this.send_chunk(ip, port, chunks[i], 3);
          }
          // Send the last chunk with type 4
          this.send_chunk(ip, port, chunks[chunks.length - 1], 4);
        };
      }else {
        // Send the entire data as type 1
        this.send_chunk(ip, port, str, 1);
      };
    };
  };

  send_chunk(ip, port, data, type) {
    const dataToSend = {
        type: type,
        data: data
    };
    this.server.send(this.compress_udp_data(JSON.stringify(dataToSend)), port, ip, (err) => {});
  };
  
};

class clientinfo {
  constructor() {
    this.name = "";
	  this.in = false;
    this.address = {};
    this.lastack;
  }
};
module.exports = Network;