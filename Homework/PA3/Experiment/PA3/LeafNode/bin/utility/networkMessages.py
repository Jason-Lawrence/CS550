"""networkMessages.py
  This file provides the classes/structs to be sent over the network

  **NOTICE**
  any changes in this file must be made in the corresponding file in superpeer

  Attributes:

  TODO:


   Author:
     Alec Buchanan - 10/2018

"""
class fileRegistration:
	def __init__(self, command, filename, version, lastMod):
		#   command = 0 -> file remove
		#   command = 1 -> file added
		self.command = command
		self.filename = filename
		self.version = version
		self.lastMod = lastMod

class fileSearch:
    def __init__(self, topology, filename):
        #   topology = 0  -> linear topology
        #   topology = 1  -> broadcast topology
        self.topology = topology
        self.filename = filename

class versionControl:
	def __init__(self, version, filename, lastMod):
		self.version = version
		self.filename = filename
		self.lastMod = lastMod

class fileMetaData:
    def __init__(self, filesize, originIP, originPort, TTR, Version, original, experation):
        self.filesize = filesize
        self.originIP = originIP
        self.originPort = originPort
        self.TTR = TTR
        self.version = Version
        self.original = original
        self.experation = experation

class queryHit:
	def __init__(self, id, ttl, fname, origin, lastMod, leafAddr, leafPort):
		self.id = id
		self.TTL = ttl
		self.fname = fname
		self.origin = origin
		self.lastMod = lastMod
		self.ip = leafAddr
		self.port = leafPort