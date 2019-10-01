import socket
import sys
import pickle
from time import sleep
from _thread import *
import threading
from threading import Thread

sys.path.append('.\\LinearTopology')
sys.path.append('.\\broadcastTopology')
sys.path.append('.\\utility')
sys.path.append('.\\consistencyPush')

import linearTopology
import broadcast
import utility
import GLOBALS
from networkMessages import *
import superPeerUtilities
import push

dictFiles = {}
dictLeafs = {}
count = 0 ## Number of Peers registered with the Index Server
id = 0 ## used for queryHit IDs

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

    """
    print("[info] PRINTING ALL FILES ON PEER: " + str(peerID))
    for x in dictFiles[peerID]:
        print("Filename: " + x[0])

def printDict():
    """ Prints all of the files that are registered with the server

        Args:
            void

        Returns:
            Void. It prints everything to the console

        Globals:
            count

        Calls:

        Called by:
            removePeerFromGrid()

    """
    print("[info] PRINTING ALL FILES IN THE DICT")
    for d in dictFiles:
        print("[info] Files stored at peer: " + str(d))
        for x in dictFiles[d]:
            print("Filename: " + x[0])
    print("[info] END OF DICT")

def removePeerFromDict(peerID):
    """ unregisters a peer from the Grid

        Args:
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
    dictLeafs.pop(peerID)
    dictFiles.pop(peerID)
    count -= 1
    printDict()
    return

def addPeerToDict(IP, port):
	""" Registers a new Leaf Node with the Super Peer
		Args:
			IP         (Str)      - The IP address of the new Leaf Node
			port       (Int)      - The Port number of the new Leaf Node

		Returns:
			Void

		Globals:
			count      (Int)     - Used to Determine the Peer ID

		Calls:

		Called by:
			leafThreadHandler()
	"""
	global count
	peerID = count
	while peerID in dictFiles and peerID in dictLeafs:
		peerID += 1
	count += 1
	dictFiles[peerID] = []
	dictLeafs[peerID] = (IP, port)
	return peerID

def addMaster(peerID, msg):
	""" Adds a Master file to the peer.

		Args:
			peerID     (Int)    - The peer to add the file to.
			msg        (fileRegistration)  - the message that contains all relevant data to register a file

		Returns:
			Void. It prints to the console

		Globals:

		Calls:

		Called by:
			fileRegistrationHandler

	"""
	if peerID in dictFiles:
		dictFiles[peerID].append((msg.filename, msg.version, msg.lastMod, 1))
	else:
		print("[ERROR] Super Peer: Invalid Connection")

def addCache(peerID, msg):
	""" Adds a Cache file to the peer.

		Args:
			peerID     (Int)    - The peer to add the file to.
			msg        (fileRegistration)  - the message that contains all relevant data to register a file

		Returns:
			Void. It prints to the console

		Globals:

		Calls:

		Called by:
			fileRegistrationHandler

	"""
	if peerID in dictFiles:
		dictFiles[peerID].append((msg.filename, msg.version, msg.lastMod, 0))
	else:
		print("[ERROR] Super Peer: Invalid Connection")

def remove(peerID, filename):
	""" Removes a file from the peer.

		Args:
			peerID     (Int)    - The peer to remove the file from.
			filename   (Str)    - The name of the file to be added to the peer's file list

		Returns:
			Void. It prints to the console

		Globals:

		Calls:

		Called by:
			leafThreadHandler()
			fileRegistrationHandler
	"""
	if peerID in dictFiles:
		for x in dictFiles[peerID]:
			if x[0] == filename:
				dictFiles[peerID].remove(x)
				break
	else:
		print("[ERROR] Super Peer: Invalid connection")

def searchLocal(filename):
	""" Searches the registered files and appends the peer's IP address and Server port to a list.

		Args:
			filename        (str)    - The file to search for

		Returns:
			peers           (list)   - list of tuples where in it is the peer's IP address and server port

		Globals:

		Calls:

        Called by:
			leafThreadHandler()
			superPeerThreadHandler()
			broadcast.broadcastQueryHandler
			linearTopology.superPeerConnection
			
	"""
	global id
	peers = []
	for d in dictFiles:
		for x in dictFiles[d]:
			if x[0] == filename:
				hit = queryHit(id, 0, filename, x[3], x[2], dictLeafs[d][0], dictLeafs[d][1])
				id += 1
				peers.append(hit)

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
            externalFileSearch
    """
    peerList = []

    for hit in linearTopology.findFileLinearly(filename):
        #TODO: add timeout incase something gets stuck
        print("[info] Linear lib: Query hit at " + str(hit.ip) + ":" + str(hit.port))
        peerList.append(hit)

    return peerList

def broadcastSearch(filename):
    """Searches the registered files of the other Super Peers in a Broadcast Topology and appends the peer's IP address and Server port to a list.

        Args:
            filename        (str)    - The file to search for

        Returns:
            peersList           (list)   - list of tuples where in it is the peer's IP address and server port

        Globals:

        Calls:
            broadcast.broadcastQuery
			classes.query

        Called by:
            externalFileSearch
    """
    message = query(0, 1, filename) ##make the query to broadcast
    peers = broadcast.broadcastQuery(message) ##returns a list of lists
    peerList = []
    for x in peers:
        for hit in x:
            if hit is not None:
                peerList.append(hit)

    return peerList

def versionControlHandler(msg):
    """ Searches the local Peers to see if the specified file is registered if so it sends and invalidate message to it
    
        Args:
            msg    (versionContro)    - message that specifies the file that is invalid
        
        Returns:
            Void
            
        Globals:
            
        Calls:
            searchLocal
            push.sendInvalidate
            remove
            
        Called by:
            superPeerThreadHandler
    
    """
    peers = searchLocal(msg.filename)
    if peers:
        for peerID, val in dictLeafs.items():
            for hit in peers:
                if hit.ip == val[0] and hit.port == val[1]:
                    push.sendInvalidate(msg, val[0], val[1])
                    
    return
    
def superPeerThreadHandler(con):
    """ A thread Handler for Super Peer Broadcast lib connections.

        Args:
            con   (socket.socket) - the socket with an open connection with a Super Peer.

        Returns:

        Globals:

        Calls:
            broadcast.broadcastQueryHandler
			versionControlHandler

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
            print("[info] Broadcast lib: Super Peer exited")
            return
        if not data:
            print("[info] Broadcast lib: End")
            con.close()
            break
        elif isinstance(data, query):
            broadcast.broadcastQueryHandler(con, data)
        
        elif isinstance(data, versionControl):
            versionControlHandler(data)
        else:
            print("[ERROR] Super Peer: Invalid Message")
			
        con.close()
        return

