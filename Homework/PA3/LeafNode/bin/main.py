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
import globals
import server
import client

sys.path.append('.\\pullLib')
import pullClient

def getValueFromConfLine(line):
	return line.split("=")[1].strip()

def assignGlobals(conf):
	lines = conf.readlines()
	globals.globalInit()
	globals.PEER_SERVER_PORT = int(getValueFromConfLine(lines[0]))
	globals.INDEX_SERVER_IP = getValueFromConfLine(lines[1])
	globals.INDEX_SERVER_PORT = int(getValueFromConfLine(lines[2]))
	globals.MASTER_FILE_SPACE = getValueFromConfLine(lines[3])
	globals.CACHED_FILE_SPACE = getValueFromConfLine(lines[4])

def init():
	try:
    # Check command line arguements
		if len(sys.argv) != 2:
			print("Expected the config file as an arguement")
			return -1

		#get config file location
		confFile = sys.argv[1]

		#open config file
		with open(confFile, 'r') as conf:
			assignGlobals(conf)

	except EnvironmentError:
		print("Invalid config file given")
		return -1

	return 1

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
	init()
	peerServer = Thread(target = server.server)
	peerServer.daemon = True
	peerServer.start()
	clientThread = Thread(target = client.client)
	clientThread.daemon = True
	clientThread.start()
	stat = globals.PEER_CLIENT_STATUS
	if globals.CONSISTENCY == "PULL":
	    pullClient.init()
	while stat >= 0:
		sleep(1)
		stat = globals.PEER_CLIENT_STATUS

if __name__ == '__main__':
    main()
