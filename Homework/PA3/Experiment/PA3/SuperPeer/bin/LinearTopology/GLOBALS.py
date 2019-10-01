"""GLOBALS.py
  This module provides global variables between all of the other modules
  
  Attributes:
  
  TODO:
   - investigate a faster/more efficient data structure to use other than a list for message IDs
   
   Author:
     Alec Buchanan - 10/2018

"""
def init():
	global LOCAL_PORT, CONSISTENCY, NEIGHBOR_IP, NEIGHBOR_PORT, TTL, DEBUG_MODE, SENT_MESSAGE_IDS, RECV_MESSAGE_IDS, SUPER_PEER_PORT_BROADCAST, SUPER_PEER_ID, TOPOLOGY, BROADCAST_STATUS, LEAF_NODE_PORT, SUPER_PEER_LIST
	RECV_MESSAGE_IDS = [] # a record of all seen message IDs
	SENT_MESSAGE_IDS = []	# a record of all sent message IDs
	TTL = 2				# defines query and query hit ttl
	DEBUG_MODE = True 	# enables/disables print statements
	BROADCAST_STATUS = 0
	CONSISTENCY = "PULL"
	SUPER_PEER_LIST = [[0, "198.37.24.124", 7000], [1, "198.37.24.124", 7001], [2, "198.37.24.124", 7002], [3, "198.37.24.124", 7003], [4, "198.37.24.124", 7004], [5, "198.37.24.124", 7005], [6, "198.37.24.124", 7006], [7, "198.37.24.124", 7007], [8, "198.37.24.124", 7008], [9, "198.37.24.124", 7009]]
	#, [3, "198.37.24.124", 7003], [4, "198.37.24.124", 7004], [5, "198.37.24.124", 7005], [6, "198.37.24.124", 7006], [7, "198.37.24.124", 7007], [8, "198.37.24.124", 7008], [9, "198.37.24.124", 7009]]
	##[[0, "198.37.24.124", 7000], [1, "198.37.24.124", 7004]]
	## full list: [[0, "198.37.24.124", 7000], [1, "198.37.24.124", 7001], [2, "198.37.24.124", 7002], [3, "198.37.24.124", 7003], [4, "198.37.24.124", 7004], [5, "198.37.24.124", 7005], [6, "198.37.24.124", 7006], [7, "198.37.24.124", 7007], [8, "198.37.24.124", 7008], [9, "198.37.24.124", 7009]]