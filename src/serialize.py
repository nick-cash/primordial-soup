from simulator import Traits

# Take server data and pack it for the client
# Should return tuples
def serialize_player(p, sim):
   data = {}
   player = sim.players[p.id]

   data.update({"type": player.type, "huename": player.huename})
   data.update({"action": player.action})
   data.update({"mainpoint": player.mainpoint})
   data.update({"activedivide": player.activedivide})
   data.update({"sprite_stats": player.sprite_stats.get_stats()})
   data.update({"sprites": dict({s.id: serialize_sprite(s, sim) for s in player.sprites.sprites()})})

   return data

def serialize_sprite(sprite, sim):
   data = {}

   data.update({"xspeed": sprite.xspeed, "yspeed": sprite.yspeed})
   data.update({"stx": sprite.stx, "sty": sprite.sty})
   data.update({"start_of_life": sprite.start_of_life})
   data.update({"energy": sprite.energy})
   data.update({"center": (sprite.rect.centerx, sprite.rect.centery)})

   return data

def unserialize_players(data, sim):
   for pid in data['pdata']:
      if not pid in sim.players.keys():
         sim.add_player(pid)

      for attr in data['pdata'][pid]:
         if attr == "sprites":
            pass
            unserialize_sprites(data['pdata'][pid]['sprites'], sim.players[pid], sim)
         elif attr == "sprite_stats":
            sim.players[pid].sprite_stats = Traits(data['pdata'][pid]['type'], data['pdata'][pid][attr])
         else:
            setattr(sim.players[pid], attr, data['pdata'][pid][attr])

def unserialize_sprites(data, player, sim):
   # Set attributes or create as necessary
   for sid in data:
      if not player.sprite_dict.has_key(sid):
         spr = player.add_sprite(data[sid]['center'][0], data[sid]['center'][1])
         spr.id = sid
      else:
         spr = player.sprite_dict[sid]

      for attr in data[sid]:
         if attr == "center":
            spr.rect.center = (data[sid]["center"][0], data[sid]["center"][1])
         else:
            setattr(spr, attr, data[sid][attr])
   
   # Kill any leftovers
   mark = []
   for sprite in player.sprites.sprites():
      if not data.has_key(sprite.id):
         mark.append(sprite)

   for sprite in mark:
      player.kill_sprite(sprite)
