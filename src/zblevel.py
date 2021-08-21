# Level loading code
# Game object code may temporarily be here

import xml.parsers.expat, os, pygame

class ZbObject(pygame.sprite.Sprite):
      def __init__(self, img, x, y):
         pygame.sprite.Sprite.__init__(self)

         self.image = img
         self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())

class ZbTile(ZbObject):
   def __init__(self, img, x, y, gid=0):
      ZbObject.__init__(self, img, x, y)

      # Optional
      self.gid = gid

class ZbLevel() :
   """ Contains all information related to a level, including
       its freshly loaded state, file information, and current play information """
   
   def __init__(self, filename, directory='levels'):
      """ Initialize and load a level object. """

      # Width in tiles
      self.width = 0

      # Height in tiles
      self.height = 0

      # Width -of- tiles
      self.tile_width = 0

      # Height -of- tiles
      self.tile_height = 0

      # Level properties
      self.properties = {}

      # Defined objects
      self.objects = []

      # Tilesets
      self.tilesets = []

      # Individual subsurfaces of the tileset keyed with gid
      self.tile_images = {}

      # Layers of tiles. 
      self.tile_layers = []
      self.rendered_tile_layers = []

      # Used as static variables for loading... don't touch
      self.loading_object = False
      self.rect = pygame.Rect(0,0,0,0)

      ###

      self.filename = os.path.join(directory, filename + '.tmx')
      self.load()

   def load(self):
      """ Load a level file. """

      p = xml.parsers.expat.ParserCreate()
      p.StartElementHandler = self.start_element_handler
      p.EndElementHandler = self.end_element_handler

      with open(self.filename) as f:
         p.ParseFile(f)

   def start_element_handler(self, name, attrs):
      """ Set level data and create relevant objects. """

      if name == 'map':
         self.width = int(attrs['width'])
         self.height = int(attrs['height'])
         self.tile_width = int(attrs['tilewidth'])
         self.tile_height = int(attrs['tileheight'])

      # Add property to the most recent element's object.
      # This is relevant for the top level map and objects in object sets.
      elif name == 'property':
         if self.loading_object:
            self.objects[-1]['properties'][attrs['name']] = attrs['value']
         else:
            self.properties[attrs['name']] = attrs['value']

      elif name == 'tileset':
         attrs['tilewidth'] = int(attrs['tilewidth'])
         attrs['tileheight'] = int(attrs['tileheight'])
         attrs['firstgid'] = int(attrs['firstgid'])

         self.tilesets.append(attrs)

      # Add image to the latest tileset
      elif name == 'image':
         self.tilesets[-1]['image'] = attrs

         filename = os.path.join('sprites', attrs['source'].split('/')[-1])

         image = pygame.image.load(filename).convert()
         image.set_colorkey(pygame.Color('#' + str(attrs['trans'])))

         x = y = 0
         twidth = self.tilesets[-1]['tilewidth']
         theight = self.tilesets[-1]['tileheight']
         gid = self.tilesets[-1]['firstgid']

         while y < image.get_height():
            timage = image.subsurface(pygame.Rect(x,y,twidth,theight))

            self.tile_images[gid] = timage

            # Move our offsets. If we hit the side of the image, move to the next row
            x += twidth

            if x >= image.get_width():
               x = 0
               y += theight

            gid += 1

      # Add a new layer to the end
      elif name == 'layer':
         self.tile_layers.append(pygame.sprite.Group())

         # Zero out cooridinates we can use when adding tiles and
         # calculate the pixel size of the level so we know where the edges are
         self.rect = pygame.Rect(0,0, \
                                 (self.tile_width * int(attrs['width'])), \
                                 (self.tile_height * int(attrs['height'])))

      # Add tile to the latest layer
      elif name == 'tile':
         gid = int(attrs['gid'])
         
         x = self.rect.left
         y = self.rect.top

         # gid of 0 is a blank square, anything else is a tile
         if gid > 0:
            spr = ZbTile(self.tile_images[gid], x, y, gid)
            self.tile_layers[-1].add(spr)

         # Move offsets
         self.rect.left += self.tile_width

         if self.rect.left >= self.rect.width:
            self.rect.left = 0
            self.rect.top += self.tile_height

      elif name == 'object':
         self.loading_object = True

         attrs['properties'] = {}
         self.objects.append(attrs)

   def end_element_handler(self, name):
      """ Pop the current element we are handling off the stack. """

      if name == 'object':
         self.loading_object = False

      elif name == 'layer':
         trans_color = pygame.Color('#ff00ff')

         # Make new surface, draw the layer, and save it
         rendered_layer = pygame.Surface((self.rect.width, self.rect.height)).convert()
         rendered_layer.fill(trans_color)
         rendered_layer.set_colorkey(trans_color)

         self.tile_layers[-1].draw(rendered_layer)
         self.rendered_tile_layers.append(rendered_layer)