# LD24 Simulation Server
import sys, pygame
from random import randint
from weakref import WeakKeyDictionary

from pygame.locals import *
from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from simulator import *
from serialize import *

class ServerChannel(Channel):
   """
   This is the server representation of a single connected client.
   """
   def __init__(self, *args, **kwargs):
      Channel.__init__(self, *args, **kwargs)
      self.id = str(self._server.NextId())
      self.ready = False

      self.latency = 0
      self.ping_out = 0
        
   def Close(self):
      self._server.DelPlayer(self)
   
   ##################################
   ### Network specific callbacks ###
   ##################################

   def Network_statupdate(self, data):
      self._server.input_commands[self.id] = data['stat']
   
   def Network_ready(self, data):
      if not self._server.game_in_progress:
         self.ready = not self.ready

         data.update({"ready": self.ready})
         data.update({"id": self.id})
         data.update({"action": "player_ready"})
         self._server.SendToAll(data)

         print("Player {} {} ready.".format(self.id, ("is" if self.ready else "is not")))

   def Network_player_input(self, data):
      data.update({"id": self.id})
      data.update({"recieved": self._server.time - self.latency})
      self._server.input_commands.append(data)

   def Network_ping(self, data):
      self.latency = self._server.time - self.ping_out

class LD24Server(Server):
   channelClass = ServerChannel
   
   def __init__(self, *args, **kwargs):
      self.id = 0
      Server.__init__(self, *args, **kwargs)
      self.players = WeakKeyDictionary()
      self.max_players = 2
      self.clock = pygame.time.Clock()
      self.input_commands = {}
      self.simulator = None

      self.Reset()

      # Reset per game
      print 'Server launched'
   
   def NextId(self):
      self.id += 1
      return self.id

   # Run game physics
   def UpdateGame(self):
      if self.simulator.running:
         if self.time >= self.round_end:
            self.process_round = True
            self.round_end = self.time + 5000

         if self.curr_time == 0 or self.last_time == 0:
            self.simulator.update(10,None)
         else:
            self.simulator.update(self.curr_time - self.last_time, None)

   # Manage networked i/o
   def UpdateNetwork(self):
      data = {}

      if self.game_in_progress:
         if self.time < self.game_start_countdown:
            self.SendToAll({"action": "countdown", "time_remaining": (self.game_start_countdown-self.time)})
         else:              
            if not self.simulator.running:
               self.simulator.running = True
               self.simulator.start()

               self.round_end = self.time + 5000
               self.process_round = False

            # Generate stuff to send.
            data.update({"action": "update"})
            data.update({"simdata": {"begindivide": self.simulator.begindivide, "timedivide": self.simulator.timedivide}})

            # Process all events in the input command queue
            if self.process_round:
               for pid in self.input_commands.keys():
                  if self.input_commands[pid] == "health":
                     self.simulator.players[pid].sprite_stats.energy += 1
                  elif self.input_commands[pid] == "comms":
                     self.simulator.players[pid].sprite_stats.comms += 1
                  elif self.input_commands[pid] == "aggro":
                     self.simulator.players[pid].sprite_stats.aggro += 1
                  elif self.input_commands[pid] == "speed":
                     self.simulator.players[pid].sprite_stats.speed += 1
                  elif self.input_commands[pid] == "defense":
                     self.simulator.players[pid].sprite_stats.defense += 1

               self.process_round = False

            data.update({"pdata": dict({p.id: serialize_player(p, self.simulator) for p in self.players})})

            #Add the time
            data.update({"time_remaining": self.game_end - self.time})
            data.update({"round_time": self.round_end - self.time})

      for player in self.players:
         if data:
            player.Send(data)

   def Connected(self, channel, addr):
      if len(self.players) < self.max_players:
         self.AddPlayer(channel)
      else:
         channel.Send({"action": "server_full"})
         print "Connection down connection because server is full"
   
   def AddPlayer(self, player):
      print "New Player" + str(player.addr)
      self.players[player] = True
      self.SendPlayers()
      self.SendPing(player)
   
   def DelPlayer(self, player):
      if self.players.has_key(player):
         print "Deleting Player" + str(player.addr)
         del self.players[player]

         if len(self.players) > 0:
            self.SendPlayers()
         else:
            self.Reset()
   
   def Reset(self):
      self.id = 0

      self.game_in_progress = False
      self.last_time = 0
      self.game_end = 0
      self.game_start_countdown = 0
      self.last_sim_time = 0

      self.last_time = 0
      self.curr_time = 0

      self.process_round = False
      self.round_end = 0

      if self.simulator:
         del self.simulator

      self.simulator = Simulator((720, 604), False)

   def SendPlayers(self):
      self.SendToAll({"action": "players", "players": dict([[p.id, p.ready] for p in self.players])})
   
   def SendToAll(self, data):
      [p.Send(data) for p in self.players]

   def SendPing(self, player):
      player.ping_out = self.time
      player.Send({"action": "ping", "id": player.id})
   
   def Launch(self):
      while True:
         self.Pump()
         self.time = pygame.time.get_ticks()

         for event in pygame.event.get():
            if (event.type == QUIT) or (event.type == KEYDOWN and event.key == K_ESCAPE):
               pygame.quit()
               sys.exit()

         if (not self.game_in_progress) or (self.process_network >= 3):
            self.process_network = 0
            self.UpdateNetwork()
         else:
            self.process_network += 1

         # Is the game running? If not, can we start it?
         if not self.game_in_progress:
            if len(self.players) == self.max_players:
               all_ready = True

               for p in self.players:
                  if not p.ready:
                     all_ready = False

               if all_ready:
                  self.game_in_progress = True
                  self.game_start_countdown = pygame.time.get_ticks() + 2000
                  self.game_end = self.game_start_countdown + 60000 # 1 minute

                  # Add players
                  for p in self.players:
                     self.simulator.add_player(p.id)
               else:
                  self.clock.tick(10)
         else:
            self.UpdateGame()
            ms = self.clock.tick(60)
            self.last_time = self.curr_time
            self.curr_time += ms

# Lets do it
host = "localhost"
port = 3000

if len(sys.argv) >= 3:
   host = sys.arg[1]
   port = int(sys.arg[2])

pygame.init()
screen = pygame.display.set_mode((320,240))
pygame.display.set_caption('LD24 Server')

s = LD24Server(localaddr=(host, port))
s.Launch()