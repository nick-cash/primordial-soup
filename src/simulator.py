import pygame, sys,os,time,math,random,copy
import zbscreen, zblevel,loadcellgraphic

from pygame.locals import *

class Behavior:
   def __init__(self):
      self.chance = 1 # always
    
   def perform(self, cell):
      print 'no root'
    
   def applyChanced(self, cell):
      if random.random() < self.chance:
         self.perform(cell)
    
class LiveBehavior(Behavior):
   """The behavior of life. Metabolism requires energy"""
   def __init__(self):
      Behavior.__init__(self)

   def perform(self, cell):
      cell.energy_lose

class PhotosynthesisBehavior(Behavior):
   def __init__(self):
      Behavior.__init__(self)
      self.chance = 0.25

   def perform(self, cell):
      cell.energy_gain

#We'll precache the different images here.  The server will specify which one to use.
system_images = {}
cellfcounts = {"circle":10,"vibrio":10,"spiro":2,"bacillus":9}
celltypes = {"circle": "coccus.png", "vibrio": "vibrio.png", "spiro": "spirochaete.png", "bacillus": "bacillus.png"}
playerhues = {"blue": 240.0, "purple": 302.0, "yellow": 60.0, "cyan": 163.0, "red": 16.0}
huevariants = {"l": -7, "m": 0.0, "n": 7}
#loadcellgraphic.load_cell("cocci-simcell.png", hue, sat)

def euclidean_distance (start_tuple, end_tuple):
   """ Takes two coordinate tuples, returns a distance """
   horzdist = math.fabs(float(start_tuple[0] - end_tuple[0]))
   vertdist = math.fabs(float(start_tuple[1] - end_tuple[1]))
   return ((horzdist**2)+(vertdist**2)**0.5)

def center_of_group(sgroup):
   if len(sgroup) == 0:
      return (-9000,9001) #over nine thousand!!!
   
   xsum = 0.0
   ysum = 0.0
   for s in sgroup.sprites():
      xsum += s.rect.center[0]
      ysum += s.rect.center[0]
   
   return (math.floor(xsum/len(sgroup)), math.floor(ysum/len(sgroup)))

class Player:
   def __init__(self, id, type, huename, mainpoint, sim):
      """ Takes type of cell, huename, mainpoint (mainpoint is an (x,y) tuple around
      which his players start.) """
      self.id = 0
      self.type = type
      self.huename = huename
      self.mainpoint = mainpoint
      self.sprites = pygame.sprite.Group()
      self.popcap = 250
      self.activedivide = 0
      self.deadlist = [] #Stores list of deceased until next population enforcement.
      self.action = "evade"
      self.opponents = [] #List of opponents provided by the simulator
      self.max_x_speed = 30
      self.max_y_speed = 30

      self.sprite_stats = Traits(type)
      self.sprite_id = 0
      self.sprite_dict = {}

      if self.sprite_stats.aggro > 0:
         self.action = "pursue"

   def next_sprite_id(self):
      self.sprite_id += 1
      return self.sprite_id

   def add_sprite(self, centerx, centery):
      #hue variant is purely aesthetic, random okay      
      rv = random.choice(huevariants.keys())
      imkey = "{}-{}-{}-{}".format(self.huename,rv,self.type,100)
      sprite = CellSprite(system_images[imkey],16,16,centerx,centery,self,rv)

      #add other properties here.
      self.sprites.add(sprite)
      self.sprite_dict[sprite.id] = sprite

      return sprite
   
   def spawn_initial(self, count):
      """ Spawns the initial units for a player, based on their mainpoint."""
      current_level = 0
      MinX = 32
      MinY = 32
      rowsize = math.floor(float(count)**0.5)
      startx = MinX + self.mainpoint[0] + (-12 * math.floor(rowsize/2))
      starty = MinY + self.mainpoint[1] + (-12 * math.floor(rowsize/2))

      for i in range(0, count):
         staggerx = -8 if (i%2) == 0 else 8
         staggery = (8 if (i%2) == 0 else -8) + (-10 if (i%3) == 0 else 10)
         centery = staggerx + starty + (12 * math.floor(i/rowsize))
         centerx = staggery + startx + (12 * (i%rowsize))
         self.add_sprite(centerx, centery)
   
   def enforce_popcap(self):
      """ Enforce the population cap, only call at dividing time. """
      slist = self.sprites.sprites()
      num_sprites = len(slist)

      if(num_sprites > self.popcap):
         self.deadlist = []

         num_to_delete = num_sprites - self.popcap

         print "Player has {} sprites, deleting {}".format(num_sprites, num_to_delete)

         for i in range(num_to_delete):
            self.kill_sprite(slist[0])

      if len(self.deadlist) > 5:
         self.deadlist = []            

   def kill_sprite(self, sprite):
      self.deadlist.append(sprite)
      self.sprites.remove(sprite)

      if self.sprite_dict.has_key(sprite.id):
         del self.sprite_dict[sprite.id]

