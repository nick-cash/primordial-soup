# LD24 Client Code
# This will eventually be included in the main app

import sys, pygame, time
from pygame.locals import *
from serialize import *

from PodSixNet.Connection import connection, ConnectionListener

class Client(ConnectionListener):
   def __init__(self, host, port):
      self.Connect((host, port))
      self.Reset()
      self.id = 0

      time.sleep(1)

   def Update(self):
      connection.Pump()
      self.Pump()

   def SendReady(self):
       connection.Send({"action": "ready"})

   def SendStatUpdate(self, data):
      connection.Send({"action": "statupdate", "stat": data})

   def Reset(self):
      self.players = {}      
      self.game_data = {}
      self.last_game_data = {}
      self.game_state = "waiting"
      self.countdown = 0.0
      self.new_data = False   

   def NumPlayersReady(self):
      n = 0

      for p in self.players:
         if self.players[p]:
            n += 1

      return n
          
   ###############################
   ### Network event callbacks ###
   ###############################
   
   def Network_update(self, data):
      self.game_state = "running"
      self.game_data = data
      self.new_data = True

   def Network_players(self, data):
      mark = []
     
      for player_id in data['players']:
         if not self.players.has_key(player_id):
            self.players[player_id] = data['players'][player_id]
      
      for player_id in self.players:
         if not player_id in data['players'].keys():
            mark.append(player_id)
      
      for m in mark:
         if m in self.players:
            del self.players[m]

   def Network_player_ready(self, data):
      self.players[data['id']] = data['ready']

   def Network_countdown(self, data):
      self.game_state = "countdown"
      self.countdown = data['time_remaining'] / 1000.0

   def Network_ping(self, data):
      self.id = data["id"]
      connection.Send({"action": "ping"})

   def Network_server_full(self, data):
      print("Server was full. Connection terminated.")
      connection.Close()
   
   def Network_connected(self, data):
      print("Connected")
   
   def Network_error(self, data):
      print data
      import traceback
      traceback.print_exc()
      connection.Close()
   
   def Network_disconnected(self, data):
      print("Disconnected")
