import socket
import sys
import pickle
from time import sleep
from _thread import *
import threading
from threading import Thread

sys.path.append('.\\LinearTopology')
sys.path.append('.\\broadcastTopology')

import linearTopology
import broadcast
import utility
from classes import *
import GLOBALS

grid = [[]]  ##Will end up being a list of lists. Each of the lists will represent a peer. The first
SuperPeers = []
leafNodesIP = [] ##List of IP Addresses and port numbers
leafNodesID = [] ## list of peerIDs
leafNodesPort = []
count = 0 ## Number of Peers registered with the Index Server

##Prints all of the files that are registered with the server
def printPeer(peerID):
	""" Prints all of the files that are registered under the peer

		Args:
			peerID: Unique ID for the Peer

		Returns:
			Void. It prints everything to the console

		Globals:

		Calls:

		Called by:
			add()
			remove()

	"""
	print("[info] PRINTING ALL FILES ON THE PEER")
	for x in range(1, len(grid[peerID])):
		print("Filename: " + grid[peerID][x])

def printGrid():
	""" Prints all of the files that are registered with the server

		Args:
			void

		Returns:
			Void. It prints everything to the console

		Globals:
			count

		Calls:

		Called by:
			sendCatalog()
			removePeerFromGrid()

	"""
	print("[info] PRINTING ALL FILES ON THE GRID")
	if count == 1:
		print("[info] Files stored at peer: " + str(grid))

	else:
		for y in range(len(leafNodesID)):
			print("[info] Files stored at peer: " + str(grid[y][0]))      ##prints out the the peerID
			for x in range(1, len(grid[y])):              ##Iterates through the file list for each peer
				print("Filename: " + grid[y][x])
	print("[info] END OF FILES")

def sendCatalog(con):
	""" Sends a list of all files that are being hosted within the system and available to download.

		Args:
			con  (socket.socket) - the socket with an open connection to the client

		Returns:
			Void. It prints everything to the console and sends a message to the client

		Globals:

		Calls:
			printGrid()

		Called by:
			leafThreadHandler()

	"""
	files = []
	#Get list of files
	for peer in grid:
		for file in range(1,len(peer)):
			if peer[file] not in files: files.append(peer[file])
	#convert list to string
	msg = ""
	for file in files:
		msg = msg + file + "\n"
	printGrid()
	try:
		con.send(str.encode(msg))
	except socket.error as err:
		print("[ERROR] Failed to send catalog")

def removePeerFromGrid(con, peerID):
	""" unregisters a peer from the Grid

		Args:
			con    (socket.socket) - the socket with an open connection with a Leaf Node.
			peerID (Int)    - Peer ID to remove from the grid along with its files.

		Returns:
			Void. It prints everything to the console.

		Globals:

		Calls:
			printGrid()

		Called by:
			leafThreadHandler()

	"""
	global count
	addr = con.getpeername()
	if count == 1:
		grid[0].clear()
		grid.pop(0)
		leafNodesIP.remove(addr[0])
		leafNodesID.remove(peerID)
		count -= 1
	elif peerID == grid[peerID][0]:
		grid[peerID].clear()
		grid.remove(peerID)
		leafNodesIP.remove(addr[0])
		leafNodesID.remove(peerID)
		count -= 1
	printGrid()
	return


def addPeerToGrid(peerID):
	""" Registers a peer with the server.

		Args:
			peerID    (Int)    - The peerId to add to the grid.

		Returns:
			Void

		Globals:
			count - Counts how many peers are registered with the server.

		Calls:

		Called by:
			leafThreadHandler()

	"""
	global count
	if peerID not in leafNodesID:
		if count != 0:
			grid.append([])
			grid[count].insert(0, peerID)
			count += 1
		else:
			grid[count].insert(0, peerID)
			count += 1
	else:
		print("[info] Peer already in grid")
	return

def add(peerID, filename):
	""" Adds a file to the peer by finding the peerID by locating the index of the IP address
		stored in the addresses list and then appends the filename to the end of the list.

		Args:
			peerID     (Int)    - The peer to add the file to.
			filename   (Str)    - the name of the file to be added to the peer's file list

		Returns:
			Void. It prints to the console

		Globals:

		Calls:
			printPeer()

		Called by:
			leafThreadHandler()

	"""
	if peerID == grid[peerID][0]:
		grid[peerID].append(filename) ##append the file if not already in the list.
	else:
		print("[ERROR] Super Peer: Invalid connection") ##If the IP address isn't registered with the server then thier is an invalid connection
	#printPeer(peerID)

def remove(peerID, filename):
	""" Removes a file from the peer.

		Args:
			peerID     (Int)    - The peer to remove the file from.
			filename   (Str)    - The name of the file to be added to the peer's file list

		Returns:
			Void. It prints to the console

		Globals:

		Calls:
			printPeer()

		Called by:
			leafThreadHandler()
	"""
	if peerID in leafNodesID:
		if filename in grid[peerID]:
			grid[peerID].remove(filename) ##Remoive the file if the file exists.
		else:
			print("[ERROR] Super Peer: Invalid file:" + filename)
	else:
		print("[ERROR] Super Peer: Invalid connection")
	#printPeer(peerID)

