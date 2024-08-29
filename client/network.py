import socket, zlib
import threading, random, json, struct, time, pygame

class Networking:

	def __init__(self, menu) -> None:
		self.menu = menu
		self.buff = 2*1024
		self.is_networking_active = False
		#Main shit
		self.wait_chunk = threading.Event()  
		self.connect_event = threading.Event()  
		self.welcome_event = threading.Event()  
		self.data_event = threading.Event()  
		self.world_event = threading.Event()  
		self.weather_event = threading.Event()
		self.world = {} 
		self.items = [{}, {}] 
		self.world_players = {}
		self.dropped_items = []
		self.server_address = ()
		self.pending_data = None
		self.playername = ""
		self.reqworld = ""
		self.particles = []
		self.wearable = {}
		self.stl = threading.Thread(target=self.start_loginlisten)
		self.stl.daemon = True
		self.stl.start()
		self._s = None
    
	def get_data(self, data) -> None:
		return json.loads(data)
	
	def send_ack(self) -> None:
		try:
			self.network_req('ACK_DWT') # ACK
			data,info = self._s.recvfrom(self.buff)
			d = self.get_data(self.data_decompress(data))['data']
			d_split = str(d).split('_')
			if d_split[1] == "ok":
				return "ok"
		except Exception as e:
			self._s.close()
			return str(e)

			
	def data_decompress(self, thing) -> None:
		decompressed_data = zlib.decompress(thing)
		return struct.unpack('!{}s'.format(len(decompressed_data)), decompressed_data)[0].decode('utf-8')
	
	def data_compress(self, thing) -> None:
		return zlib.compress(struct.pack('!{}s'.format(len(thing)), thing.encode('utf-8')), level=zlib.Z_BEST_COMPRESSION)

	def network_req(self, thing) -> None:
		self._s.sendto(self.data_compress(thing), self.server_address)
			
	def end_network(self) -> None:
		try:
			self.is_networking_active = False

    # Close the socket
			if self._s:
				self._s.close()

    # Reset data structures
			self.world = {}
			self.items = [{}, {}]
			self.world_players = {}
			self.dropped_items = []
      
		except:
			print('oh no')
		
	def start_loginlisten(self) -> None:
		while True:
			self.connect_event.wait()
			self.menu.chatbox.add_message("Logging in")
			try:
				ip, port, username, pw = self.menu.dst.split(':')[0], int(self.menu.dst.split(':')[1]), self.menu.username, self.menu.pw
				self.server_address = (ip, port)
				self._s = socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
				self._s.settimeout(3)
				self._s.connect(self.server_address)
				ac = self.send_ack()
				if str(ac) != "ok":
					self.menu.chatbox.add_message(str(ac))
				else:
					self.is_networking_active = True
					self.network_init()
					time.sleep(1)
					self.network_req(f"info_{username}_{pw}")
					
			except Exception as e:
				self.menu.chatbox.add_message(str(e))
			self.connect_event.clear()
																			
	def start_networklisten(self) -> None:
		while self.is_networking_active:
			if not self.is_networking_active:
					break
			try:
				data,info = self._s.recvfrom(self.buff)
				dg = json.loads(self.data_decompress(data))
				print(dg)
				dtype = dg['type']
				d = dg['data']
				
				d_split = [""]
				if dtype == 1:
					d_split = str(d).split('_')
				elif dtype == 2:
					self.pending_data = d
				elif dtype == 3:
					self.pending_data += d
				elif dtype == 4:
					self.pending_data += d
					d = self.pending_data
					d_split = str(d).split('_')

				if d_split[0] == "proxy":
					self.network_req(str(d).split('_', 1)[1])
				if d_split[0] == "ppset":
					l = json.loads(d_split[1])
					self.menu.game.playerect.x = l[0]
					self.menu.game.playerect.y = l[1]
				if d_split[0] == "wearable":
					typee = int(d_split[1])
					if(typee == 0):
						l = str(d_split[2])
						if len(l.split('\n')) > 1:
							for item in l.split('\n'):
								itid, x1, x2, y1 = item.split(',')
								itemd = self.items[0].get(str(itid))
								if itemd:
									self.wearable[itid] = [itemd[6], itemd[7], itemd[8]]
						else:
							itemd = self.items[0].get(str(l))
							if itemd:
								self.wearable[l] = [itemd[6], itemd[7], itemd[8]]
					else:
						pname = str(d_split[2])
						pdata = self.world_players.get(pname)
						if pdata:
							l = str(d_split[3])
							itemd = self.items[0].get(l)
							self.world_players[pname] = (self.world_players[pname][0], self.world_players[pname][1], self.world_players[pname][2], self.world_players[pname][3], self.world_players[pname][4], (self.world_players[pname][5] or '') + f'{l},{itemd[6]},{itemd[7]},{itemd[8]}\n')
					#type,id
				if d_split[0] == "weather":
					self.weather_event.set()
					self.menu.game.weather = (int(d_split[1]), int(d_split[2]), int(d_split[3]))
				if d_split[0] == "particle":
					l = json.loads(d_split[1])
					for i in range(int(l[2])):
						self.particles.append([[int(l[0]), int(l[1])], [random.randint(0, 20) / 10 - 1, 0], random.randint(4, int(l[3])), (l[4][0],l[4][1],l[4][2])])
				if d_split[0] == "chatbox":
					dtext = str(d).split('_', 1)
					self.menu.chatbox.add_message(dtext[1])
				if d_split[0] == "dialog":
					dialogd = str(d).split('_', 2)
					self.menu.add_dialog(dialogd[1], json.loads(dialogd[2]))	
					self.menu.game.dialogon = ['t', dialogd[1]]
				if d_split[0] == "welcome":
					self.menu.chatbox.add_message('Connected to the server.')
					self.welcome_event.set()
				if d_split[0] == "disconnect":
					self.menu.chatbox.add_message('disconnected')
					self.menu.terminate_game()
				if d_split[0] == "items":
					l = str(d).split('_', 1)[1].split('\n')
					for i in l:
						f = i.split('|')
						for item in f:
							self.items[0][str(f[0])] = f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10]
							#id,name,path,rar,type,w,h,x1,x2,y1,il
					self.data_event.set()
				if d_split[0] == "worldenter" or d_split[0] == "worldplayer":
					f = d_split[1].split('|')
					self.world_players[f[0]] = f[1], f[2], f[3], f[4], f[5], f[6]
					#name,x,y,w,h,flp,[]
				if d_split[0] == "itemdrop":
						if d_split[1] == 'set':
							f = d_split[2].split('|')
							if len(f) > 1:
								for index, item in enumerate(f): # id,x,y,w,h,c
									i = item.split(',')
									self.dropped_items.append([i[0], i[1], i[2], i[3], i[4], i[5]])
							else:
								i = f[0].split(',')
								self.dropped_items.append([i[0], i[1], i[2], i[3], i[4], i[5]])
						if d_split[1] == 'pop':
							f = int(d_split[2])
							self.dropped_items.pop(f)
				if d_split[0] == "worldexit":
					if d_split[1] == 'y':
						self.world.clear()
						self.menu.game.weather = None
						self.menu.dialogs.pop('menu', None)
						self.reqworld = d_split[2]
						self.world_players.clear()
						self.world_event.clear()
						self.weather_event.clear()
						self.dropped_items.clear()
					elif d_split[1] == 'n':
						if d_split[2] in self.world_players:
							self.world_players.pop(d_split[2])
				if d_split[0] == "inventory":
					if d_split[1] == 'pop':
						f = int(d_split[2])
						self.menu.inventory.remove(f)
					if d_split[1] == 'set':
						l = json.loads(d_split[2])
						it = self.items[1].get(str(l[0]))
						itn = self.items[0].get(str(l[0]))[0]
						self.menu.inventory.set(l[0],l[1],it, itn)
				if d_split[0] == "move":
					f = d_split[1].split('|')
					if f[0] in self.world_players:
						self.world_players[f[0]] = f[1], f[2], f[3], f[4], f[5], f[6]
				if d_split[0] == "worlde":
					if d_split[1] == 'set':
						l = json.loads(d_split[2])
						rect = [pygame.Rect(int(l[0]), int(l[1]), int(l[2]), int(l[3])), int(l[4])]
						self.world['world'][int(d_split[3])] = rect
				if d_split[0] == "world":
					l = []
					for coord in json.loads(d_split[1]):
						rect = pygame.Rect(int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3]))  # Replace width and height with actual values
						l.append([rect, int(coord[4])])
					self.world['world'] = l
					self.world['name'] = d_split[2]
					self.world['max_x'] = int(d_split[3])
					self.world['max_y'] = int(d_split[4])
					self.world['sp_x'] = int(d_split[6])
					self.world['sp_y'] = int(d_split[7])
					self.playername = str(d_split[5])
					self.world_event.set()
			except Exception as e:
				print(e)
		
		
	def start_networkack(self) -> None:
		while self.is_networking_active:
			time.sleep(5)
			if not self.is_networking_active:
				break
			self.network_req('check_1')


	def network_init(self) -> None:
		
		thread_ack = threading.Thread(target=self.start_networkack)
		thread_ack.daemon = True
		thread_ack.start()
		
		listen = threading.Thread(target=self.start_networklisten)
		listen.daemon = True
		listen.start()