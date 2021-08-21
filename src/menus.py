import pygame, sys,os,time,math,random
import zbscreen

from pygame.locals import *
from loadfont import load_font

main_menu_font = load_font(os.path.join('lato','Lato-Black.ttf'), 32)
big_ass_font = load_font(os.path.join('lato','Lato-Black.ttf'), 128)
main_menu_sprite = pygame.image.load(os.path.join('sprites', "menuselect.png"))

class MenuEntry() : 
   def __init__(self, text = 'Unentered') :
      """ Init a menu entry, text attribute sets what to do, callback
      is a function to run."""
      self.text = text
      self.normalimage = None
      self.activeimage = None
      self.callback = None
      self.X = None
      self.Y = None
      self.rect = pygame.Rect(0,0,2,2) 
         #current rendered location, update for the menu has to set this.
      self.render_images()
 
   def update_text(self, text) :
      """ Updates the text and regenerates the text images."""
      self.text = text
      self.render_images()
 
   def render_images(self) :
      """ Render our menu images. """
      self.normalimage = main_menu_font.render(self.text, True, (240, 240,240))
      nrect = self.normalimage.get_rect()
      srect = main_menu_sprite.get_rect()
      self.activeimage = pygame.Surface((nrect.width + \
         srect.width+ 3, nrect.height), SRCALPHA)
      self.activeimage.blit(self.normalimage, \
         (srect.width+3, 0))
      self.activeimage.blit(main_menu_sprite, (0,0))

class MenuScreen(zbscreen.ZbScreen) :
   def __init__(self, menu_entries, background_surface = None, menu_bg_surface = None, vertical_start = 200, title=""):
      zbscreen.ZbScreen.__init__(self)
      self.background = None

      self.title = title
      self.title_image = None

      if background_surface != None :
         self.background = background_surface

      self.menu_bg = menu_bg_surface

      self.vertical = vertical_start
      self.entries = menu_entries
      self.active_index = 0
      self.sprite_width = main_menu_sprite.get_rect().width
      self.message = None
      self.messageX = 0
      self.messageY = 0

   def input(self, events):
      """ Input function to override, call self.default_event_handler 
      if it is not None for events you don't want to handle."""
      for event in events :
         if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit(0)
         elif event.type == KEYUP:
            if event.key == K_DOWN :
               self.active_index += 1
               if self.active_index >= len(self.entries) :
                  self.active_index = len(self.entries) - 1;
            elif event.key == K_UP :
               self.active_index -= 1
               if self.active_index < 0 :
                  self.active_index = 0
            elif event.key == K_RETURN :
               if self.entries[self.active_index].callback != None:
                  return self.entries[self.active_index].callback()
         elif event.type == MOUSEMOTION :
            count = 0
            for entry in self.entries :
               if(entry.rect.collidepoint(event.pos)) :
                  self.active_index = count
               count += 1
         elif event.type == MOUSEBUTTONUP :
            count = 0
            for entry in self.entries :
               if(entry.rect.collidepoint(event.pos)) :
                  if self.entries[self.active_index].callback != None:
                     return self.entries[self.active_index].callback()
               count += 1 
         else :
            if self.default_event_handler != None :
               self.default_event_handler([event])
         return 0

   def update(self, screensurface):
      """ Updates the menu screen, draws the menu, calls input handling, and the like. """
      self.clock_tick();
      #handle input
      retval = self.input(pygame.event.get())
      #Do stuff with the screensurface here and stuff!
      screensurface.fill((0,0,0))

      if self.background != None :
         screensurface.blit(self.background, (0,0))

      if self.menu_bg != None:
         screensurface.blit(self.menu_bg, ((screensurface.get_width()/2) - self.menu_bg.get_width()/2, \
            (self.vertical - 50)))

      if len(self.title) > 0:
         if not self.title_image:
            self.title_image = big_ass_font.render(self.title, True, (200,200,200))

         screensurface.blit(self.title_image, ((screensurface.get_width()/2 - self.title_image.get_width()/2, 80)))
 
      currenty = self.vertical
      s = screensurface.get_rect()
 
      count = 0
      for entry in self.entries :
         if(self.active_index == count) :
            cx = math.floor(s.width/2 - entry.activeimage.get_rect().width/2 \
               - self.sprite_width/2 - 1.5) #centerish the menu image
            if entry.X != None :
               cx = entry.X
            if entry.Y != None :
               currenty = entry.Y
            screensurface.blit(entry.activeimage, (cx,currenty))
            entry.rect = entry.activeimage.get_rect()
            entry.rect.x = cx
            entry.rect.y = currenty
            currenty += entry.activeimage.get_rect().height + 5
         else :
            cx = math.floor(s.width/2 - entry.normalimage.get_rect().width/2)
            #center the menu image
            
            if entry.X != None :
               cx = entry.X
            if entry.Y != None :
               currenty = entry.Y      
            screensurface.blit(entry.normalimage, (cx,currenty))
            entry.rect = entry.normalimage.get_rect()
            entry.rect.x = cx
            entry.rect.y = currenty 
            currenty += entry.normalimage.get_rect().height + 5
         count += 1
         
      if self.message != None :
         screensurface.blit(self.message, (self.messageX, self.messageY))
      #return value reported by the input handler
      return retval