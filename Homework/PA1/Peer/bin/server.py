import socket
from threading import Thread
from time import sleep
from queue import Queue
from os import listdir
import pickle
import sys
import os
from globals import * 


def sendMessagesToIndex(sock, messages):
	""" sends messages from specified format over socket
		
		Args:
			sock (socket.socket):	socket with established connection
			messages ((I4,C)[:]):	a list of tupples containing a command and message
			
		Message:
			command:	0 means removed, 1 means add
			message:	the file name
			
		Returns:
			-1 - error
			1  - success
			
		Calls:
			void
			
		Called By:
			indexServer()
			
	"""
	for msg in messages:
		print("+ Peer Server: Change to file: " + msg[1])
		m = pickle.dumps(msg)
		try:
			sock.send(m)
			data = sock.recv(1024)
			data = pickle.loads(data)
		except socket.error as err:
			return -1
	return 1
def diffInLocalFiles():
	""" Finds which files have been added/removed locally since last checked
		
		Args:
			void
			
		Returns:
			messages ((I4,C)[:]):	list of tuples in format (command, message) where message is a filename
			
		Globals:
			LOCAL_FILE_LIST
			
		Calls:
			void
			
		Called By:
			indexServer()
			
	"""
	global LOCAL_FILE_LIST
	addedFiles = listdir(LOCAL_SHARED_FILE_SPACE)	#aka current files
	removedFiles = LOCAL_FILE_LIST					#aka previously recorded files
	#TODO: this can be a lot more efficient
	
	#record files that appear in both lists
	commonFiles = []
	for file in removedFiles:
		if file in addedFiles:
			commonFiles.append(file)
			
	#remove files that appear in both lists
	for file in commonFiles:
		addedFiles.remove(file)
		removedFiles.remove(file)
		
	#The files remaining in the respective list were either recently added or removed
	messages = []
	for file in removedFiles:
		messages.append((REMOVE_FILE, file))	#these files not longer exist
	for file in addedFiles:
		messages.append((ADD_FILE, file))		#these files have been recently added

	#redefine list of local files
	LOCAL_FILE_LIST = listdir(LOCAL_SHARED_FILE_SPACE)
	return messages
	
def connectToIndexServer():
	""" Establishes connection with index server
		
		Args:
			void
			
		Returns:
			socket.socket 	- On success, returns socket with connection to index server
			-1				- Error connecting to index server
			
		Globals:
			INDEX_SERVER_CONNECTION
			INDEX_SERVER_IP
			INDEX_SERVER_PORT
			
		Calls:
			
		Called By:
			indexServer()
			
		TODO:
			
		Updates:
			8/19	- remove attemped connection loop and combine try statments so there will only be one return value
	"""
	global INDEX_SERVER_CONNECTION
	try:
		sock = socket.socket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
		INDEX_SERVER_CONNECTION = 1
		return sock
	except socket.error as err:
		print("- Peer Server: Error connecting to index server!")
		INDEX_SERVER_CONNECTION = -1
	return -1
	
def indexServer():
	""" A thread that handles the connection with the index server. It also is in charge of keeping local files registered with index server
		
		Args:
			void
			
		Returns:
			0	- returns 0 on completion
			
		Globals:
			
		Calls:
			connectToIndexServer()
			diffInLocalFiles()
			sendMessagesToIndex(socket.socket, [(Int, Str)])
			
		Called By:
			server()
			
		TODO:
			Investigate making the local file update timer event driven
			
		Updates:
			8/19	- lowered loop timer from 60s to 2s
	"""
	#connect to index server
	sock = connectToIndexServer()
	if not isinstance(sock, socket.socket):
			print("- Peer Server: Gave up trying to connect to index server. Peer server shutting down.")
			return 0
	
	print("* Peer Server: Connected to index server")
	
	#TODO: make this event driven
	while 1:
		message = diffInLocalFiles()
		if sendMessagesToIndex(sock, message) == -1: return -1
		sleep(2)
	
	
def connectionHandler(con, addr):
	""" A thread that handles the connection with each individual client. 
		The protocol is a three step protocol:
		1.  receive file name
			  - looks for file and gets file size
		2. 	send file size
			  - if file does not exist, a file size of 0 is sent
		3. 	send the file
		
		Args:
			con (socket.socket)	- The socket with an open connection to the client
			addr (Str)			- The address of the client
			
		Returns:
			0	- returns 0 on error or completion
			
		Globals:
			
		Calls:
			
		Called By:
			server()
			
		TODO:
			clean and comment
			
		Updates:
	"""
	#get filename
	msg = con.recv(260) #260 bytes is the max file length, TODO: add try
	msg = pickle.loads(msg)
	
	#look for file sent by message
	size = 0
	try:
		#print("Looking for: " + LOCAL_SHARED_FILE_SPACE + "\\" + msg)
		size = os.path.getsize(LOCAL_SHARED_FILE_SPACE + "\\" + msg)
	except Exception as err:
		print("- Peer Server: client asked for nonexisting file")
		con.send(pickle.dumps(0))
		con.close()
		return 0
	
	#do a con.send for the file
	con.send(pickle.dumps(str(size))) # TODO: add try
	with open(LOCAL_SHARED_FILE_SPACE + "\\" + msg, 'rb') as file:
		content = file.read(1024)
		while content:
			con.send(content)
			#con.send(pickle.dumps(content))
			content = file.read(1024)
			
	#file is sent, close connection
	con.shutdown(socket.SHUT_WR)
	con.close()
	return 0	

def server():
	""" A thread that spawns the indexServer thread and spawns the connectionHandler thread when a client connects
		
		Args:
			
		Returns:
			-1 	- returns -1 on failure
			
		Globals:
			INDEX_SERVER_CONNECTION
			PEER_SERVER_STATUS
			
		Calls:
			indexServer()
			connectionHandler()
			
		Called By:
			main()
			
		TODO:
			clean and comment
			
		Updates:
	"""	
	global INDEX_SERVER_CONNECTION
	global PEER_SERVER_STATUS
	# Create connection with index server
	print("* Peer Server: connecting to index server...")
	indexServerThread = Thread(target = indexServer)
	indexServerThread.start()
	
	# Wait for connection with index server
	while INDEX_SERVER_CONNECTION == 0:
		sleep(1)
		if INDEX_SERVER_CONNECTION == 1: break
		if INDEX_SERVER_CONNECTION == -1: 
			set_PEER_SERVER_STATUS(-1)
			exit()
			return -1
	
	
	# Create socket for Peer Server
	try:
		sock = socket.socket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', P2P_PORT))
		sock.listen(5)
		print("+ Peer Server: Now listening for other peers")
	except socket.error as err:
		print("- Peer Server: Error setting up server")
		print(err)
		set_PEER_SERVER_STATUS(-1)
		exit()
		return -1
	
	# Listen for clients
	set_PEER_SERVER_STATUS(1)
	while True:
		con, addr = sock.accept()
		connection = Thread(target = connectionHandler, args = (con,addr))
		connection.start()
	sock.close()