##Searches all of the peers for the Given FileName and returns a lit of peers that have that file.
##If file is not found sends an empty list.
def searchLocal(filename):
	"""Searches the registered files and appends the peer's IP address and Server port to a list. 
		
		Args:
			filename        (str)    - The file to search for
			
		Returns:
			peers           (list)   - list of tuples where in it is the peer's IP address and server port
			
		Globals:
			LeafNodesIP     (list)   - list of peer IP addresses 
			LeafNodesPort   (list)   - list of peer Server Ports
		
		Calls:
			None
			
		Called by:
			leafThreadHandler()
			superPeerThreadHandler()
	"""
	peers = []
	for x in range(len(grid)):
		for y in range(len(grid[x])):
			if grid[x][y] == filename:
				peers.append((leafNodesIP[x], leafNodesPort[x]))

	return peers

def linearSearch(filename):
	"""Searches the registered files of the other Super Peers in a linear topology and appends any hits to a list. 
		
		Args:
			filename        (str)    - The file to search for
			
		Returns:
			peers           (list)   - list of tuples where in it is the peer's IP address and server port
			
		Globals:
			queryHit.ip     (str)   - leaf IP address of the 
			queryHit.port   (int)   - leaf port number
		
		Calls:
			linearTopology.findFileLinearly()
			
		Called by:
			leafThreadHandler()
	"""
	peerList = []

	for hit in linearTopology.findFileLinearly(filename):
		#TODO: add timeout incase something gets stuck
		print("[info] Linear lib: Query hit at " + str(hit.ip) + ":" + str(hit.port))
		peerList.append((hit.ip, hit.port))

	return peerList

def broadcastSearch(filename):
	"""Searches the registered files of the other Super Peers in a Broadcast Topology and appends the peer's IP address and Server port to a list. 
		
		Args:
			filename        (str)    - The file to search for
			
		Returns:
			peers           (list)   - list of tuples where in it is the peer's IP address and server port
			
		Globals:
			LeafNodesIP     (list)   - list of peer IP addresses 
			LeafNodesPort   (list)   - list of peer Server Ports
		
		Calls:
			None
			
		Called by:
			leafThreadHandler()
	"""
	peers = broadcast.broadcastMsg(filename)
	peerListtmp = []
	peerList = []
	for x in range(len(peers)):
		for y in range(len(peers[x])):
			for z in range(len(peers[x][y])):
				if peers[x][y]is not None:
					peerListtmp.append(peers[x][y][z])
	x = 0
	while x < len(peerListtmp):
		peerList.append((peerListtmp[x], peerListtmp[x+1]))
		##print("[info] Braodcast lib: Query hit at " + str(peerListtmp[x]) + ":" + str(peerListtmp[x+1]))
		x += 2
	print("[info] Super Peer: Boadcast lib: All query hits " + str(peerList))
	return peerList

def superPeerThreadHandler(con):
	""" A thread Handler for Super Peer Broadcast lib connections.

		Args:
			con   (socket.socket) - the socket with an open connection with a Super Peer.

		Returns:

		Globals:

		Calls:
			searchLocal()

		Called by:
			listenForSuperPeers()
	"""
	addr = con.getpeername()
	filename = ""
	sock = socket.socket
	while True:
		try:
			data = con.recv(1024)
		except socket.error as err:
			print("[info] Braodcast lib: Super Peer disconnected")
			return
		try:
			data = pickle.loads(data)
		except:
			print("[info] Braodcast lib: Super Peer exited")
			return
		if not data:
			print("[info] Braodcast lib: End")
			con.close()
			break
		filename = data
		peers = []
		print("[info] Broadcast lib: Searching for file: " + filename)
		peers = searchLocal(filename)
		try:
			msg = pickle.dumps(peers)
			con.sendall(msg)
		except:
			print("[ERROR] Broadcast lib: Connection Failed")
		con.close()
		return


