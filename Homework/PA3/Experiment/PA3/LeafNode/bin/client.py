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
import globals
import server

sys.path.append('.\\utility')
from networkMessages import *

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
			clientConnect()

		Called By:
			main()

		TODO:
			- seperate into functions
			- add trys and excepts

		Updates:
			9/21 - if file size is 0 then set error handling
	"""
	#Gets the requested file from the server address given

	def clientConnect(sock):
		peerID = globals.PEER_ID
		serverport = str(globals.PEER_SERVER_PORT)
		try:
			sock.connect((globals.INDEX_SERVER_IP, globals.INDEX_SERVER_PORT))
			sock.send(pickle.dumps((peerID, serverport)))
			res = sock.recv(80)
			res = pickle.loads(res)
			if res == peerID:
				return
			else:
				print("Error: unregistered")
				exit()
				return
		except socket.error as err:
			return - 1

	def getFile(serverAddr, serverPort, requestedFile):
			try:
				#connect to peer server
				peerServer = socket.socket()
				peerServer.connect((serverAddr, serverPort))
				pickled = pickle.dumps(requestedFile)
				#Ask for file
				peerServer.send(pickled)
				#get file size
				metaData = peerServer.recv(1024)
				metaData = pickle.loads(metaData)
			except socket.error as err:
				print("- Peer Client: Problem connecting to peer server: " + str(serverPort))


			#if filesize == 0: then file does not exist
			if metaData.filesize == 0:
				print("- Peer Client: Requested file was not found on peer server: " + str(serverPort))
				return


			#Download file
			globals.VERSION_RECORDER[requestedFile] = metaData
			with open(globals.CACHED_FILE_SPACE + "\\" + requestedFile, 'wb') as file:
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

	def clientSearch(sock, requestedFile, flag):
			#connect to index server
			try:
				clientConnect(sock)
				#search index server
				searchRequest = fileSearch(globals.TOPOLOGY, requestedFile)
				pickled = pickle.dumps(searchRequest)
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
				hit = response[random.randint(0, len(response)-1)]
				serverAddr = hit.ip
				serverPort = hit.port
				print("+ Peer Client: Looking for '" + str(requestedFile) + "' on: " + str(serverPort))
				getFile(serverAddr, serverPort, requestedFile)
			else:
				return 0
			return 1
			
	def clientTestSearch(sock, requestedFile):
		countInvalid = 0
		countTotal = 0
		try:
			clientConnect(sock)
			#search index server
			searchRequest = fileSearch(globals.TOPOLOGY, requestedFile)
			pickled = pickle.dumps(searchRequest)
			sock.send(pickled)
		except socket.error as err:
			print("- Peer Client: failed to contact index server, aborting")
			return -1
		try:
			response = sock.recv(1024)
			response = pickle.loads(response)
		except socket.error as err:
			print("- Peer Client: failed to contact index server, aborting")
			return -1
		sock.close()
		print("Total number of Responses:" + str(len(response)))
		if len(response) == 0:
			print("- Peer Client: File not registered with index server")
			return -1
		for hit in response:
			if hit.origin == 1:
				lastMod = hit.lastMod
				break
			else:
				print("No Origin Server")
				return -1
		for hit in response:
			if float(hit.lastMod) < lastMod:
				countInvalid += 1
				countTotal += 1
			else:
				countTotal += 1
		print("Invalid Count: " + str(countInvalid) + " Total Count: " + str(countTotal))
		invalidPercentage = (countInvalid/countTotal) * 100
		filePath = globals.CACHED_FILE_SPACE + "\\" + requestedFile
		if os.path.isfile(filePath):
			return invalidPercentage
		else:
			hit = response[random.randint(0, len(response)-1)]
			serverAddr = hit.ip
			serverPort = hit.port
			print("+ Peer Client: Looking for '" + str(requestedFile) + "' on: " + str(serverPort))
			getFile(serverAddr, serverPort, requestedFile)
			return invalidPercentage
		
	def test():
		globals.TEST_STATUS = 1
		test = open("test.txt", "r")
		print("test file opened")
		result = open(globals.RESULT_FILE, "w+")
		while True:
			sock = createClientSocket()
			if sock == -1:
				return -1
			requestedFile = test.readline().strip()
			if requestedFile == '':
				break
			print("Searching for file: " + requestedFile)
			result.write(str(clientTestSearch(sock, requestedFile))+ "\n")
			sleep(1)
			
		globals.TEST_STATUS = 0
		result.close()
		test.close()
	
	if globals.TEST == 1:
		sleep(5)
		test()
	
	timeTotal = 0
	while globals.PEER_SERVER_STATUS == 0:
		sleep(1)
		if globals.PEER_SERVER_STATUS == 1: break
		elif globals.PEER_SERVER_STATUS == -1: return -1

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
		#print("search: retreives list of registered files")
		print("exit: exits the program")
		print("linear: changes the topology to be linear")
		print("broadcast: changes the topolgy to be broadcast")
		print("topology: returns the current topology")
		print("----------------------------------------")

		requestedFile = input("What file do you want?\n")

		if requestedFile == 'exit':
			sock.close()
			globals.PEER_CLIENT_STATUS = -1
			break

		elif requestedFile == 'test.txt':
			test()
			
		elif requestedFile == 'linear':
			globals.TOPOLOGY = globals.SEARCH_FILES_LINEAR

		elif requestedFile == 'broadcast':
			globals.TOPOLOGY = globals.SEARCH_FILES_BROADCAST

		elif requestedFile == 'topology':
			print("The current topology is " + str(globals.TOPOLOGY)) #TODO fix this

		else:
			clientSearch(sock, requestedFile, 1)
			sock.close()
			sock = createClientSocket()
