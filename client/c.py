import pygame, sys, math

from network import Networking
from inventory import Inventory
from chatbox import Chatbox
from animation import Animation

pygame.init()
pygame.scrap.init()
pygame.scrap.set_mode(pygame.SCRAP_CLIPBOARD)

clock = pygame.time.Clock()
screen_info = pygame.display.Info()
screen_w = screen_info.current_w
screen_h = screen_info.current_h


fwindow = (screen_w,screen_h)
window = (1280,720)
screen = pygame.display.set_mode(window, 0)
display = pygame.Surface((screen_w/3.6,screen_h/3.6))	

class Menu:
	def __init__(self) -> None:
		self.chatbox: Chatbox = Chatbox()
		self.inventory: Inventory = Inventory()
		self.game: Game = Game(self)
		self.network: Networking = Networking(self)
		self.back = []
		self.main = True
		self.login = False
		self.about = False
		self.settings = False
		self.settings_vids = False
		self.settings_keyboard = False
		self.settings_graphics = False
		
		self.username = ""
		self.pw = ""
		self.dst = ""
		self.ksc = [[], []]
		
		self.display_rect = screen.get_rect()
		self.game_display = display
		self.back_ground = pygame.transform.scale(pygame.image.load("recs/menu/Background.png"), (screen_w, screen_h))
		self.font = pygame.font.Font("./recs/menu/gothicb.ttf", int(0.00003*screen.get_rect().w * screen.get_rect().h))
		self.buttons = {}
		self.black_color = (0, 0, 0)
		self.options_w = self.display_rect.w*0.2
		self.options_h = 0.06*self.display_rect.h
		self.options_x = self.display_rect.w / 15
		self.options_y = self.display_rect.h / 15
		self.option_spacer = 0.00006 * self.display_rect.w * self.display_rect.h
		self.edit = {}
		self.itsmenu = True
		self.itsgame = False
		self.dialogs = {}
		self.mouse_rect = None
		self.fpss = False
		
	def events(self) -> None:
		for event in pygame.event.get():
			self.pygame_events(event)
					
	def pygame_events(self, event) -> None:
		#quit game
		if event.type == pygame.QUIT:
			sys.exit()
			
		#key down
		elif event.type == pygame.KEYDOWN:	
			
			#add the key stroke
			self.ksc[0].append(event.key)
			
			#the esc click			
			if event.key == pygame.K_ESCAPE:
				if self.chatbox.istyping:
					self.chatbox.istyping = False
					self.chatbox.input_text = ""
				elif not self.back:
					sys.exit()
				elif self.back:
					if self.itsgame and len(self.back) > 1 or self.itsmenu:
						self.change_screen('back')
				if len(self.back) == 1 and self.itsgame:	
					self.game.menuon = not self.game.menuon
					self.game.dialogon = ['f', '']
					
			#the enter click
			elif event.key == pygame.K_RETURN:
				if not self.back and not self.itsgame:
					self.back.append('main')
					self.change_screen('login')			
				elif self.itsgame:
					self.chatbox.istyping = not self.chatbox.istyping
					if self.chatbox.input_text:
						self.network.network_req('chatbox_'+self.chatbox.input_text)
						self.chatbox.input_text = ""
					
			elif event.key == pygame.K_SLASH and self.itsgame and not self.chatbox.istyping:
				self.chatbox.istyping = True
				self.chatbox.input_text += "/"

			elif event.mod & pygame.KMOD_CTRL:
				if event.key == pygame.K_v:
					if not self.chatbox.istyping:
						self.chatbox.istyping = True
					self.chatbox.input_text += pygame.scrap.get("text/plain;charset=utf-8").decode()
					
			#the back space click
			elif event.key == pygame.K_BACKSPACE:
				if self.chatbox.istyping:
					if self.chatbox.input_text:
						self.chatbox.input_text = self.chatbox.input_text[:-1]
			elif event.key == pygame.K_TAB:
				self.game.invon = not self.game.invon
			else:
				if self.chatbox.istyping:
					self.chatbox.input_text += event.unicode
	
		elif event.type == pygame.KEYUP:
			if event.key in self.ksc[0]:
				self.ksc[0].remove(event.key)
			
		#mouse or keydown
		if event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
			if event.type == pygame.MOUSEMOTION:
				self.mouse_rect = pygame.Rect(event.pos[0], event.pos[1], 3, 3)
			if event.type == pygame.MOUSEBUTTONDOWN:		
				self.edit = {}
				if self.itsgame:
					if self.chatbox.myrect:
						if self.chatbox.myrect.colliderect(event.pos[0], event.pos[1], 5, 5):
							if event.button == 4:  # Scroll up
								self.chatbox.scroll(-1)
							elif event.button == 5:  # Scroll down
								self.chatbox.scroll(1)					
						else:
							if event.button == 4:  # Scroll up
								self.inventory.current_index[0] = max(self.inventory.current_index[0] - 1, 0)
							elif event.button == 5:  # Scroll down
								self.inventory.current_index[0] = min(self.inventory.current_index[0] + 1, len(self.inventory.myrects) - 1)
					
			if self.inventory.myrects and self.mouse_rect:
				for i, t in enumerate(self.inventory.myrects): #invblock = color, index_number, x, y, sx, sy
					trect = pygame.Rect(t[2], t[3], t[4], t[5])
					self.inventory.iscolli = False
					if trect.colliderect(self.mouse_rect):
						if event.type == pygame.MOUSEMOTION:
							self.inventory.current_index[1] = i		
						if event.type == pygame.MOUSEBUTTONDOWN and int(event.button) == 1:
							self.inventory.current_index[0] = i
							
			if event.type == pygame.MOUSEBUTTONDOWN and self.chatbox.myrect and self.inventory.myrects and not self.chatbox.myrect.colliderect(event.pos[0], event.pos[1], 5, 5) and not any(pygame.Rect(t[2], t[3], t[4], t[5]).colliderect(self.mouse_rect) for t in self.inventory.myrects):
				#place/break shit
				#math for reverse scale (634.2342342342342 * 444 / 1280) - 160
				mouse_x_scaled = (self.mouse_rect.x * display.get_width() / self.display_rect.w) + self.game.scroll[0]
				mouse_y_scaled = (self.mouse_rect.y * display.get_height() / self.display_rect.h) + self.game.scroll[1]
				if int(event.button) == 1:
					self.network.network_req(f'worlde_{[mouse_x_scaled, mouse_y_scaled, self.mouse_rect.w, self.mouse_rect.h, int(event.button)]}')
				elif int(event.button) == 3:
					if self.inventory.current_index[0] > -1:
						self.network.network_req(f'worlde_{[mouse_x_scaled, mouse_y_scaled, self.mouse_rect.w, self.mouse_rect.h, int(event.button), self.inventory.current_index[0]]}')
						
						
			#if its menu, the botton edit
			if self.buttons.items() and self.itsmenu or self.game.isdialog:
				for name, data in self.buttons.items():
					rect, color, text, onb = data
					#if its editing
					if self.edit.items() and event.type == pygame.KEYDOWN:
						l = self.edit.get(str(name), None)
						if l:
							if event.key == pygame.K_RETURN:
								self.buttons[name] = rect, (0,0,0), text, onb
								self.edit = {}
							elif event.key == pygame.K_BACKSPACE:
								text = text[:-1]
								self.buttons[name] = rect, color, text, onb
								if name == 'username_':
									self.username = text
								if name == 'pass_':
									self.pw = text
								if name == 'dst_':
									self.dst = text
							elif event.unicode in '1234567890wertyuioplkjhgfdsaxcvbnmQWERTYUIOPKJHGFDSAZXCVBNM.:':
								text += event.unicode
								if name == 'username_':
									self.username = text
								if name == 'pass_':
									self.pw = text
								if name == 'dst_':
									self.dst = text					
								self.buttons[name] = rect, color, text, onb
					elif event.type == pygame.MOUSEMOTION or event.type == pygame.MOUSEBUTTONDOWN:
						l = self.edit.get(str(name), None)
						if rect.colliderect(event.pos[0], event.pos[1], 5, 5):
							if not l and not onb:
								self.buttons[name] = rect, (255,0,0), text, onb
							if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
								n = name.split('_')
								self.buttons[name] = pygame.Rect(0,0,0,0), color, text, onb
								self.edit = {}
								if n[0] == 'onb':
									onb = not onb
									#self.buttons[name] = rect, color, text, onb
									if onb:
										self.buttons[name] = rect, (124,252,0), text, onb
										if n[1] == 'fps':
											self.fpss = True
									else:
										self.buttons[name] = rect, (0,0,0), text, onb		
										if n[1] == 'fps':
											self.fpss = False										
								if n[0] == 'exit':
									sys.exit()
						
								if n[0] == 'login':
									self.back.append('main')
									self.change_screen('login')	
						
								if n[0] == 'back':
									self.change_screen('back')
						
								if n[0] == 'about':
									self.change_screen('about')
									if self.itsmenu:
										self.back.append('main')
								
								if n[0] == 'settings':	
									if self.itsgame:
										self.back.append('game')
									if self.itsmenu:
										self.back.append('main')
									self.change_screen('settings')
							
								if n[0] == 'reselution':
									self.back.append('settings')
									self.change_screen('settings_vids')
							
								if n[0] == 'keyboard':	
									self.back.append('settings')
									self.change_screen('settings_keyboard')	
							
								if n[0] == 'graphics':
									self.back.append('settings')
									self.change_screen('settings_graphics')	
							
								if n[0] == 'dialog':
									self.network.network_req('dialog_'+n[1])
								if n[0] == 'gamemenu':
									self.game.menuon = False
									if n[1] == 'back':
										pass
									if n[1] == 'help':
										pass
									if n[1] == 'store':
										self.network.network_req('store_1')
									if n[1] == 'about':
										pass
									if n[1] == 'options':
										self.game.optionson = True
										self.back.append('game')
										self.change_screen('settings')	
									if n[1] == 'respawn':
										self.network.network_req('respawn_1')									
									if n[1] == 'exit':
										self.terminate_game()
										self.change_screen('back')						
								if n[0] == 'screen':
									self.dialogs = {}
									self.inventory.reset_pos()
									if n[1] == 'full':
										screen = pygame.display.set_mode(fwindow, pygame.FULLSCREEN)
									else:
										w = str(n[1]).split('x')[0]
										h = str(n[1]).split('x')[1]
										screen = pygame.display.set_mode((int(w),int(h)), 0)
									self.display_rect = screen.get_rect()
									self.options_w = self.display_rect.w*0.2
									self.options_h = 0.06*self.display_rect.h
									self.options_x = self.display_rect.w / 15
									self.options_y = self.display_rect.h / 15
									self.option_spacer = 0.00006 * self.display_rect.w * self.display_rect.h
									self.font = pygame.font.Font("./recs/menu/gothicb.ttf", int(0.00003*self.display_rect.w * self.display_rect.h))
								if n[0] == 'dst':
									self.buttons[name] = rect, (124,252,0), text, onb
									self.dst = text
									self.edit = {}
									self.edit[name] = True
								if n[0] == 'username':
									self.buttons[name] = rect, (124,252,0), text, onb
									self.username = text
									self.edit = {}
									self.edit[name] = True									
								if n[0] == 'pass':
									self.buttons[name] = rect, (124,252,0), text, onb
									self.pw = text
									self.edit = {}
									self.edit[name] = True									
						elif not l:
							if not onb:
								self.buttons[name] = pygame.Rect(0,0,0,0), (0, 0, 0), text, onb
		
	def add_dialog(self, name, messages):
		self.dialogs[name] = messages # [ width, height, color, {'button':text, nm, spacer}] 
		
	def dialog_blit(self, name, dis):
		display_rect = dis.get_rect()
		box_data = self.dialogs[name]
		chatbox_width = self.display_rect.w * box_data[0]
		chatbox_height = self.display_rect.w * box_data[1]
		chatbox_x = display_rect.centerx - (chatbox_width // 2)
		chatbox_y = display_rect.centery - (chatbox_height // 2)
		blue_box_surface = pygame.Surface((chatbox_width, chatbox_height), pygame.SRCALPHA)
		bbx = blue_box_surface.get_rect()
		pygame.draw.rect(blue_box_surface, box_data[2], bbx)
		dis.blit(blue_box_surface, (chatbox_x, chatbox_y))
		for i, (name, data) in enumerate(box_data[3].items()):	
			if name.split('_')[0] == 'button':
				text, nm, spacer = data
				self.button_blitter(text, (255, 255, 255), self.options_w, self.options_h, (0, 0, 0), chatbox_x + (chatbox_width - self.options_w) // 2, chatbox_y +self.options_h + spacer, nm, False, None, None, dis)	
			if name.split('_')[0] == 'text':
				text, nm, spacer = data
				self.text_blitter(text, chatbox_x + (chatbox_width - self.options_w) // 2, chatbox_y +self.options_h + spacer, dis)
				
	def text_blitter(self, text, x, y, disp) -> None:
		disp.blit(text, (x, y))
		
	def button_blitter(self, text, t_color, button_w, button_h, color, posx, posy, name, isinp, theinpt, inphint, disp) -> None:	
		obj = self.buttons.get(str(name), None)
		render_text = self.font.render(text, False, t_color)
		inputt = pygame.Surface((button_w,button_h))
		inp = render_text.get_rect()
		if obj:
			inputt.fill(obj[1])
			self.buttons[name] = pygame.Rect(posx,posy,button_w,button_h), obj[1], obj[2], obj[3]
			if isinp:
				render_text = self.font.render(theinpt + str(obj[2]), False, t_color)
				inp = render_text.get_rect()
		else:
			inputt.fill(color)
			self.buttons[name] = pygame.Rect(posx,posy,button_w,button_h), color, inphint, False #rect, color, input, inputtext, onb
			if isinp:
				if name == 'username_':
					self.username = inphint
				if name == 'pass_':
					self.pw = inphint
				if name == 'dst_':
					self.dst = inphint
		inp.center = (button_w // 2, button_h // 2)
		inputt.blit(render_text, inp)
		disp.blit(inputt, (posx, posy))
						
	def change_screen(self, thing) -> None:
		self.main = False
		self.login = False
		self.about = False
		self.settings = False
		self.settings_vids = False
		self.settings_keyboard = False
		self.settings_graphics = False
		
		for name, data in self.buttons.items():
			rect, color, text, onb = data
			self.buttons[name] = pygame.Rect(0,0,0,0), color, text, onb
      
		if thing == 'login':
			self.login = True
			self.network.loggingin = True
			
		if thing == 'game':
			self.itsmenu = False
			self.itsgame = True
			
		if thing == 'about':
			self.about = True
			
		if thing == 'main':
			self.main = True
			self.back = []
		if thing == 'settings':
			self.settings = True
			
		if thing == 'settings_vids':
			self.settings_vids = True
			
		if thing == 'settings_keyboard':
			self.settings_keyboard = True
			
		if thing == 'settings_graphics':
			self.settings_graphics = True
			
		if thing == 'back':
			if self.back:
				self.change_screen(self.back.pop())	
			
	def terminate_game(self) -> None:
		if self.network._s:
			self.network.network_req('world_exit')
		self.itsmenu = True
		self.itsgame = False
		self.dialogs = {}
		self.network.end_network()
		self.network = None
		del self.network
		self.network: Networking = Networking(self)
		self.game = None
		del self.game
		self.game: Game = Game(self)
		self.inventory = None
		del self.inventory
		self.inventory: Inventory = Inventory()	
			
	def start_game(self) -> None:
		if self.network.welcome_event.is_set():
			self.change_screen('game')
		
	def login_blit(self, screen) -> None:
		self.chatbox.chatbox_blit(screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*7, 'back_', False, None, None, screen)
		if self.network.loggingin:
				self.network.loggingin = False
				self.network.connect_event.set()
		self.start_game()
      
	def graphics_blit(self, screen) -> None:
		self.button_blitter('FPS', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y, 'onb_fps', False, None, None, screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'back_', False, None, None, screen)
				
	def keyboard_blit(self, screen) -> None:
		self.text_blitter(self.font.render("Soon", True, (255, 100, 0)), self.options_x, self.options_y, screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'back_', False, None, None, screen)
		
	def settings_vid_blit(self, screen) -> None:
		self.button_blitter('1280x720', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y, 'screen_1280x720', False, None, None, screen)
		self.button_blitter('1366×768', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'screen_1366x768', False, None, None, screen)
		self.button_blitter('1440×900', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*2, 'screen_1440x900', False, None, None, screen)
		self.button_blitter('1600×900', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*3, 'screen_1600x900', False, None, None, screen)
		self.button_blitter('1920×1080', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*4, 'screen_1920x1080', False, None, None, screen)
		self.button_blitter('Full Screen', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*5, 'screen_full', False, None, None, screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*6, 'back', False, None, None, screen)
		
	def settings_blit(self, screen) -> None:
		self.button_blitter('Reselution', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y, 'reselution_', False, None, None, screen)
		self.button_blitter('Keyboard', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'keyboard_', False, None, None, screen)
		self.button_blitter('Graphics', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*2, 'graphics_', False, None, None, screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*3, 'back_', False, None, None, screen)
				
	def about_blit(self, screen) -> None:
		self.text_blitter(self.font.render("Soon", True, (255, 100, 0)), self.options_x, self.options_y, screen)
		self.button_blitter('Back', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'back_', False, None, None, screen)
		
	def main_blit(self, screen) -> None:
		self.button_blitter('Login', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y, 'login_', False, None, None, screen)
		self.button_blitter('Settings', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer, 'settings_', False, None, None, screen)
		self.button_blitter('About', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*2, 'about_', False, None, None, screen)
		self.button_blitter('Exit', (255, 255, 255), self.options_w, self.options_h, self.black_color, self.options_x, self.options_y+self.option_spacer*3, 'exit_', False, None, None, screen)
		self.button_blitter('', (255, 255, 255), self.options_w*2, self.options_h, self.black_color, self.display_rect.centerx, self.display_rect.centery, 'dst_', True, "IP:PORT: ", "127.0.0.1:6003", screen)
		self.button_blitter('', (255, 255, 255), self.options_w*2, self.options_h, self.black_color, self.display_rect.centerx, self.display_rect.centery-self.option_spacer*2, 'username_', True, "NAME: ", "admin", screen)
		self.button_blitter('', (255, 255, 255), self.options_w*2, self.options_h, self.black_color, self.display_rect.centerx, self.display_rect.centery-self.option_spacer, 'pass_', True, "PASS: ", "admin", screen)	
			
	def run(self) -> None:
		while True:
			fps = clock.get_fps()
			if self.itsmenu:
				screen.blit(self.back_ground, (0, 0))
				if self.login:
					self.login_blit(screen)
				if self.main:
					self.main_blit(screen)
				if self.about:
					self.about_blit(screen)
				if self.settings:
					self.settings_blit(screen)
				if self.settings_vids:
					self.settings_vid_blit(screen)
				if self.settings_keyboard:
					self.keyboard_blit(screen)
				if self.settings_graphics:
					self.graphics_blit(screen)
			
			if self.itsgame:
				self.game.loop()
			if self.fpss:
				fps_text = self.font.render("FPS: "+str(fps), True, (0, 0, 0))
				screen.blit(fps_text, (10, 10))							
			self.events()				
			pygame.display.update()
			clock.tick(60)

class Game:
	def __init__(self, menu) -> None:
		self.menu = menu
		self.animation: Animation = Animation()
		self.animation.init_images(pygame)
		#player shit
		self.player_width = 14 
		self.player_height = 40
		self.playerect = None
		self.player_img = None
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
					x, y, w, h, f, l = data 
					player_positionp = (int(x), int(y))
					textp = self.menu.font.render(play, True, (255, 255, 255))
					scaled_text_position = ((player_positionp[0] * self.menu.display_rect.w) / display.get_width() - textp.get_width()/2,
                        (player_positionp[1] * self.menu.display_rect.h) / display.get_height() - 40)					
					self.playern_blit(scl, str(play), int(x)- self.scroll[0], int(y)- self.scroll[1])
		except Exception as e:
			print(e)		

		
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
		except Exception as e:
			print(e)
		
	def world_players_blit(self) -> None:	
		try:
			if self.menu.network.world_players.items():
				for play, data in self.menu.network.world_players.items():
					x, y, w, h, f, lista = data
					cl = pygame.Rect(int(x),int(y),int(w),int(h))
					display.blit(pygame.transform.flip(self.animation.image,int(f),False),(cl.x-self.scroll[0],cl.y-self.scroll[1]))
					if len(lista.split('\n')) > 1:
						for item in lista.split('\n'):
							if item:
								itid, x1, x2, y1 = item.split(',')
								itemd = self.menu.network.items[1].get(str(itid), None)
								offset = int(x1)
								if int(f):
									offset = int(x2)	
								display.blit(pygame.transform.flip(itemd,int(f),False),(cl.x-offset-self.scroll[0],cl.y-int(y1)-self.scroll[1]))
		except Exception as e:
			print(e)
				
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
		
		self.animation.loop(pygame)
		#player
		if self.animation.image:
			display.blit(pygame.transform.flip(self.animation.image,self.flip,False),(self.playerect.x-self.scroll[0],self.playerect.y-self.scroll[1]))
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
		
if __name__ == "__main__":
	Menu().run()