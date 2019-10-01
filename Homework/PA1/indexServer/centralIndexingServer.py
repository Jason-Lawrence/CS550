import socket
import sys
import pickle
from queue import Queue 
from _thread import *
import threading

grid = [[]]  ##Will end up being a list of lists. Each of the lists will represent a peer. The first
addresses = [] ##List of IP Addresses
count = 0 ## Number of Peers registered with the Index Server

##Prints all of the files that are registered with the server
def printPeer(peerID):
	print("PRINTING ALL FILES ON THE PEER")
	for x in range(1, len(grid[peerID])):
		print("Filename: " + grid[peerID][x])
	#print("END")
		
def printGrid(): 
	print("PRINTING ALL FILES ON THE GRID")
	for y in range(len(grid)):
		print("Files stored at peer: " + str(y))      ##prints out the the peerID
		for x in range(1, len(grid[y])):              ##Iterates through the file list for each peer
			print("Filename: " + grid[y][x])
	print("END OF FILES")
	
def sendCatalog(con):
	files = []
	#Get list of files
	for peer in grid:
		for file in range(1,len(peer)):
			if peer[file] not in files: files.append(peer[file])
	#convert list to string
	msg = ""
	for file in files:
		msg = msg + file + "\n"
	try:
		con.send(str.encode(msg))
	except socket.error as err:
		print("Failed to send catalog")
	
##Deletes a Peer from the Server

def removePeerFromGrid(addr):
	global count
	if addr in grid:
		grid.remove(addr)                             ##removes the peer and file list from the server
		addresses.remove(addr)                        ##deletes the peer from the server
		count -= 1 
	printGrid()
	return
##Registers a peer with the server
	
def addPeerToGrid(addr): 
	global count
	if addr not in grid:
		if count != 0: 
			grid.append([])
			grid[count].insert(0, addr)
			count += 1
		else:
			grid[count].insert(0, addr)
			count += 1
	else:
		print("Peer already in grid")
		return

""" Adds a file to the peer by finding the peerID by locating the index of the IP address 
	stored in the addresses list and then appends the filename to the end of the list
"""
def add(con, filename): 
	peerID = 0 
	addr = con.getpeername() ##get the address from the socket object 
	if addr[0] in addresses:
		for i in range(len(addresses)): 
			if addr[0] == addresses[i]: ##find the index and therefore the peerID.
				peerID = i
				break
		if filename not in grid[peerID]: 
			grid[peerID].append(filename) ##append the file if not already in the list.
	else:
		print("INVALID CONNECTION") ##If the IP address isn't registered with the server then thier is an invalid connection 
	#printPeer(peerID)
	
## Removes file from peer

def remove(con, filename):
	peerID = 0
	addr = con.getpeername()     ##get the address from the socket object
	if addr[0] in addresses:
		for i in range(len(addresses)):
			if addr[0] == addresses[i]:  ##find the index and therefore the peerID.
				peerID = i
				break
	else:
		print("Invalid Connection")
		return
		
	if filename in grid[peerID]:
		grid[peerID].remove(filename) ##Remoive the file if the file exists.
	else:
		print("Invalid filename: " + filename)
	printPeer(peerID)
	return

##Searches all of the peers for the Given FileName and returns a lit of peers that have that file.
##If file is not found sends an empty list.
	
def search(con, filename):	
	peers = []  ##list of peers that have the filename
	for x in range(len(grid)):
		for y in range(len(grid[x])): ##iterates through each peer's file list looking for a match
			if grid[x][y] == filename:
				peers.append(addresses[x]) ##append the IP address of the peers that have the file. 
				#print("Peer: " + str(x) + " has the file: " + filename) not neccissarily true yet
	msg = pickle.dumps(peers) ##Serializes the message before it is sent.
	con.sendall(msg) ##Sends the message containing a list of IP addresses that have the file. 
	con.close() ##Close the connection
	return
				
	
				
def thread(con):
	global count
	x = 0
	addr = con.getpeername()
	status = []
	filename = []
	while True:
		try:
			data = con.recv(1024)
		except socket.error as err:
			print("Client disconnected")
			return
		try:
			data = pickle.loads(data)
		except:
			print("Client exited")
			return
		if not data:
			print('End')
			removePeerFromGrid(addr[0])
			con.close()
			break
		status = data[0]
		filename = data[1]
		if status == 0:
			print("Removing file: " + filename)
			remove(con, filename)
			m = pickle.dumps(1)
			con.send(m)
		elif status == 1:
			print("ADDING FILE: " + filename)
			add(con, filename)
			m = pickle.dumps(1)
			con.send(m)
		elif status == 2:
			print("Searching for file: " + filename)
			search(con, filename)
		elif status == 3:
			print("Sending file catalog")
			sendCatalog(con)
	con.close()
	print("Client Disconnected")

def main():
	print('Starting Central Indexing Server')
	port = 6001
	host = ""
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		soc.bind((host, port))
	except soc.error:
		print("Binding failed")
		sys.exit()
	
	soc.listen(80)
	
	print("socket is now active")
	
	while True:
		con, addr = soc.accept()
		if addr[0] not in addresses:
			addresses.append(addr[0])
			addPeerToGrid(addr[0])
		print('Connected to :', addr[0], ':', addr[1])
		start_new_thread(thread, (con,))
	
	soc.close()
	
if __name__ == '__main__':
	main()

