"""
	CS550
	Programming Assignment 1
	Alec Buchanan & Jason Lawrence
	
	main.py:
		starts the peer node including its client and server threads.
		
	Child Threads:
		server - spawns indexServer thread and connection handler thread. Also listens for peer clients trying to connect
		indexServer - spawned by server and keeps the index server updated on the local files
		connectionHandler - spawned by server and handles client connections
		client - Takes user input and asks peer server for files
		
	TODO:
	
	Updates:

	resources:
		https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
"""
#############################
##
##	importing libraries
##
#############################
import socket
from threading import Thread
from time import sleep
from queue import Queue
from os import listdir
import pickle
import sys
import os

#local files
from globals import * 
import server
import client



def main():
	""" The main function. The entry point for the program
		
		Args:
			
		Returns:
			
		Globals:
		
		Calls:
			server()
			client()
			
		Called By:
			cmd
			
		TODO:
			
		Updates:
	"""	
	print("Starting Peer")
	print("Starting Peer Server")
	peerServer = Thread(target = server.server)
	peerServer.daemon = True
	peerServer.start()
	clientThread = Thread(target = client.client)
	clientThread.daemon = True
	clientThread.start()
	while get_PEER_CLIENT_STATUS() >= 0:
		sleep(1)

if __name__ == '__main__':
    main()