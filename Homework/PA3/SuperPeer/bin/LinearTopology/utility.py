"""utility.py
	This module is used to house all of the utility functions for linear topology.

	Attributes:

	TODO:
		- Add a function to generate messageIDs

	Author:
		Alec Buchanan - 10/2018

"""

#
# generic imports
#
import sys
import socket
import pickle
from threading import Thread
import time

#
# local imports
#
import GLOBALS


def connectToSuperPeer(addr, port):
	""" Creates a socket and connects to the address given

		Args:
			addr (char[15]):	IP address of server as a string
			port (int):		Port number

		Returns:
			Sucess
			socket.socket:	socket with active connection to server
		Error
	    -1:				Error connecting

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none
		Updates:
		none
	"""
	try:
		# create socket and connect to super peer
		sock = socket.socket()
		sock.connect((addr, port))
		if GLOBALS.DEBUG_MODE: print("[info] Linear lib: connecting to neighbor " + str(addr) + ":" + str(port))
		return sock
	except socket.error as err:
		print("[ERROR] Linear lib: Error connecting to other super peer: " + str(addr) + ":" + str(port))
		return -1


def listenForConnection(port):
	""" Creates socket and listens for connections.

		Args:
			port (int):	Port number to listen on

		Returns:
			Success
			Generator that yields an active connection
		Error
			-1:	Could not create socket

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none

		Updates:
		none
	"""
	try:
		#create socket as a server
		sock = socket.socket()
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', port))
		sock.listen(5)
		if GLOBALS.DEBUG_MODE: print("[info] Linear lib: Now listening for other super peers")
	except socket.error as err:
		print("[Error] Linear lib: Error setting up server")
		return -1
	while True:
		# yield the connection every time a connection is received
		con, addr = sock.accept()
		yield con

def sendMessage(neighbor, message):
	""" Send message over given connection

		Args:
			neighbor (socket.socket):	an active connection
			message  (anything?):		what ever you want sent

		Returns:
			1:  sucess
			-1: failure

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none

		Updates:
			none
	"""
	try:
		msg = pickle.dumps(message)
		neighbor.send(msg)
		return 1
	except socket.error as err:
		print("[Error] Linear lib: Connection with neighbor closed.")
		return -1

def receiveMessage(sock):
	""" reads message from given socket

		Args:
			sock (socket.socket): socket with an active connection

		Returns:
			message (void *):	the message read from the buffer
			0:				connection closed
			-1:				error or connection closed

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none

		Updates:
			none
	"""
	try:
		msg = sock.recv(4096)
		#print(msg)
		if msg == b'': return 0
		message = pickle.loads(msg)
		return message
	except socket.error as err:
		print("[ERROR] Linear lib: Connection with neighbor closed.")
		return -1

def getValueFromConfLine(line):
	""" Reads a single line of the config file. It is assumed that the following format:
		VARIABLE NAME = VALUE

		Args:
			line (c[:]):	line from the conf file

		Returns:
			c[:]	the value from the specified conf line

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none

		Updates:
			none
	"""
	return line.split("=")[1].strip()

def closeConnections(left, right):
	""" Closes two connections at once

		Args:
		  left (socket.socket):	 the socket for the left neighbor
		  right (socket.socket): the socket for the right neighbor

		Returns:
			void

		Globals:
			none

		Calls:
			none

		Called By:

		TODO:
			none
		Updates:
			none

	  """
	if GLOBALS.DEBUG_MODE: print("[info] Linear lib: Closing connections")
	left.shutdown(socket.SHUT_RDWR)
	left.close()
	right.shutdown(socket.SHUT_RDWR)
	right.close()

def assignGlobals(conf):
	""" reads the config file and populates global variables

		Args:
			conf (file):	opened config file

		Returns:
			void

		Globals:
			LOCAL_PORT
			NEIGHBOR_IP
			NEIGHBOR_PORT
		Calls:
			GLOBALS.init()
			getValueFromConfLine()

		Called By:

		TODO:
			none

		Updates:
			none

	"""
	lines = conf.readlines()
	GLOBALS.init()
	GLOBALS.LOCAL_PORT    = int(getValueFromConfLine(lines[0]))
	GLOBALS.NEIGHBOR_IP   = getValueFromConfLine(lines[1])
	GLOBALS.NEIGHBOR_PORT = int(getValueFromConfLine(lines[2]))
	GLOBALS.SUPER_PEER_PORT_BROADCAST = int(getValueFromConfLine(lines[3]))
	GLOBALS.SUPER_PEER_ID = int(getValueFromConfLine(lines[4]))
	GLOBALS.LEAF_NODE_PORT = int(getValueFromConfLine(lines[5]))

def generateUniqueID():
	""" generates a globally unique id for messages

		Args:
			void

		Returns:
			void

		Globals:
			NEIGHBOR_IP

		Calls:

		Called By:

		TODO:
			none

		Updates:
			none

	"""
	neighbor = GLOBALS.NEIGHBOR_IP.replace(".","")	# this makes the id unique to this super peer
	timestamp = str(time.time()).replace(".","")		# this should make the id unique on this super peer
	id = int(neighbor + timestamp)
	while id in GLOBALS.SENT_MESSAGE_IDS:				# this validates its uniqueness
		id = id + 1

	GLOBALS.SENT_MESSAGE_IDS.append(id)				# add to global list
	return id