class Traits():
   def __init__(self, type, stats=None):
      self.energy = 0
      self.comms = 0
      self.aggro = 0
      self.speed = 0
      self.defense = 0

      if stats:       
         for stat in stats:
            setattr(self, stat, stats[stat])          

      else:
         if type == "circle":
            self.energy = 1
            self.comms = 1
            self.aggro = 1
            self.speed = 1
            self.defense = 1
         elif type == "vibrio":
            self.energy = 1
            self.speed = 3
            self.comms = 1
         elif type == "spiro":
            self.energy = 2
            self.aggro = 2
            self.defense = 1
         else:
            self.defense = 2
            self.energy = 2
            self.speed = 1

   def get_defense(self):
      return self.defense

   def get_stats(self):
      stats = {}

      stats["energy"] = self.energy
      stats["aggro"] = self.aggro
      stats["defense"] = self.defense
      stats["comms"] = self.comms
      stats["speed"] = self.speed

      return stats

class CellSprite (pygame.sprite.Sprite):
   def action_evade(self):
      """ Somehow, we should get this in a better way. """
      MinX = 32
      MinY = 32
      MaxX = 688
      MaxY = 572
      
      nearestgroupcenter = None
      nearestdist = 10000
      target = None
      mecheck = self.rect.inflate(64,64)
      col_sprite = pygame.sprite.Sprite()
      col_sprite.rect = mecheck
      for opponent in self.player.opponents:
         list = pygame.sprite.spritecollide(col_sprite, opponent.sprites, False)
         if len(list) > 0:
            target = list[0]
            break
      
      xmulti = -1 if self.player.mainpoint[0] < (MaxX-MinX)/2 else 1
      ymulti = -1 if self.player.mainpoint[1] < (MaxY-MinY)/2 else 1
            
      if target == None:
         if self.xspeed == 0:
            self.xspeed = xmulti * self.player.max_x_speed
         
         if self.yspeed == 0:
            self.yspeed = ymulti * self.player.max_y_speed
      else:
         xspeed = (target.rect.center[0] - self.rect.center[0]) * -1
         yspeed = (target.rect.center[1] - self.rect.center[1]) * -1
         if math.fabs(xspeed) > self.player.max_x_speed:
            xspeed = self.player.max_x_speed * (1 if xspeed > 1 else -1)
         if math.fabs(yspeed) > self.player.max_y_speed:
            yspeed = self.player.max_y_speed * (1 if yspeed > 1 else -1)
         if math.fabs(xspeed) < 10 :
            xspeed = self.player.max_x_speed/2 * xmulti
         if math.fabs(yspeed) < 10 :
            yspeed = self.player.max_y_speed/2 * ymulti            
         self.xspeed = xspeed
         self.yspeed = yspeed

   def action_pursue(self):
      """ Pursue first sited enemy, otherwise begin movement in standar pattern """
      MinX = 32
      MinY = 32
      MaxX = 688
      MaxY = 572
      
      nearestgroupcenter = None
      nearestdist = 10000
      target = None
      mecheck = self.rect.inflate(64,64)
      col_sprite = pygame.sprite.Sprite()
      col_sprite.rect = mecheck
      for opponent in self.player.opponents:
         list = pygame.sprite.spritecollide(col_sprite, opponent.sprites, False)
         if len(list) > 0:
            target = list[0]
            break
      
      xmulti = 1 if self.player.mainpoint[0] < (MaxX-MinX)/2 else -1
      ymulti = 1 if self.player.mainpoint[1] < (MaxY-MinY)/2 else -1
            
      if target == None:
         if self.xspeed == 0:
            self.xspeed = xmulti * self.player.max_x_speed
         
         if self.yspeed == 0:
            self.yspeed = ymulti * self.player.max_y_speed
      else:
         xspeed = target.rect.center[0] - self.rect.center[0]
         yspeed = target.rect.center[1] - self.rect.center[1]
         if math.fabs(xspeed) > self.player.max_x_speed:
            xspeed = self.player.max_x_speed * (1 if xspeed > 1 else -1)
         if math.fabs(yspeed) > self.player.max_y_speed:
            yspeed = self.player.max_y_speed * (1 if yspeed > 1 else -1)
         if math.fabs(xspeed) < 10 :
            xspeed = self.player.max_x_speed/2 * xmulti
         if math.fabs(yspeed) < 10 :
            yspeed = self.player.max_y_speed/2 * ymulti            
         self.xspeed = xspeed
         self.yspeed = yspeed

   def __init__(self, srcimage, width, height, centerx, centery, player, hv):
      """ Produce a cell sprite, tie it to a player with a hue variant 
      code to keep track of which variant we're using."""
      pygame.sprite.Sprite.__init__(self) #call Sprite initializer
      self.image = pygame.Surface((width, height), SRCALPHA)
      self.rect = self.image.get_rect()
      self.rect.center = (centerx, centery)
      self.start_of_life = pygame.time.get_ticks();
      self.animtime = 30
      self.stx = 0.0
      self.sty = 0.0
      self.frame = 0
      self.numframe = cellfcounts[player.type]
      self.src = srcimage
      self.orientation = 0;
      self.framedelay = 100;
      self.ticks = 0
      self.xspeed = 0
      self.yspeed = 0
      self.hv = hv
      self.origwidth = width
      self.origheight = height
      self.player = player
      
      self.id = player.next_sprite_id()

      #Reduce load by making them make fewer decisions
      self.decisiondelay = 500
      self.decisiontime = 100
      self.myaction = None #Allows the cell to switch away from the default action
      #Not yet implemented

      self.energy = 100 + (10 * self.player.sprite_stats.energy)
      self.behaviors = {}
      #self.load_behaviors()

      #Subject to change: sprite stats
      self.dividing = 0
      self.activedivide = 0
   
   def load_behaviors(self):
     self.behaviors = {}
     self.behaviors[0] = LiveBehavior()
     self.behaviors[1] = PhotosynthesisBehavior()
      
   def mutate(self):
      for index in self.behaviors:
         self.behaviors[index].applyChanced(self)
     
   def energy_lose(self):
     self.energy = max(0, self.energy - 1)
       
   def energy_gain(self):
     self.energy = min(100, self.energy + 1)
        
   def update(self, ticktime, sim):      
      self.decisiontime -= ticktime
      self.animtime -= ticktime      
      self.ticks += ticktime

      if sim.clientMode:
         #update for cell color on damage and such
         elvl = 10
         for i in range (10, 110, 10):
            if(self.energy < i):
               break
            else:
               elvl = i

         imkey = "{}-{}-{}-{}".format(self.player.huename,self.hv,self.player.type,elvl)
         self.src = system_images[imkey]

         #update for cell color on damage
         self.activedivide = self.player.activedivide

         if self.animtime < 0:
            self.switch_frame()
            self.animtime = self.framedelay

         return

      ncx = self.rect.center[0]
      ncy = self.rect.center[1]

      if self.decisiontime < 0:
         self.decisiontime = self.decisiondelay
         getattr(self, "action_{}".format(self.player.action))()

      #movement and behaviors here?
      self.mutate()
      
      MinY = 32;
      MinX = 32;
      MaxX = 688;
      MaxY = 572;

      self.stx += (ticktime/1000.0) * self.xspeed * self.player.sprite_stats.speed
      self.sty += (ticktime/1000.0) * self.yspeed * self.player.sprite_stats.speed
      
      if math.fabs(self.stx) > 1 :
         if self.stx > 0:
            ncx += math.ceil(self.stx)
            self.stx -= math.ceil(self.stx);
         else:
            ncx += math.floor(self.stx);
            self.stx -= math.floor(self.stx)

      if math.fabs(self.sty) > 1 :
         if self.sty > 0:
            ncy += math.ceil(self.sty)
            self.sty -= math.ceil(self.sty);
         else:
            ncy += math.floor(self.sty);
            self.sty -= math.floor(self.sty)      

      if(ncx < MinX):
         ncx = MinX+1
         self.xspeed *= -1
      elif(ncx > MaxX):
         ncx = MaxX-1
         self.xspeed *= -1
         
      if(ncy < MinY):
         ncy = MinY+1
         self.yspeed *= -1
      elif(ncy > MaxY):
         ncy = MaxY-1
         self.yspeed *= -1        
         
      self.rect.center = (ncx,ncy)
   
   def switch_frame(self, frame = None):
      if frame == None:
         self.frame += 1
      else:
         self.frame = frame
      if(self.frame >= self.numframe) :
         self.frame = 0
         
      if self.activedivide > 0 and self.activedivide <= 5:
         if(self.origwidth == self.image.get_rect().width):
            oldcenter = self.rect.center;
            newimg = pygame.Surface((self.origwidth*2, self.origheight), SRCALPHA)
            self.image = newimg
            self.rect = self.image.get_rect()
            self.rect.center = oldcenter
            
         #do anime stuffage
         self.image.fill((0,0,0,0))
         offset = self.origwidth * self.frame
         showwidth = (self.origwidth/2) + \
            (((self.origwidth/2)*(float(self.activedivide)/5.0)))
         leftx = self.origwidth-showwidth
         rightx = self.origwidth
         hgt = self.origheight
         #print showwidth
         self.image.blit(self.src, (leftx, 0), (offset,0,showwidth,hgt))
         self.image.blit(self.src, (rightx,0), (offset+leftx,0,showwidth,hgt))
      else:
         #reset size if ending
         if(self.origwidth != self.image.get_rect().width):
            oldcenter = self.rect.center
            self.rect.width = self.origwidth
            self.rect.center = (oldcenter[0]+8,oldcenter[1])
         
         w = self.origwidth
         self.image = self.src.subsurface((w*self.frame,0,w,self.origheight))
         
