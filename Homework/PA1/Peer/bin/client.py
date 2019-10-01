import socket
from threading import Thread
from time import sleep
import time
from queue import Queue
from os import listdir
import pickle
import sys
import os
import random
from globals import * 




def createClientSocket():
	""" The main function. The entry point for the program
		
		Args:
			
		Returns:
			socket.socket	- returns a socket on success
			-1				- returns -1 on failure
			
		Globals:
		
		Calls:
			
		Called By:
			createClientSocket
			
		TODO:
			
		Updates:
	"""	
	try:
		sock = socket.socket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		return sock
	except socket.error as err:
		#TODO: Handle error
		print("- Peer Client: Error creating socket for client!")
		return -1

def client():
	""" The main function. The entry point for the program
		
		Args:
			
		Returns:
			-1	- on failure
			
		Globals:
		
		Calls:
			createClientSocket()
			
		Called By:
			main()
			
		TODO:
			- seperate into functions
			- add trys and excepts
			
		Updates:
			9/21 - if file size is 0 then set error handling
	"""	
	#Gets the requested file from the server address given
	def getFile(serverAddr):
			try: 
				#connect to peer server
				peerServer = socket.socket()
				peerServer.connect((serverAddr, PEER_SERVER_PORT))
				pickled = pickle.dumps(requestedFile)
				#Ask for file 
				peerServer.send(pickled)
				#get file size
				filesize = peerServer.recv(1024)
				filesize = pickle.loads(filesize)
			except socket.error as err:
				print("- Peer Client: Problem connecting to peer server: " + str(serverAddr))
				
				
			#if filesize == 0: then file does not exist
			if filesize == 0:
				print("- Peer Client: Requested file was not found on peer server: " + serverAddr)
				return
	
	
			#Download file
			with open(LOCAL_SHARED_FILE_SPACE + "\\" + requestedFile, 'wb') as file:
				while True:
					try:
						data = peerServer.recv(1024) 
					except socket.error as err:
						print("- Peer Client: Download interrupted")
						return
					if len(data) == 0: break
					#data = pickle.loads(data)
					file.write(data)
			print("+ Peer Client: retreived file: '" + str(requestedFile) + "'")

	def getCatalog(sock):
		#connect to index server
		try: 
			sock.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
			sock.send(pickle.dumps((3, "search")))
			msg = "\n"
			
			#get string of all the file names
			while True:
				data = sock.recv(1024)
				msg = msg + data.decode()
				if len(data) < 1024: break
				
			#give file names to user
			print(msg)
		except socket.error as err:
			print("- Peer Client: failed to contact index server, aborting")
			return -1
			
	def clientSearch(sock, requestedFile, flag):
			#connect to index server
			try: 
				sock.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
				#search index server
				pickled = pickle.dumps((SEARCH_FILES, requestedFile))
				sock.send(pickled) 
			except socket.error as err:
				print("- Peer Client: failed to contact index server, aborting")
				return -1
		
	
			#TODO: what if reponse is larger than 1024
			try: 
				response = sock.recv(1024)
				response = pickle.loads(response)
			except socket.error as err:
				print("- Peer Client: failed to contact index server, aborting")
				return -1
			sock.close()
			if len(response) == 0:
				print("- Peer Client: File not registered with index server")
				return -1
			elif flag == 1:
				serverAddr = response[random.randint(0,len(response) - 1)]
				print("+ Peer Client: Looking for '" + str(requestedFile) + "' on: " + str(serverAddr))
				getFile(serverAddr)
			else:
				return 0
			return 1
				
	global PEER_SERVER_STATUS
	timeTotal = 0
	while get_PEER_SERVER_STATUS() == 0:
		sleep(1)
		if get_PEER_SERVER_STATUS() == 1: break
		elif get_PEER_SERVER_STATUS() == -1: return -1
	
	#create client socket
	print("+ Peer Client: Client starting...")
	sock = createClientSocket()
	if sock == -1: 
		print("- Peer Client: Client failed to start")
		return -1
	
	#################################################
	##
	##	input loop with peer server-client protocol:
	##		1. SEND: requested file name to index server
	##		2. RECV: list of peers that host that file
	##		3. SEND: file name to peer server
	##		4. RECV: file size
	##		5. RECV: file
	##
	##	- If list of peers that the index server sends is empty
	##	then there are no peers hosting that file
	##	- If the file size returned by the peer server is 0
	## 	then the peer does not have the file
	##
	#################################################
	print("+ Peer Client: Client started")
	while True:
		print("\n")
		print("----------- Special Commands -----------")
		print("search: retreives list of registered files")
		print("exit: exits the program")
		print("----------------------------------------")
		requestedFile = input("What file do you want?\n")
		if requestedFile == 'exit':
			sock.close()
			set_PEER_CLIENT_STATUS(-1)
			break
		elif requestedFile == 'search':
			getCatalog(sock)
			sock.close()
			sock = createClientSocket()
		elif requestedFile == 'test.txt':
			test = open("test.txt", "r")
			print("test file opened")
			while True:
				sock = createClientSocket()
				if sock == -1: 
					return -1
				timeStart = time.time()
				requestedFile = test.readline().strip()
				if requestedFile == '':
					break
				print("Searching for file: " + requestedFile)
				clientSearch(sock, requestedFile, 0)
				timeTotal += (time.time() - timeStart)
			timeAvg = timeTotal/500
			print("Average search request in seconds: " + str(timeAvg))
			 
				
		else:
			clientSearch(sock, requestedFile, 1)
			sock.close()
			sock = createClientSocket()
		
		#connect to index server
		"""
		try: 
			sock.connect((INDEX_SERVER_IP, INDEX_SERVER_PORT))
		except socket.error as err:
			print("- Peer Client: failed to contact index server, aborting")
			continue
		
		#search index server
		pickled = pickle.dumps((SEARCH_FILES, requestedFile))
		sock.send(pickled) # TODO: add try
		
		#TODO: what if reponse is larger than 1024
		response = sock.recv(1024)	#TODO: add try
		response = pickle.loads(response)
		sock.close()
		sock = createClientSocket()
		if sock == -1: return -1
		if len(response) == 0:
			print("+ Peer Client: File not registered with index server")
			continue
		#TODO: add error handling for if empty list is sent
		#print("looking on server: " + str(response[0])) 
		try: 
			peerServer = socket.socket()
			peerServer.connect((response[0], PEER_SERVER_PORT))
			pickled = pickle.dumps(requestedFile)
			peerServer.send(pickled)
			filesize = peerServer.recv(1024) # TODO: add try
			filesize = pickle.loads(filesize)
		except socket.error as err:
			print("- Peer Client: Problem connecting to peer server: " + str(response[0]))
			continue
		#print("filesize: ")
		#print(filesize)
		if filesize == 0:
			print("- Peer Client: Requested file was not found on peer server: " + response[0])
		
		
		#parse index server results
		with open(LOCAL_SHARED_FILE_SPACE + "\\" + requestedFile, 'w') as file:
			while True:
				data = peerServer.recv(1024) # TODO: add try
				if len(data) == 0: break
				data = pickle.loads(data)
				file.write(data)
			continue
			"""

			