def leafThreadHandler(con):
	""" A thread handler that handles leaf Node connections.

		Args:
			con  (socket.socket)  - the socket with an open connection with the peer.

		Return:

		Globals:
			count

		Calls:
			add()
			remove()
			removePeerFromGrid()
			searchLocal()
			linearSearch()
			broadcastSearch()
			sendCatalog()

		Called by:
			listenForLeafs()

	"""

	global count
	addr = con.getpeername()
	status = -1
	filename = ""
	try:
		res = con.recv(80)
		res = pickle.loads(res)
		peerID = res[0]
		serverPort = res[1]
		if peerID < 0:
			peerID = count
			print("[info] Super Peer: Peer connected, PeerID: " + str(peerID))
			con.send(pickle.dumps(peerID))
			addPeerToGrid(peerID)
			leafNodesIP.append(addr[0])
			leafNodesID.append(peerID)
			leafNodesPort.append(serverPort)
		else:
			con.send(pickle.dumps(peerID))
	except:
		print("[ERROR] ")
	while True:
		try:
			data = con.recv(1024)
		except socket.error as err:
			print("[info] Super Peer: Leaf Node " + str(peerID) + " disconnected")
			removePeerFromGrid(con, peerID)
			con.close()
			return
		try:
			data = pickle.loads(data)
		except:
			print("[info] Super Peer: Client " + str(peerID) + " exited")
			return
		if not data:
			print('[info] Super Peer: End')
			removePeerFromGrid(peerID)
			con.close()
			break

		status = data[0]
		filename = data[1]
		if status == 0:
			print("[info] Super Peer: Peer " + str(peerID) + " removing file: " + filename)
			remove(peerID, filename)

		elif status == 1:
			print("[info] Super Peer: Peer " + str(peerID) + " adding file: " + filename)
			add(peerID, filename)
			try:
				m = pickle.dumps(1)
				con.send(m)
			except:
				print("[ERROR] Super Peer: Super Peer: Failed to send")
				
		elif status == 2:
			print("[info] Super Peer: Sending file catalog")
			sendCatalog(con)

		elif status == 3:
			print("[info] SuperPeer: Searching for file: " + filename)
			peers = searchLocal(filename)
			if peers:
				try:
					msg = pickle.dumps(peers)    
					con.sendall(msg)
				except:
					print("[ERROR] Super Peer: Unable to send results")
					
			else:
				print("[info] Super Peer: File " + filename + " was not found locally")
				print("[info] Super Peer: Searching other Peers via Broadcast Search")
				peers = broadcastSearch(filename)
				try:
					msg = pickle.dumps(peers)    
					con.sendall(msg)
				except:
					print("[Error] Super Peer: Unable to send results")

		elif status == 4:
			print("[info] Super Peer: Searching for file: " + filename)
			peers = searchLocal(filename)
			if peers:
				try:
					msg = pickle.dumps(peers)    
					con.sendall(msg)
				except:
					print("[Error] Unable to send results")
			else:
				print("[info] Super Peer: File " + filename + " was not found locally")
				print("[info] Super Peer: Searching other Peers via Linear Search")
				peers = linearSearch(filename)
				try:
					msg = pickle.dumps(peers)    
					con.sendall(msg)
				except:
					print("[Error] Super Peer: Unable to send results")		
					
	con.close()
	print("Client Disconnected")

def listenForSuperPeerBroadcast():
	"""Listens for Super Peer connections and spawns off threads that handle the connection.

		Args:
			None

		Return:
			None

		Globals:
			SUPER_PEER_PORT_BROADCAST - the port to listen for Super Peer connections on.

		Calls:
			superPeerThreadHandler()

		Called by
			main()
	"""
	port = GLOBALS.SUPER_PEER_PORT_BROADCAST
	host = ""
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((host, port))
	except soc.error:
		print("[ERROR] Super Peer: Binding failed")
		sys.exit()

	soc.listen(80)

	print("[info] Broadcast lib: Socket for Super Peers is now active")

	while True:
		con, addr = soc.accept()
		print('[info] Broadcast lib: Connected to Super Peer at:', addr[0], ':', addr[1])
		start_new_thread(superPeerThreadHandler, (con,))

	soc.close()

def listenForLeafs():
	"""Listens for Leaf Node connections and spawns off threads that handle the connection.

		Args:
			None

		Return:
			None

		Globals:
			LEAF_NODE_PORT - the port to listen for leaf node connections on.
		Calls:
			get_LEAF_NODE_PORT()
			leafThreadHandler()

		Called by
			main()
	"""
	port = GLOBALS.LEAF_NODE_PORT
	host = ""
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((host, port))
	except soc.error:
		print("[info] Super Peer: Binding for peers failed")
		sys.exit()

	soc.listen(80)

	print("[info] Super Peer: Socket for Leaf Nodes is now active")

	while True:
		con, addr = soc.accept()
		print('[info] Super Peer: Connected to Leaf Node at:', addr[0], ':', addr[1])
		start_new_thread(leafThreadHandler, (con,))

def main():
	"""Main function. Starts the threads that handle listening for other Super Peers and Leaf Nodes.

		Args:

		Return:

		Globals:
			None
		Calls:
			listenForSuperPeers
			listenForLeafs()
		Called by
			main.main()
	"""
	print('[info] Super Peer: Starting Super Peer')
	superPeerServerBroadcast = Thread(target = listenForSuperPeerBroadcast)
	superPeerServerBroadcast.deamon = True
	superPeerServerBroadcast.start()
	superPeerLeafs = Thread(target = listenForLeafs)
	superPeerLeafs.daemon = True
	superPeerLeafs.start()
