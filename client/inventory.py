import pygame
class Inventory: 
	def __init__(self):
		self.font = pygame.font.Font("./recs/menu/font.ttf", 13)
		self.box_size = 65
		self.margin = 7
		self.inventory_s_number = 8
		self.myrects = []
		self.current_index = [-1, -1, ""]
		self.inventory_items = {} #{'itemid' = [count, path]}
		self.finv = False
		self.bname = []
		
	def reset_pos(self):
		self.finv = False
		self.myrects.clear()
		
	def set(self, itemid, count, path, name):
	  self.inventory_items[itemid] = [count, path, name]
	  self.inventory_items = {int(k): v for k, v in sorted(self.inventory_items.items())}
	def remove(self, itemid):
	  self.inventory_items.pop(itemid)
				
	def inventory_blit(self, dis, mouserect):
		if not self.finv:
			self.create_front_inv(dis)
			self.finv = True
			
		for i, invblock in enumerate(self.myrects):
			#invblock = color, index_number, x, y, sx, sy
			c = ()
			if self.current_index[1] == i:
				c = (198,198,198)
			else:
				c = invblock[0]				
			if self.current_index[0] == i:
				c = (49,49,49)
			trect = pygame.draw.rect(dis, c, (invblock[2], invblock[3], invblock[4], invblock[5]))	
			if len(self.inventory_items.items()) > i:
				it = list(self.inventory_items.items())
				if it:
					scaled_item_size = (int(self.box_size * 0.8), int(self.box_size * 0.8))
					item_image = pygame.transform.scale(it[i][1][1], scaled_item_size)
					if self.current_index[0] == i:
						self.current_index[2] = it[i][1][2]
						bbname = self.font.render(str(self.current_index[2]), True, (255, 255, 255))
						bbname_rect = bbname.get_rect(bottomright=trect.topright)
						bbname_rect.centerx = trect.centerx
						dis.blit(bbname, bbname_rect)	
					dis.blit(item_image, item_image.get_rect(center=trect.center).topleft)
				
					count_text = self.font.render(str(it[i][1][0]), True, (255, 255, 255))
					dis.blit(count_text, count_text.get_rect(bottomright=trect.bottomright).topleft)	
				
		
	def create_back_inv(self, dis):
		pass
	def create_front_inv(self, dis):
		total_height = self.box_size + 2 * self.margin  # Height of a single box with margins
		start_x = (dis.get_width() - (4 * (self.box_size + self.margin) - self.margin)) // 2 - self.box_size
		start_y = dis.get_height() - total_height  # Updated this line
		for i in range(self.inventory_s_number):			
			box_x = start_x + i * (self.box_size + self.margin)
			box_y = start_y
			self.myrects.append([(139,139,139,255), i, box_x, box_y, self.box_size, self.box_size, box_x+box_y+self.box_size])
