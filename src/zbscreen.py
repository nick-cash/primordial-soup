import pygame, sys,os,time,math,random
from pygame.locals import *

class ZbScreen() :
   """ Base screen class, expand """
   def __init__(self):
      """ Default screen constructor, creates a new clock """
      self.clock = pygame.time.Clock();
      self.req_fps = 60
      self.accumulated_time = 0
      self.paused = False
      self.lasttime = 0;
      self.clock_tick()
      self.default_event_handler = None

   def pause_clock(self):
      """ Pause this screen's clock, basically tells update
       to ignore ticks """
      self.paused = True

   def unpause_clock(self):
      self.clock_tick()
      self.paused = False
      self.clock_tick()

   def clock_tick(self):
      """ Runs the screen's clock tick and updates accumulated time """
      millesecond = self.clock.tick(self.req_fps)

      if self.paused :
         self.accumulated_time = self.accumulated_time
      else :
         self.lasttime = self.accumulated_time
         self.accumulated_time += millesecond
 

   def input(self, events):
      """ Input function to override, call self.default_event_handler 
      if it is not None for events you don't want to handle."""
      for event in events :
         if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit(0)
         else :
            if self.default_event_handler != None :
               self.default_event_handler([event])

   def update(self, screensurface):
      """ Convenient hook to plug screen updates into,
      doesn't actually do anything without being overridden,
      remember to call clock tick in your update implementation,
      pass it your screen surface for the drawatage.  Return some
      game specific logic for switching or ending or what have you."""
      self.clock_tick();
      #handle input
      self.input(pygame.event.get())
      #Do stuff with the screensurface here and stuff!

      #return something!
      return 0