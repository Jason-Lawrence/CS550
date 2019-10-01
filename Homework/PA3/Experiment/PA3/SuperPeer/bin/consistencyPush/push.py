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
sys.path.append('.\\broadcastTopology')
sys.path.append('.\\utility')

import GLOBALS
import utility
from networkMessages import *

def sendInvalidate(msg, ip, port):
	"""Sends a message to the Leaf Node that the specified file is invalid
		
		Args:
			msg  (versionControl) - The message that invalidates a file 
			ip   (Str)            - The IP address of the Leaf Node to message
			port (Int)            - The Port number of the Leaf Node to message
			
		Returns:
			0     - returns 0 regardelss of error or success
			
		Globals:
			
		Calls:
			
		Called By:
			superPeer.superPeerThreadHandler
	"""
	if isinstance(msg, versionControl):
		try:
			con = socket.socket()
			con.connect((ip, port))
			msg = pickle.dumps(msg)
			con.send(msg)
			con.close()
		except:
			print("[ERROR] Super Peer: COnnection with Leaf Node Failed")
	
	return 0
	
def broadcastVersionControl(msg):
	"""Spawns threads to handle broadcasting out the given message
	
		Args:
			msg    (versionControl)   - message that specifies the file that is invalid
			
		Returns:
			0      - returns 0 regardelss of error or success
			
		Globals:
			
		Calls:
			broadcastVCThread
		
		Called by:
			superPeer.changeVersions
	"""
	threads = []
	for x in range(len(GLOBALS.SUPER_PEER_LIST)):
		if x == GLOBALS.SUPER_PEER_ID:
			continue
		proc = Thread(target = broadcastVCThread, args = [msg, x])
		proc.start()
		threads.append(proc)
		
	for proc in threads:
		proc.join()
	print("All messages have been sent")
	return 0
	
def broadcastVCThread(msg, index):
	"""Connects to the Super Peer and sends the Message
		
		Args:
			msg    (versionControl)    - message that specifies the file that is invalid
			index  (Int)               - which Super Peer to connect to 

		Returns:
			Void
			
		Globals:
			
		Calls:
			
		Called by:
			broadcastVersionControl
	"""
	ip = GLOBALS.SUPER_PEER_LIST[index][1]
	port = int(GLOBALS.SUPER_PEER_LIST[index][2])
	try:
		sock = socket.socket()
		sock.connect((ip, port))
		msg = pickle.dumps(msg)
		sock.send(msg)
	except:
		print("[ERROR] Broadcast lib: Error connecting " + str(ip) + ":" + str(port))

	sock.close()
	return 0