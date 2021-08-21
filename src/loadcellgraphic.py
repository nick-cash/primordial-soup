import pygame, sys,os,time,math,random
from pygame.locals import *

def load_cell(imagefile, hue, sat) :
   """ SLOW loads an image, resets hue/sat for each pixel, should preserve alpha. """
   image = pygame.image.load(os.path.join('sprites', imagefile)).convert_alpha()
   srect = image.get_rect();
   x = 0
   y = 0
   newsurface = pygame.Surface( (srect.width, srect.height), SRCALPHA )
   image.lock()
   newsurface.lock()
   pa = pygame.PixelArray(newsurface)
   pi = pygame.PixelArray(image)
   for x in range(0, srect.width - 1) :
      for y in range(0, srect.height -1) :
         incolor = image.unmap_rgb(pi[x][y])
         [H, S, V, A] = incolor.hsva
         incolor.hsva = (int(hue), int(sat), int(V), int(A))
         
         pa[x][y] = (incolor.r, incolor.g, incolor.b, incolor.a)
   image.unlock()
   newsurface.unlock()
   return newsurface