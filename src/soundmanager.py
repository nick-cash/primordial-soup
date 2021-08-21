import pygame, sys,os,time,math,random
from pygame.locals import *

musicon = True
activesong = ""
activeloops = -1
soundman_haveinit = 0

#song files:
# title: music.ogg
# game: LD24tune1.ogg

def toggle_music():
   """ Designed for use as a menu callback, turns off and restarts music."""
   global activesong
   global activeloops
   global musicon
   
   if musicon == False:
      musicon = True
      if activesong != "":
         pygame.mixer.music.load(os.path.join("distmusic", activesong))
         pygame.mixer.music.play(activeloops)
   else :
      musicon = False
      pygame.mixer.music.stop()
   return "dont-do-anything"

def sound_init():
   """ Sets up pygame mixer """
   global soundman_haveinit
   if soundman_haveinit == 0:
      pygame.mixer.pre_init(44100, -16, 2, 4096)
      pygame.mixer.init()
      soundman_haveinit = 1

def load_and_play_song(songfile = "", loops = -1):
   """ Loads a song and sets it to play a specified number of loops. 
   Empty string to stop music. -1 loops for indefinite playing. """
   global activesong
   global activeloops
   #so we don't reload the same song.
   if activesong != songfile:
      activesong = songfile
      activeloops = loops
      if musicon:
         if activesong != "":
            pygame.mixer.music.load(os.path.join("distmusic", activesong))
            pygame.mixer.music.play(activeloops)
         else:
            pygame.mixer.music.stop()
