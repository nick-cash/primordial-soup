import pygame, sys, os, time, math, random
import zbscreen
import menus
import loadcellgraphic
import testscreen
import subprocess
import soundmanager

from client import *
from pygame.locals import *

def default_event_handler(events):
   for event in events :
      if event.type == QUIT:
         sys.exit(0)

def launch_server():
   pid = subprocess.Popen([sys.executable, "server.py", "stand-alone"]).pid
   return "server-started"

def start_game():
   testa.client = Client("localhost", 3000)
   testa.simulator.start()
   return "switch-to-test"

if __name__ == '__main__':
   pygame.init()
   window = pygame.display.set_mode((972, 728))
   pygame.display.set_caption('Primordial Soup')
   screensurface = pygame.display.get_surface()

   # Loading screen
   splash = pygame.image.load('splash.png').convert()
   screensurface.blit(splash, (0,0))
   pygame.display.flip()

   soundmanager.sound_init()
   soundmanager.load_and_play_song('music.ogg',-1)

   # Menus
   connect = menus.MenuEntry('Connect')
   connect.callback = start_game;
   
   start_server = menus.MenuEntry('Start Server')
   start_server.callback = launch_server;

   exit = menus.MenuEntry('Exit')
   exit.callback = lambda : "exit-game";

   return_to_game = menus.MenuEntry('Return to Game')
   return_to_game.callback = lambda : "switch-to-game";

   toggle_music = menus.MenuEntry('Toggle Music')
   toggle_music.callback = soundmanager.toggle_music
   
   bg = pygame.image.load(os.path.join('sprites', 'main-menu-bg.jpg')).convert()
   menu_bg = pygame.image.load(os.path.join('sprites', 'main-menu-bg.png')).convert_alpha()

   mainmenu = menus.MenuScreen([connect, start_server, toggle_music, exit], bg, menu_bg, 375, "Primordial Soup");
   pausemenu = menus.MenuScreen([return_to_game, toggle_music, exit], bg, menu_bg, 375, "Primordial Soup");

   currentscreen = mainmenu;
   mainmenu.default_event_handler = default_event_handler

   testa = testscreen.TestScreen();
   testa.default_event_handler = default_event_handler
   testa.pause_clock()

   while True:
      status = currentscreen.update(screensurface)
      pygame.display.flip()
 
      if status == "switch-to-test":
         soundmanager.load_and_play_song('LD24tune1.ogg', -1)
         currentscreen = testa
         testa.unpause_clock()
      elif status == "switch-to-pause":
         currentscreen = pausemenu
      elif status == "exit-game":
         pygame.quit()
         sys.exit(0)
