import socket
import sys
import pickle
from time import sleep
from queue import Queue
from _thread import *
import threading
from threading import Thread

sys.path.append('.\\LinearTopology')

import GLOBALS
import classes
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
	tmp = [[] for x in GLOBALS.SUPER_PEER_LIST]
	global response
	global num
	if num != 0:
		response.append([])
	for x in GLOBALS.SUPER_PEER_LIST:
		response[num].append(tmp)
	num +=1

def broadcastThread(filename, response, id, index):
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
	try:
		sock = socket.socket()
		sock.connect((ip, port))
		msg = pickle.dumps(filename)
		sock.send(msg)
		data = sock.recv(1024)
		data = pickle.loads(data)
		print("[info] Broadcast lib: Response from Super Peer: " + str(index) + " : " + str(data))
		response[id][index] = data
	except socket.error as err:
		print("[ERROR] Broadcast lib: Error connecting " + str(ip) + ":" + str(port))
	sock.close()
	return

def broadcastMsg(filename):
	"""Spawns threads to handle messaging the other Super Peers.

		Args:
			filename    (Str)    - the name of the file to be searched for.

		Returns:
			A list of leaf nodes that have a the file.

		Globals:
			response - List that will store all of the responses form the super peers.

		Calls:
			addMessage()
			broadcastThread()

		Called by:
			superPeer.broadcastSearch()
	"""
	threads = []
	GLOBALS.BROADCAST_STATUS = 1
	global num
	id = num
	global response
	addMessage()
	for x in range(len(GLOBALS.SUPER_PEER_LIST)):
		if x == GLOBALS.SUPER_PEER_ID:
			continue
		proc = Thread(target = broadcastThread, args = [filename, response, id, x])
		proc.start()
		threads.append(proc)

	#print("[info] Broadcast lib: All threads created")
	for proc in threads:
		proc.join()
	GLOBALS.BROADCAST_STATUS = 0
	return response[id]
