import pygame, sys, os
from pygame.locals import *

pygame.font.init()

def load_font(name, size, bold=False, italic=False):
   font = None

   # Attempt to load system fonts first, then local
   path = pygame.font.match_font(name, bold, italic)

   if path:
      font = pygame.font.Font(path)
   else:
      path = os.path.join('fonts', name)
      font = pygame.font.Font(path, size)

   return font