class Simulator:
   def pre_load_images(self):
      """ Loads images used by the game."""
      for huename in playerhues:
         for variant in huevariants:
            for type in celltypes:
               for sat in range (10,110,10):
                  key = "{}-{}-{}-{}".format(huename,variant,type,sat)
                  hue = playerhues[huename]
                  file = celltypes[type]
                  if key not in system_images:
                     system_images[key] = loadcellgraphic.load_cell(file, hue + huevariants[variant], sat)

   def pre_load_blanks(self):
      """ Loads blank image for use on the server, adjust this as necessary to
         make the server work. """
      im = pygame.Surface((16,16))
      for huename in playerhues:
         for variant in huevariants:
            for type in celltypes:
               for sat in range (10,110,10):
                  key = "{}-{}-{}-{}".format(huename,variant,type,sat)
                  system_images[key] = im

   def __init__(self, size, clientMode = False):
      """ Inits the GameAction, can optionally autoload a level."""
      
      self.surface = pygame.Surface(size, SRCALPHA)
      
      if clientMode:
         self.pre_load_images()
      else:
         self.pre_load_blanks()

      self.clientMode = clientMode
      random.seed()

      self.players = {}

      # Used serverside
      self.running = False
      self.start_locations = [(50,50), (50, 350), (350,50), (350,350)]

      self.begindivide = 5000
      self.timedivide = 1000

      self.simulationImage = pygame.image.load(os.path.join('sprites', 'ui', '049_A_Texture.jpg')).convert()

   def add_player(self, id):
      hue = random.choice(playerhues.keys())
      org_type = random.choice(cellfcounts.keys())
      start_loc = random.choice(self.start_locations)
      g2g = False

      # Find some 
      while not g2g:
         for p in self.players:
            if self.players[p].type == org_type:
               org_type = random.choice(cellfcounts.keys())
               break
            elif self.players[p].huename == hue:
               hue = random.choice(playerhues.keys())
               break
            elif self.players[p].mainpoint == start_loc:
               start_loc = random.choice(self.start_locations)
               break
         else:
            g2g = True

      self.players[id] = Player(id, org_type, hue, start_loc, self)
      
   def start(self):
      #Inform the players of their opponents and spawn starting mobbies
      for i in self.players:
         if not self.clientMode:
            self.players[i].spawn_initial(10)

         for x in self.players:
            if x != i:
               self.players[i].opponents.append(self.players[x])         

   def update(self, ticktime, screensurface):
      """ Updates the simulator based on the amount of time specified in 
      ticktime """
      
      statusrec = "this could carry a win or lose notice or something."
      
      self.begindivide -= ticktime
      if(self.begindivide < 0) :
         self.timedivide -= ticktime

      players = self.players

      for p in players:
         if self.timedivide < 0:
            players[p].activedivide = 0
         elif self.timedivide < 1000:
            players[p].activedivide = 5 - math.floor((float(self.timedivide)/1000.0)*5)
         players[p].sprites.update(ticktime, self)
        
      #do splitting.
      if self.clientMode == False:
         #collisions
         if len(players) > 1:
            for p in players:
               mark = []

               for sprite in players[p].sprites.sprites():
                  lst = pygame.sprite.spritecollide(sprite, players[p].opponents[0].sprites, False)

                  for jerk in lst:
                     if jerk.player.sprite_stats.get_defense() > players[p].sprite_stats.get_defense():
                        jerk.energy -= players[p].sprite_stats.get_defense()
                        mark.append(sprite)
                     else:
                        sprite.energy -= jerk.player.sprite_stats.get_defense()
                        mark.append(jerk)

               for sprite in mark:
                  sprite.player.kill_sprite(sprite)

         if self.timedivide < 0:
            self.begindivide = 5000
            self.timedivide = 1000

            for p in players:
               len_sprites = len(players[p].sprites.sprites())

               if len_sprites < players[p].popcap:
                  toadd = []
                  slist = players[p].sprites.sprites()

                  for sprite in slist:
                     centerx = sprite.rect.x + (sprite.origwidth*1.5);
                     centery = sprite.rect.center[1];

                     toadd.append((centerx,centery))

                     len_sprites += 1

                     if len_sprites >= players[p].popcap:
                        break

                  for center in toadd:
                     players[p].add_sprite(center[0],center[1])

      else:
         self.surface.blit(self.simulationImage, (0,0))
         
         for p in self.players:
            self.players[p].sprites.draw(self.surface)         

      for p in players:
         players[p].enforce_popcap()

      return statusrec
