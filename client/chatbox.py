import pygame

class Chatbox:
	def __init__(self):
		self.chatbox_text = [] # List to store chat messages
		self.max_lines = 6 # Maximum number of lines to display
		self.lines_height = 25 # Height of each line
		self.chatbox_height = self.lines_height * self.max_lines
		self.chatbox_y = 0 # Position at the top of the screen
		self.font = pygame.font.Font("./recs/menu/font.ttf", 13)
		self.scroll_position = 0 # Current scroll position
		self.old_chat = 0
		self.myrect = None
		self.counter = 0
		self.cursor_visible = False
		self.cursor_blink_frequency = 500  # Cursor blink frequency in milliseconds
		self.cursor_last_blink_time = pygame.time.get_ticks()				
		self.input_text = ""
		self.istyping = False

	def split_string_by_length(input_string, chunk_length):
		return [input_string[i:i+chunk_length] for i in range(0, len(input_string), chunk_length)]
	
	def add_message(self, message):
		self.chatbox_text.append("[" + str(self.counter) + "] " + message)
		self.counter += 1
		self.scroll_position = max(0, len(self.chatbox_text) - self.max_lines)
		
	def chatbox_blit(self, dis):
		display_rect = dis.get_rect()
		self.lines_height = display_rect.w*display_rect.h/37000
		self.font = pygame.font.Font("./recs/menu/font.ttf", min(display_rect.w, display_rect.h) // 60)
		chatbox_width = display_rect.width * 0.9 # 90% of the screen width
		chatbox_height = display_rect.height * 0.3 # 30% of the screen height
		chatbox_x = (display_rect.width - chatbox_width) / 4 # Centered horizontally
    # Create a transparent blue box with a blue border
		blue_color = (128, 128, 255, 128)
		blue_box_surface = pygame.Surface((chatbox_width, chatbox_height), pygame.SRCALPHA)
		pygame.draw.rect(blue_box_surface, blue_color, blue_box_surface.get_rect())
    # Blit the transparent blue box onto the display surface
		pygame.display.get_surface().blit(blue_box_surface, (chatbox_x, self.chatbox_y))
		self.myrect = pygame.Rect(chatbox_x, self.chatbox_y, chatbox_width, chatbox_height)
		if self.old_chat != len(self.chatbox_text) and len(self.chatbox_text) > 10:
			self.old_chat = len(self.chatbox_text)
			self.scroll_position += 1

		text_y = self.chatbox_y # Adjust these values for desired position
		for i in range(self.scroll_position, min(self.scroll_position + self.max_lines, len(self.chatbox_text))):
			if i >= 0 and i < len(self.chatbox_text):
				line = self.chatbox_text[i]
				text_length = int(chatbox_width/13.6)
				ft = ""
				while len(line) > text_length:
					ft = line[:text_length]
					text_surface = self.font.render(ft, True, (255, 255, 255))
					blue_box_surface.blit(text_surface, (chatbox_x + 10, text_y))
					text_y += self.lines_height
					line = line[text_length:]
					
				text_surface = self.font.render(line, True, (255, 255, 255))
				blue_box_surface.blit(text_surface, (chatbox_x + 10, text_y))
				text_y += self.lines_height


		dis.blit(blue_box_surface, (chatbox_x, self.chatbox_y))
		
    # Text Entry Box
		text_entry_box_width = display_rect.width * 0.9  # 90% of the screen width
		text_entry_box_height = display_rect.height * 0.05  # 5% of the screen height
		text_entry_box_x = (display_rect.width - text_entry_box_width) / 4  # Centered horizontally
		text_entry_box_y = self.chatbox_y + chatbox_height  # Directly below the blue box
		if len(self.input_text) > 90:
			self.input_text = self.input_text[:90]
		input_text_surface = self.font.render(self.input_text, True, (0, 0, 0))
		dis.blit(input_text_surface, (text_entry_box_x + 10, text_entry_box_y + 10)) 
    # Create a transparent white box with a black border for text entry
		white_color = (255, 255, 255, 128)
		black_color = (10, 10, 10)
		text_entry_box_surface = pygame.Surface((text_entry_box_width, text_entry_box_height), pygame.SRCALPHA)
		pygame.draw.rect(text_entry_box_surface, black_color, text_entry_box_surface.get_rect(), 2)
		pygame.draw.rect(text_entry_box_surface, white_color, text_entry_box_surface.get_rect())

    # Blit the transparent white box onto the display surface
		pygame.display.get_surface().blit(text_entry_box_surface, (text_entry_box_x, text_entry_box_y))

    # Additional code for handling text entry can be added here
		current_time = pygame.time.get_ticks()
		if current_time - self.cursor_last_blink_time >= self.cursor_blink_frequency:
			self.cursor_visible = not self.cursor_visible
			self.cursor_last_blink_time = current_time

		if self.cursor_visible and self.istyping:
			cursor_x = text_entry_box_x + 10 + self.font.size(self.input_text[:])[0]
			cursor_y = text_entry_box_y + 5  # Adjust for vertical alignment
			pygame.draw.line(dis, (10, 10, 10), (cursor_x, cursor_y), (cursor_x, cursor_y + text_entry_box_height - 10), 2)
		dis.blit(text_entry_box_surface, (text_entry_box_x, text_entry_box_y))
		
	def scroll(self, direction):
		self.scroll_position += direction
		if self.scroll_position < 0:
			self.scroll_position = 0
		if self.scroll_position > (len(self.chatbox_text) - self.max_lines):
			self.scroll_position = max(0, len(self.chatbox_text) - self.max_lines)
