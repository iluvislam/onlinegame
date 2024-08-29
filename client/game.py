class Game:
	def __init__(self, menu) -> None:
		self.menu = menu
		#player shit
		self.player_width = 12 
		self.player_height = 40
		self.playerect = None
		self.player_img = pygame.image.load('recs/player/player.png')
		self.pt = pygame.image.load('recs/blocks/female_ponytail.png')
		self.player_old_x = 0
		self.player_old_y = 0
		self.player_movment = [0,0]
		self.fall = False
		self.flip = 0
		self.move_speed = 2
		self.fall_force = 0
		self.moving_right = False
		self.moving_left = False
		self.scroll = [0,0]
		self.weather = None
		#dialogs shit
		self.isdialog = False
		self.menuon = False
		self.invon = False
		self.optionson = False
		self.dialogon = ['f', '']
		
	def core(self) -> None:
		if not self.menu.network.items[0]:
			self.menu.network.network_req('items_get')
			if self.menu.network.data_event.wait():
				self.menu.chatbox.add_message("Items updates.")
				self.menu.network.items[1] = {}
				for zz, zzz in self.menu.network.items[0].items():
					path = zzz[1]
					self.menu.network.items[1][zz] = pygame.image.load(str(path))

		if not self.menu.network.world.get('world', None):
			if self.menu.network.reqworld:
				self.menu.network.network_req('world_'+self.menu.network.reqworld)
			else:
				self.menu.network.network_req('world_start')
			if self.menu.network.world_event.wait():
				self.playerect = pygame.Rect(self.menu.network.world['sp_x'],self.menu.network.world['sp_y'],self.player_width,self.player_height)

		if not self.weather:
			self.menu.network.network_req('weather_1')
			self.menu.network.weather_event.wait()
				
		if not self.menu.dialogs.get('menu', None):
			me = {}
			me['button_1'] = "Exit", "gamemenu_exit", self.menu.option_spacer *0.2
			me['button_2'] = "Respawn", "gamemenu_respawn", self.menu.option_spacer * 2
			me['button_3'] = "Options", "gamemenu_options", self.menu.option_spacer*3
			me['button_4'] = "About", "gamemenu_about", self.menu.option_spacer*4
			me['button_5'] = "Store", "gamemenu_store", self.menu.option_spacer*5
			me['button_6'] = "Help", "gamemenu_help", self.menu.option_spacer*6
			me['button_7'] = "Back", "gamemenu_back", self.menu.option_spacer*7
			if self.menu.network.world:
				me['text_8'] = self.menu.font.render("Current World: "+ self.menu.network.world['name'], True, (255, 100, 0)), "gamemenu_worldname", self.menu.option_spacer*8
			self.menu.add_dialog('menu', [0.3, 0.5, (128, 128, 255, 128), me])

			
		if self.player_old_x != self.playerect.x or self.player_old_y != self.playerect.y:
			self.player_old_x = self.playerect.x
			self.player_old_y = self.playerect.y
			self.menu.network.network_req(f"move_{[self.playerect.x,self.playerect.y,self.playerect.w,self.playerect.h,self.flip]}")
				
		
		if 220 < self.playerect.x <= self.menu.network.world['max_x'] - display.get_width() + 220:
			self.scroll[0] += self.playerect.x - self.scroll[0] - 220
		if 100 < self.playerect.y <= self.menu.network.world['max_y'] - display.get_height() + 100:
			self.scroll[1] += self.playerect.y - self.scroll[1] - 100
		
		self.player_movment = [0, 0]	
		
		#physics
		if not self.menu.chatbox.istyping:
			if pygame.K_d in self.menu.ksc[0]:
				self.player_movment[0] += self.move_speed
				self.flip = 0
			if pygame.K_a in self.menu.ksc[0]:
				self.player_movment[0] -= self.move_speed
				self.flip = 1
			if pygame.K_w in self.menu.ksc[0] and not self.fall:
				self.fall_force = -4
				self.fall = True #true
			
		self.player_movment[1] += self.fall_force
		self.fall_force += 0.2
		if self.fall_force > 3:	self.fall_force = 3	
					
	def colliderect(self) -> None:
		self.playerect.x += self.player_movment[0]
		if self.menu.network.world.get('world', None):
			for tilex in self.menu.network.world['world']:
				if self.playerect.left < 0:
					self.playerect.left = 0
				elif self.playerect.right > self.menu.network.world['max_x']:
					self.playerect.right = self.menu.network.world['max_x']
				if tilex[1] > 0:
					if self.playerect.colliderect(tilex[0]):
						if self.player_movment[0] > 0:
							self.playerect.right = tilex[0].left
						elif self.player_movment[0] < 0:
							self.playerect.left = tilex[0].right
			self.playerect.y += self.player_movment[1]
			for tilex in self.menu.network.world['world']:
				if self.playerect.top < 0:
					self.playerect.top = 0
					#self.fall_force = 0
					self.fall = True
				elif self.playerect.bottom > self.menu.network.world['max_y']:  # Assuming world_height is the height of your game world
					self.playerect.bottom = self.menu.network.world['max_y']
					self.fall_force = 0
					self.fall = False				
				if tilex[1] > 0:
					if self.playerect.colliderect(tilex[0]):	
						if self.player_movment[1] > 0:
							self.playerect.bottom = tilex[0].top
							self.fall_force = 0
							self.fall = False
						elif self.player_movment[1] < 0:
							self.playerect.top = tilex[0].bottom
				
	def dialogs(self, scl) -> None:
		self.isdialog = True
		if self.menuon:
			self.menu.dialog_blit('menu', scl)
		elif self.invon:
			pass
		elif self.dialogon[0] == 't':
			self.menu.dialog_blit(self.dialogon[1], scl)
		elif self.menu.about:
			self.menu.about_blit(scl)
		elif self.menu.settings:
			self.menu.settings_blit(scl)
		elif self.menu.settings_vids:
			self.menu.settings_vid_blit(scl)
		elif self.menu.settings_keyboard:
			self.menu.keyboard_blit(scl)
		elif self.menu.settings_graphics:
			self.menu.graphics_blit(scl)
		else:
			self.isdialog = False
			self.menu.inventory.inventory_blit(scl, self.menu.mouse_rect)
			self.menu.chatbox.chatbox_blit(scl)		
			
	def map_blit(self, s) -> None:	
		itemd = self.menu.network.items[1]
		for tile in self.menu.network.world['world']:
			#pygame.draw.rect(s, (0,0,0), (tile[0].x-self.scroll[0], tile[0].y-self.scroll[1], 18, 18))
			obj = itemd.get(str(tile[1]), None)
			if obj is not None:
				s.blit(obj, (tile[0][0]-self.scroll[0],tile[0][1]-self.scroll[1]))			

	def effects_blit(self, scl) -> None:
		try:
			if self.menu.network.effects.items():
				for key, data in self.menu.network.effects.items():
					itemd = self.menu.network.items[1].get(str(key), None)
					x, y, w, h = data 
					effect_pos = self.scl_scale_up(int(x), int(y), int(w), int(h))
					scl.blit(itemd, effect_pos)
		except:
			pass	
		
	def world_playersn_blit(self, scl) -> None:
		try:
			if self.menu.network.world_players.items():
				for play, data in self.menu.network.world_players.items():
					x, y, w, h, f = data 
					player_positionp = (int(x), int(y))
					textp = self.menu.font.render(play, True, (255, 255, 255))
					scaled_text_position = ((player_positionp[0] * self.menu.display_rect.w) / display.get_width() - textp.get_width()/2,
                        (player_positionp[1] * self.menu.display_rect.h) / display.get_height() - 40)					
					self.playern_blit(scl, str(play), int(x)- self.scroll[0], int(y)- self.scroll[1])
		except:
			pass		

		
	def self_wearable_blit(self, dis) -> None:	
		try:
			if self.menu.network.wearable.items():
				for itid, data in self.menu.network.wearable.items():
					x1, x2, y1 = data
					itemd = self.menu.network.items[1].get(str(itid), None)
					offset = int(x1)
					if self.flip:
						offset = int(x2)
					dis.blit(pygame.transform.flip(itemd,self.flip,False),(self.playerect.x-offset-self.scroll[0],self.playerect.y-int(y1)-self.scroll[1]))
		except:
			pass
		
	def world_players_blit(self) -> None:	
		try:
			if self.menu.network.world_players.items():
				for play, data in self.menu.network.world_players.items():
					x, y, w, h, f, lista = data
					cl = pygame.Rect(int(x),int(y),int(w),int(h))
					display.blit(pygame.transform.flip(self.player_img,int(f),False),(cl.x-self.scroll[0],cl.y-self.scroll[1]))
					for item in lista.split('\n'):
						itid, x1, x2, y1 = item.split(',')
						itemd = self.menu.network.items[1].get(str(itid), None)
						offset = int(x1)
						if int(f):
							offset = int(x2)	
						display.blit(pygame.transform.flip(itemd,int(f),False),(cl.x-offset-self.scroll[0],cl.y-int(y1)-self.scroll[1]))
		except:
			pass
				
	def playern_blit(self, dis, text, x, y) -> None:
		player_position = (x, y)
		text = self.menu.font.render(text, True, (255, 255, 255))
		scaled_text_position = self.scl_scale_up(player_position[0], player_position[1], text.get_width(), 100)
		dis.blit(text, scaled_text_position)
				
	def scl_scale_up(self, x,y,w,h):
		return ((x * self.menu.display_rect.w) / display.get_width() - w/2,
						(y * self.menu.display_rect.h) / display.get_height() - h/2)
		
	def particle_blit(self, dis):
		for particle in self.menu.network.particles:
			particle[0][0] += particle[1][0]
			particle[0][1] += particle[1][1]
			particle[2] -= 0.5
			particle[1][1] += 0.1
			scl = self.scl_scale_up(int(particle[0][0]) - self.scroll[0], int(particle[0][1]) - self.scroll[1], 1, 1)
			pygame.draw.circle(dis, particle[3], [scl[0], scl[1]], int(particle[2]))
			if particle[2] <= 0:
				self.menu.network.particles.remove(particle)	
				
	def dropped_blit(self, dis):
		try:
			dol = self.menu.network.items[1].get('-2', None)
			if self.menu.network.dropped_items:
				for index, item in enumerate(self.menu.network.dropped_items):
					itid, x, y, w, h, count = item 
					obj = self.menu.network.items[1].get(itid, None)
					t_x = int(x) - self.scroll[0]
					t_y = int(y) - self.scroll[1] + 1 * math.sin(pygame.time.get_ticks() * 0.007)
					t_w = int(w)
					t_h = int(h)
					scl = self.scl_scale_up(t_x, t_y, t_w, t_h)
					if obj is None:
						self.menu.network.dropped_items.pop(index)
					else:
						dis.blit(dol, scl)
						dis.blit(obj, (scl[0]+5, scl[1]+5, t_w+10, t_h+10))
						if int(count) > 1:
							text = self.menu.font.render(str(count), True, (255, 255, 255))
							display.blit(text, (scl[0]+5, scl[1]+5, t_w, t_h))	
							
		except Exception as e:
			print(e)
		
	def display(self) -> None:
		#weather
		if self.weather:
			display.fill(self.weather)
			
		#map
		self.map_blit(display)
		
		#effects
		self.effects_blit(display)	
		
		#other players
		self.world_players_blit()
		
		#player
		display.blit(pygame.transform.flip(self.player_img,self.flip,False),(self.playerect.x-self.scroll[0],self.playerect.y-self.scroll[1]))
		#display.blit(pygame.transform.flip(self.pt,self.flip,False),(self.playerect.x -4-self.scroll[0],(self.playerect.y - 8)-self.scroll[1]))
		
		#wearable
		self.self_wearable_blit(display)
		
		#scale
		scl = pygame.transform.scale(display, (self.menu.display_rect.w, self.menu.display_rect.h))	
		
		#particles
		self.particle_blit(scl)
		
		#dropped items
		self.dropped_blit(scl)
		
		#player name
		self.playern_blit(scl, self.menu.network.playername, self.playerect.centerx - self.scroll[0], self.playerect.y - self.scroll[1])	
		
		#other players
		self.world_playersn_blit(scl)
		
		#dialogs
		self.dialogs(scl)
		
		screen.blit(scl, (0, 0))
		
	def loop(self) -> None:
		self.core()
		self.colliderect()
		self.display()