import socket
import sys
import pickle
from time import sleep
from queue import Queue
from _thread import *
import threading
from threading import Thread
import superPeer

sys.path.append('.\\LinearTopology')

import GLOBALS
import utility

response = [[]]
num = 0

def addMessage():
	"""Initializes the Reponse list to make sure no old responses were left in it.

		Args:
			None

		Returns:
			None

		Globals:
			response - List to store the responses from the other Super Peers.

		Calls:
			None

		Called by:
			broadcastMsg

	"""
	global response
	global num
	if num != 0:
		response.append([])
	for x in GLOBALS.SUPER_PEER_LIST:
		response[num].append([])
	num +=1

def broadcastQueryThread(msg, response, id, index):
	"""Sends a message to all other Super Peers.

		Args:
			filename    (Str)    - The name of the file to be searched for.
			response    (List)   - List that will store all of the responses form the super peers.
			id          (int)    - Then index for the list to put all of the data in
			index       (Int)    - The index of response to store the answer from the Super Peer in.

		Returns:
			A list of leaf nodes that have a the file.

		Globals:

		Calls:

		Called by:
			broadcastMsg()
	"""
	ip = GLOBALS.SUPER_PEER_LIST[index][1]
	port = int(GLOBALS.SUPER_PEER_LIST[index][2])
	hits = []
	try:
		sock = socket.socket()
		sock.connect((ip, port))
		msg = pickle.dumps(msg)
		sock.send(msg)
		data = sock.recv(1024)
		data = pickle.loads(data)
		if data is not -1:
			response[id][index] = data
			print("[info] Broadcast lib: Response from Super Peer: " + str(index) + " : " + str(data))
		else:
			print("[info] Broadcast Lib: No hits")
	except socket.error as err:
		print("[ERROR] Broadcast lib: Error connecting " + str(ip) + ":" + str(port))
	sock.close()
	return

def broadcastQuery(msg):
	"""Spawns threads to send out the query to all other super peers
		
		Args:
			msg    (query)   - query object to get broadcasted
		
		Returns:
			response[msg.id]   - list of responses from the other Super Peers
		
		Globals:
			num   (Int)        - used for msg ID's 
			response  (List)   - stores the responses form the other Super Peers
			
		Calls:
			broadcastQueryThread
		
		Called by:
			superPeer.broadcastSearch
	"""
	threads = []
	global num
	msg.id = num
	global response
	addMessage()
	for x in range(len(GLOBALS.SUPER_PEER_LIST)):
		if x == GLOBALS.SUPER_PEER_ID:
			continue
		proc = Thread(target = broadcastQueryThread, args = [msg, response, msg.id, x])
		proc.start()
		threads.append(proc)

	for proc in threads:
		proc.join()
	print("All responses received")
	return response[msg.id]
	
def broadcastQueryHandler(con, msg):
	"""Handles query requests from other Super Peers
	
		Args:
			con    (socket.socket)  - socket object that holds the connection with the other Super Peer
			msg    (Query)          - Query Object that holds the info for what file to look for
			
		Returns:
			void                    - Sends back a list of QueryHit objects if the file was found
			
		Globals:
			
		Calls:
			superPeer.searchLocal  

		Called By:
			superPeer.superPeerThreadHandler
	"""
	filename = msg.fname
	peers = []
	print("[info] Broadcast lib: Searching for file: " + filename)
	peers = superPeer.searchLocal(filename)
	if peers:
		try:
			msg = pickle.dumps(peers)
			con.sendall(msg)
		except:
			print("[ERROR] Broadcast lib: Connection Failed")
	else:
		try:
			con.send(pickle.dumps(-1))
		except:
			print("[ERROR] Broadcast lib: Connection Failed")
	return
