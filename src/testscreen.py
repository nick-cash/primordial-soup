import pygame, sys,os,time,math,random,copy
import zbscreen, zblevel,loadcellgraphic,simulator
from pygame.locals import *
from client import *
from loadfont import *

class Button:
   def __init__(self, id, normal_surface, active_surface, pos, callback):
      self.normal_surface = normal_surface
      self.active_surface = active_surface
      self.pos = pos
      self.callback = callback
      self.active = False
      self.id = id

   def get_rect(self):
      return self.normal_surface.get_rect().move(self.pos)

   def render(self, surface):
      if self.active:
         surface.blit(self.active_surface, self.pos)
      else:
         surface.blit(self.normal_surface, self.pos)

class TestScreen(zbscreen.ZbScreen) :
   def __init__(self, firstlvl = None) :
      """ Inits the GameAction, can optionally autoload a level."""
      zbscreen.ZbScreen.__init__(self)
      self.req_fps = 40

      self.simulator = simulator.Simulator((720, 604), True)
      self.backgroundImage = pygame.image.load(os.path.join('sprites', 'ui', 'dark_mosaic.png')).convert_alpha()
      self.controlImage = pygame.image.load(os.path.join('sprites', 'ui', 'UI-Concept_01.png')).convert_alpha()
      self.headerImage = pygame.image.load(os.path.join('sprites', 'ui', 'UI-Concept_02.png')).convert_alpha()
      self.simulatorBorderImage = pygame.image.load(os.path.join('sprites', 'ui', 'UI-Concept_03.png')).convert_alpha()
      self.statusImage = pygame.image.load(os.path.join('sprites', 'ui', 'UI-Concept_04.png')).convert_alpha()
      self.plusImage = pygame.image.load(os.path.join('sprites', 'plus.png')).convert_alpha()
      self.buttonImage = pygame.image.load(os.path.join('sprites', 'button-big.png')).convert_alpha()      

      self.font_lato = load_font(os.path.join('lato','Lato-Bold.ttf'), 32)
      self.font_lato_small = load_font(os.path.join('lato','Lato-Bold.ttf'), 24)
      self.font_lato_tiny = load_font(os.path.join('lato', 'Lato-Bold.ttf'), 16)
      self.font_countdown = load_font(os.path.join('lato','Lato-Black.ttf'), 60)

      self.gg = False

      # BUTTONS
      self.buttons = {}

      self.activeImage = pygame.Surface((25,25))
      self.activeImage.fill((255,0,0))

      self.make_button(1, "Health", (45,50), 'button_test')
      self.make_button(2, "", (150,54), 'button_evolve', self.plusImage, self.activeImage)

      self.make_button(3, "Comms", (45,100), 'button_test')
      self.make_button(4, "", (150,104), 'button_evolve', self.plusImage, self.activeImage)

      self.make_button(5, "Aggro", (45,150), 'button_test')
      self.make_button(6, "", (150,154), 'button_evolve', self.plusImage, self.activeImage)

      self.make_button(7, "Speed", (45,200), 'button_test')
      self.make_button(8, "", (150,204), 'button_evolve', self.plusImage, self.activeImage)

      self.make_button(9, "Defense", (45,250), 'button_test')
      self.make_button(10, "", (150,254), 'button_evolve', self.plusImage, self.activeImage)

      self.client = None
      self.background = None
      self.static_ui = None

   def make_button(self, id, text, pos, cb, img=None, active=None):
      if not img:
         img = self.buttonImage.copy()
         rtext = self.font_lato_tiny.render(text, True, (0,0,0))

         img.blit(rtext, (12,7))

      if not active:
         self.buttons[id] = Button(id, img, img, pos, cb)
      else:
         self.buttons[id] = Button(id, img, active, pos, cb)

   def button_test(self, button):
      pass

   def button_evolve(self, button):
      if button.id == 2:
         self.client.SendStatUpdate("health")
      elif button.id == 4:
         self.client.SendStatUpdate("comms")
      elif button.id == 6:
         self.client.SendStatUpdate("aggro")
      elif button.id == 8:
         self.client.SendStatUpdate("speed")
      else:
         self.client.SendStatUpdate("defense")

   def check_button(self, button, pos):
      if button.get_rect().collidepoint(pos):
         button.active = True
         getattr(self, button.callback)(button)

   def check_button_release(self, button, pos): 
      if button.active:
         button.active = False

   def input(self, events):
      """ Input function to override, call self.default_event_handler 
      if it is not None for events you don't want to handle."""
      ret = 0

      for event in events :
         if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            global quit
            quit.value = 1
            ret = "exit-game"
         elif (event.type == KEYUP) and (event.key == K_r):
            self.client.SendReady()
         elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            for i in self.buttons:
               self.check_button(self.buttons[i], event.pos)
         elif event.type == MOUSEBUTTONUP and event.button == 1:
            for i in self.buttons:
               self.check_button_release(self.buttons[i], event.pos)
         else:
            if self.default_event_handler != None :
               self.default_event_handler([event])

         return ret

   def draw_background(self, surface):
      if self.background:
         surface.blit(self.background, (0,0))
      else:
         backgroundSize = self.backgroundImage.get_size()
         self.background = pygame.Surface((surface.get_width(), surface.get_height()))
         x = 0
         y = 0

         while True:
            self.background.blit(self.backgroundImage, (x, y))
            x += backgroundSize[0]
            
            if x >= self.background.get_width():
               y += backgroundSize[1]
               x = 0
            if y >= self.background.get_height():
               break

         surface.blit(self.background, (0,0))

   def draw_static_ui(self, surface):
      if self.static_ui:
         surface.blit(self.static_ui, (0,0))
      else:
         margin_top = 5
         margin_left = 5

         static_ui = pygame.Surface((surface.get_width(), surface.get_height()))
         self.draw_background(static_ui)

         static_ui.blit(self.controlImage, (margin_left, margin_top))
         static_ui.blit(self.headerImage, (margin_left + self.controlImage.get_width(), margin_top))
         static_ui.blit(self.statusImage, (margin_left, margin_top + self.controlImage.get_height()))

         self.static_ui = static_ui

         surface.blit(static_ui, (0,0))

   def draw_ui(self, surface):
      self.draw_static_ui(surface)

      for i in self.buttons:
         self.buttons[i].render(surface)

      if self.client:
         if self.gg:
            rtext = self.font_lato.render("GAME OVER", True, (240, 240, 240))
            surface.blit(rtext, (450,35))

         # Draw the countdown
         if self.client.game_state == "countdown":
            rendered_message = self.font_countdown.render("Get Ready!", True, (240, 240, 240))

            text = "%.2f" % self.client.countdown
            rendered_numbers = self.font_countdown.render(text, True, (240, 240,240))

            surface.blit(rendered_message, (surface.get_width() - 525, surface.get_height() - 450))
            surface.blit(rendered_numbers, (surface.get_width() - 450, surface.get_height() - 375))
         # Draw the clocks
         elif self.client.game_state == "running":
            minutes = math.floor(self.client.game_data["time_remaining"] / 60000)
            seconds = math.floor((self.client.game_data["time_remaining"] - (60000 * minutes)) / 1000)

            t = "%2d:%02d" % (minutes, seconds)

            rendered_clock = self.font_lato.render(t, True, (240,240,240))
            surface.blit(rendered_clock, (850, 30))

            ###
            text = "%.2f" % (self.client.game_data["round_time"] / 1000.0)
            rendered_numbers = self.font_lato.render(text, True, (240, 240,240))
            surface.blit(rendered_numbers, (75, 350))
         # Tell them how to say they are ready
         else:
            col = (240,240,240)
            num_connected = "{} players are connected.".format(len(self.client.players))
            num_ready = "{} players are ready to begin.".format(self.client.NumPlayersReady())
            t = "Press 'R' when you are ready to play."

            rnum_connected = self.font_lato_small.render(num_connected, True, col)
            rnum_ready = self.font_lato_small.render(num_ready, True, col)
            rt = self.font_lato.render(t, True, col)

            surface.blit(rt, (350, 375))
            surface.blit(rnum_connected, (450, 425))
            surface.blit(rnum_ready, (425, 455))

   def update(self, surface):
      """ Convenient hook to plug screen updates into,
      doesn't actually do anything without being overridden,
      remember to call clock tick in your update implementation,
      pass it your screen surface for the drawatage.  Return some
      game specific logic for switching or ending or what have you."""
      self.clock_tick()

      # Check network
      self.client.Update()

      if self.client.new_data:
         self.simulator.timedivide = self.client.game_data["simdata"]["timedivide"]
         self.simulator.begindivide = self.client.game_data["simdata"]["begindivide"]

         unserialize_players(self.client.game_data, self.simulator)

         if self.client.game_data['time_remaining'] < 0:
            self.gg = True

         self.client.new_data = False

      # Handle input & Game Update
      statusrec = self.input(pygame.event.get())

      if not connection.isConnected:
         return "exit-game"

      # Draw
      self.draw_ui(surface)

      if self.client.game_state == "running":
         self.simulator.update(self.accumulated_time - self.lasttime, surface)
         surface.blit(self.simulator.surface, (235, 105))
         surface.blit(self.simulatorBorderImage, (5 + self.controlImage.get_width(), 5  + self.headerImage.get_height()))

      return statusrec
