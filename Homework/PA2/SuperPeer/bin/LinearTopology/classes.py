"""classes.py
  This file provides the classes/structs to be sent over the network
  
  Attributes:
  
  TODO:
   
   
   Author:
     Alec Buchanan - 10/2018

"""
class query:
  def __init__(self, id, ttl, fname):
    self.id = id
    self.TTL = ttl
    self.fname = fname
class queryHit:
  def __init__(self, id, ttl, fname,leafAddr, leafPort):
    self.id = id
    self.TTL = ttl
    self.fname = fname
    self.ip = leafAddr
    self.port = leafPort