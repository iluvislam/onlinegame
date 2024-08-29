import os

class Animation:

	def __init__(self) -> None:
		self.animation = {}
		self.image = None
		self.frame = 0
		self.duration = 100
		self.start_time = 0
		
	def loop(self, pygame, moving_right = False, moving_left = False) -> None:
		if pygame.time.get_ticks() - self.start_time >= self.duration:
			self.frame += 1
			self.start_time = pygame.time.get_ticks()
			
			if self.frame >= len(self.animation['idle']):
				self.frame = 0			
				
			self.image = self.animation['idle'][self.frame][0]
			self.duration = self.animation['idle'][self.frame][1]
				
	def init_images(self, pygame) -> None:
		idle_path = 'recs/player/idle/'
		self.start_time = pygame.time.get_ticks()
		self.animation['idle'] = []
		self.animation['run'] = []
		for filename in os.listdir(idle_path):
			t = 100
			if int(filename.split('_')[-1].split('.')[0]) == 0:
				t = 3000
			image = pygame.image.load(os.path.join(idle_path, filename))
			self.animation['idle'].append([image, t])   