def fileRegistrationHandler(peer, message):
	""" Registers and unregisters files with the Super Peer 
		
		Args:
			peer    (Int)   - PeerID
			message (fileRegistration)   - message that specifies which file to register or unregisters
			
		Returns:
			1
		
		Globals:
			
		Calls:
			remove
			add
		
		Called by:
			leafThreadHandler
	"""
	if message.command == 0:
		print("[info] Super Peer: Peer " + str(peer) + " removing file: " + message.filename)
		remove(peer, message.filename)
		
	elif message.command == 1:
		print("[info] Super Peer: Peer " + str(peer) + " adding MASTER file: " + message.filename)
		addMaster(peer, message)    #TODO: unhardcode the version number here
		
	elif message.command == 2:
		print("[info] Super Peer: Peer " + str(peer) + " adding CACHE file: " + message.filename)
		addCache(peer, message)
		
	else:
		print("[ERROR] Super Peer: Unknown file file registration from peer server.")
		return -1
	return 1

def externalFileSearch(message, con):
	"""Handles File requests
		
		Args:
			message    (fileSearch)    - message that specifies which file to search for
			con		   (socket.socket) - socket object for the connection
		
		Returns:
			void
		
		Globals:
			
		Calls:
			searchLocal
			broadcastSearch
			linearSearch
		
		Called by:
			leafThreadHandler
		
	"""
	filename = message.filename
	print("[info] SuperPeer: Searching for file: " + filename)
	##peers = searchLocal(filename) 
	peers = broadcastSearch(filename)
	if peers:
		try:
			msg = pickle.dumps(peers)
			con.sendall(msg)
		except:
			print("[ERROR] Super Peer: Unable to send results")
    
	else:
		print("[info] Super Peer: File " + filename + " was not found locally")
		if message.topology == 3:
			print("[info] Super Peer: Searching other Peers via Broadcast Search")
			peers = peers + broadcastSearch(filename)
        
		elif message.topology == 4:
			print("[info] Super Peer: Searching other Peers via Linear Search")
			peers = peers + linearSearch(filename)
        
		try:
			msg = pickle.dumps(peers)
			con.sendall(msg)
		except:
			print("[Error] Super Peer: Unable to send results")

def changeVersions(peerID, message):
	""" Handles Version control 
		
		Args:
			peerID     (Int)  - ID of the Peer
			message    (versionControl) - message that specifies which file is invalid
		
		Returns:
			0
		
		Globals:
			
		Calls:
			push.broadcastVersionControl
		
		Called by:
			leafThreadHandler
	
	"""
	for x in dictFiles[peerID]:
		if x[0] == message.filename:
			origin = x[3]
			break
	remove(peerID, message.filename)
	if origin:
		addMaster(peerID, message)
	else:
		addCache(peerID, message)
	if GLOBALS.CONSISTENCY == "PUSH":
		push.broadcastVersionControl(message)
	print("[info] Super Peer: Update to " + message.filename)
	return 0

def leafThreadHandler(con):
	""" A thread handler that handles leaf Node connections.

		Args:
			con  (socket.socket)  - the socket with an open connection with the peer.

		Return:

		Globals:
			count

		Calls:
			addPeerToDict
			removePeerFromDict
			superPeerUtilities.sendACK
			fileRegistrationHandler
			externalFileSearch
			changeVersions

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
			peerID = addPeerToDict(addr[0], serverPort)
			print("[info] Super Peer: Peer connected, PeerID: " + str(peerID))
			con.send(pickle.dumps(peerID))
		else:
			con.send(pickle.dumps(peerID))
	except:
		print("[ERROR] ")
	while True:
		try:
			data = con.recv(1024)
		except socket.error as err:
			print("[info] Super Peer: Leaf Node " + str(peerID) + " disconnected")
			removePeerFromDict(peerID)
			con.close()
			return
		try:
			data = pickle.loads(data)
		except:
			print("[info] Super Peer: Client " + str(peerID) + " exited")
			return

		if isinstance(data, fileRegistration):
			superPeerUtilities.sendACK(con)
			fileRegistrationHandler(peerID, data)
		elif isinstance(data, fileSearch):
			externalFileSearch(data, con)
		elif isinstance(data, versionControl):
			superPeerUtilities.sendACK(con)
			changeVersions(peerID, data)
		else:
			print("[ERROR] Super Peer: unknown message sent from peer")
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
            listenForLeafs
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
