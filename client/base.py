import pygame, os, time, random

window = (1000,700)
screen = pygame.display.set_mode(window, pygame.RESIZABLE)
display = pygame.Surface((300,200))
clock = pygame.time.Clock()
#VARIABLES
recsbp = 'recs/blocks/'
recpp = 'recs/player/'
dirt = pygame.image.load(recsbp + 'dirt.png')
grass = pygame.image.load(recsbp + 'grass.png')
player = pygame.image.load(recpp + 'player.png')
playerw = 15
playerh = 44
playerect = pygame.Rect(100,100,playerw,playerh)
moving_right = False
moving_left = False
player_action = 'idle'
player_frame = 0
player_flip = False
punch = False
punch1 = False
punch2 = False
kick = False
kick1 = False
kick2 = False
kiked = False
tilesz = 20
fall = False
verm = 0
krnch = False
idlenz = []
mapl ="""

1111      11111122222
1 1            12
1    1 11  111112
  1              11                        1 11 1 11111111    111111111111          1 1 1 1111  11 1
  0             111    2      1  11  11 1    1 11    11    1   1   1
  1              11          1             1     1     1    1
  11101111111110000000001                  1 
        22                 222    222222              1 1 1 1 1 111111111111111111111111111111111
1111111110111111111                               1
                         222222222             1     1   1  1
1111111111111111111111111111111111111111111111111111111111111111"""
mapl = mapl.splitlines()
print(mapl)
global animation_frames
animation_frames = {}
def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path
    animation_frame_data = []
    n = 1
    for frame in frame_durations:
        animation_frame_id = 'recs/' + animation_name + '_' + str(n)
        img_loc = animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0,0,0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(5):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame       
animation_database = {}
for i in range(49):
  idlenz.append(7)
animation_database['run'] = load_animation('player/run/run',[7])
animation_database['idle'] = load_animation('player/idle/idle',idlenz)
game_map = {}
#animation variables
playerr = pygame.image.load(recpp + 'player.png')
playerl = pygame.transform.flip(playerr, 1,0)

def animation():
  global player, playermv, player_action, player_flip,player_frame
  if playermv[0] == 0:
    player_action,player_frame = change_action(player_action,player_frame,'idle')
  if playermv[0] > 0:
    player_flip = False
    player_action,player_frame = change_action(player_action,player_frame,'run')
  if playermv[0] < 0:
    player_flip = True
    player_action,player_frame = change_action(player_action,player_frame,'run')

def scroll(sscroll,zscroll):
  sscroll[0] += (playerect.x-sscroll[0]-152)/1
  sscroll[1] += (playerect.y-sscroll[1]-106)/1
  zscroll[0] = int(sscroll[0])
  zscroll[1] = int(sscroll[1])
  return zscroll,sscroll

def move(playermv):
  if moving_right == True:
    playermv[0] += 2
  if moving_left == True:
    playermv[0] -= 2
  return playermv
  
def playerc(tilesrect,playermv,playerect):
  global verm, fall, didc
  playermv[1] += verm
  verm += 0.2
  if verm > 3:
    verm = 3
  playerect.x += playermv[0]
  for tile in tilesrect:
    ch = pygame.Rect(tile[0],tile[1],tilesz,tilesz)
    tile[3] = ch[3]  
    if playerect.colliderect(tile):
      if playermv[0] > 0:
        playerect.right = tile.left
      elif playermv[0] < 0:
        playerect.left = tile.right
  playerect.y += playermv[1]
  for tile in tilesrect:
    if playerect.colliderect(tile):  
      if playermv[1] > 0:
        playerect.bottom = tile.top
        verm = 0
        fall = False
      elif playermv[1] < 0:
        playerect.top = tile.bottom
def buildmap(zscroll):
  for tile in tilesrect:
    dirtid = pygame.Rect(0,0,0,1)
    grassid = pygame.Rect(0,0,0,2)
    if dirtid[3] == tile[3]:
      display.blit(dirt, (tile[0]-zscroll[0],tile[1]-zscroll[1]))
    if grassid[3] == tile[3]:
      display.blit(grass, (tile[0]-zscroll[0],tile[1]-zscroll[1]))

def map(zscroll):
  global mapl
  print(mapl)
  for y, line in enumerate(mapl):
    for x, tile in enumerate(line):
      if tile == '1':
        tilesrect.append(pygame.Rect(x*tilesz,y*tilesz,tilesz,1))
      if tile == '2':
        tilesrect.append(pygame.Rect(x*tilesz,y*tilesz,tilesz,2))
  #bap()
  buildmap(zscroll)
  return tilesrect
        
        
def updateS(zscroll):
  global player_frame, player, player_img_id
  player_frame += 1
  if player_frame >= len(animation_database[player_action]):
    player_frame = 0
  player_img_id = animation_database[player_action][player_frame]
  player = animation_frames[player_img_id]
  display.blit(pygame.transform.flip(player,player_flip,False),(playerect.x-zscroll[0],playerect.y-zscroll[1]))
  screen.blit(pygame.transform.scale(display,window),(0,0))
  pygame.display.update()

def events(playermv):
  global moving_right, moving_left, verm, fall, krnch, window
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      os.system('exit') 
    elif event.type == pygame.VIDEORESIZE:
      window = event.size
      screen = pygame.display.set_mode(window, pygame.RESIZABLE)
      display = pygame.Surface((event.w, event.h))
      pygame.display.update()
    if event.type == pygame.KEYDOWN: 
      if event.key == pygame.K_d:
        moving_right = True
      if event.key == pygame.K_a:
        moving_left = True
      if event.key == pygame.K_w and fall == False:
        verm = -4
        fall = True
      if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
        krnch = True
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_d:
        moving_right = False
      if event.key == pygame.K_a:
        moving_left = False
      if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
        krnch = False        
  return moving_right, moving_left, verm, fall, krnch

while True:
  display.fill((146,244,255))
  playermv = [0,0]
  sscroll = [0,0]
  zscroll = [0,0]
  tilesrect = []
  events(playermv)
  scroll(sscroll,zscroll)
  map(zscroll)
  move(playermv)
  playerc(tilesrect,playermv,playerect)
  animation()
  updateS(zscroll)
  clock.tick(60)
