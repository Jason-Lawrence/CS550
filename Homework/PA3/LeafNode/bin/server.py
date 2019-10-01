import socket
from threading import Thread
from time import sleep
from queue import Queue
from os import listdir
import pickle
import sys
import os
import globals
from datetime import *

sys.path.append('.\\utility')
from networkMessages import *

sys.path.append('.\\pullLib')
import pullServer



def versionControlHandler(msg):
    """Removes Invalid files
        Args:
            msg    (versionControl)  - message object that holds information needed to maintain consistency
            
        Returns:
            0      - returns 0 on completion regardless of error
            
    
    TODO:
        Check file version first before delete
    
    """
    filename = msg.filename
    newVersion = msg.version
    filePath = globals.CACHED_FILE_SPACE + "\\" + filename
    if os.path.isfile(filePath):
        os.remove(filePath)
    else:
        print("File not found")
    return 0

def sendMessagesToIndex(sock, messages):
    """ sends messages from specified format over socket

        Args:
            sock (socket.socket):    socket with established connection
            messages ((I4,C)[:]):    a list of tupples containing a command and message

        Message:
            command:    0 means removed, 1 means add
            message:    the file name

        Returns:
            -1 - error
            1  - success

        Calls:
            void

        Called By:
            indexServer()

    """
    for msg in messages:
        print("+ Peer Server: Sending " + str(type(msg).__name__) + " on file " + msg.filename)
        m = pickle.dumps(msg)
        try:
            sock.send(m)
            data = sock.recv(1024)
            if data == b'':
                print("[ERROR] Peer Server: Super peer connection closed.")
        except socket.error as err:
            print("[ERROR] Peer Server: Super peer connection closed.")
            return -1
    return 1

"""
    TODO!!!!!!!!!!!!!
    1. add documentation
    2. save VERSION_RECORDER to file
    3. add a way to detect offline edits to file and maintain dictionary consistency
    4. break this function up into subroutines so its not as messy
"""
def diffInSharedSpace(previous, dir):
	def generateVerNum(time):
		time = str(time).replace(".", "")
		return int(time)

	addedFiles = []                #aka current files
	currentFiles = []
	removedFiles = previous                    #aka previously recorded files
	messages = []
	#TODO: this can be a lot more efficient

	#get list of current files
	for file in listdir(dir):
		addedFiles.append((file, os.stat(dir + "\\" + file).st_mtime))## Jason Look here

	#Ignore unchanged files
	commonFiles = []
	for file in addedFiles:
		if file in removedFiles:
			commonFiles.append(file)
	for file in commonFiles:
		addedFiles.remove(file)
		removedFiles.remove(file)

	# Check version control
	for addedFile in addedFiles:
		for removedFile in removedFiles:
			if addedFile[0] == removedFile[0]:
				if dir == globals.CACHED_FILE_SPACE:
					os.remove(dir + "\\" + addedFile[0])
					addedFiles.remove(addedFile)
				else:
					globals.VERSION_RECORDER[addedFile[0]].version += 1
					invalid = versionControl(globals.VERSION_RECORDER[addedFile[0]].version, addedFile[0], addedFile[1])
					messages.append(invalid)
					addedFiles.remove(addedFile)    #TODO: fix this, could cause errors when deleting from list that is being iterated over
					removedFiles.remove(removedFile)
				break
	#TODO: throws error if cached dir is not empty on start up. its because there is no version record for it
	for file in addedFiles:
		if dir == globals.MASTER_FILE_SPACE:
			globals.VERSION_RECORDER[file[0]] = fileMetaData(os.path.getsize(dir + "\\" + file[0]), socket.gethostbyname(socket.gethostname()), globals.PEER_SERVER_PORT, globals.TTR, 1, True, 0)
			register = fileRegistration(globals.ADD_MASTER, file[0], globals.VERSION_RECORDER[file[0]].version, file[1])
		else:
			register = fileRegistration(globals.ADD_CACHE, file[0], globals.VERSION_RECORDER[file[0]].version, file[1])
		messages.append(register)

	for file in removedFiles:
		register = fileRegistration(globals.REMOVE_FILE, file[0], 1, file[1]) # TODO: unhardcode the 1
		try:
			del globals.VERSION_RECORDER[file[0]]
		except:
			a = 4
		messages.append(register)

	#get list of current files
	for file in listdir(dir):
		currentFiles.append((file, os.stat(dir + "\\" + file).st_mtime))
	return (currentFiles, messages)

def connectToIndexServer():
    """ Establishes connection with index server

        Args:
            void

        Returns:
            socket.socket     - On success, returns socket with connection to index server
            -1                - Error connecting to index server

        Globals:
            INDEX_SERVER_CONNECTION
            INDEX_SERVER_IP
            INDEX_SERVER_PORT

        Calls:

        Called By:
            indexServer()

        TODO:

        Updates:
            8/19    - remove attemped connection loop and combine try statments so there will only be one return value
    """
    peerID = globals.PEER_ID
    serverPort = globals.PEER_SERVER_PORT
    try:
        sock = socket.socket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((globals.INDEX_SERVER_IP, globals.INDEX_SERVER_PORT))
        globals.INDEX_SERVER_CONNECTION = 1
    except socket.error as err:
        print("- Peer Server: Error connecting to index server!")
        globals.INDEX_SERVER_CONNECTION = -1
        return -1

    sock.send(pickle.dumps((peerID, serverPort)))
    res = sock.recv(80)
    res = pickle.loads(res)
    if res == peerID:
        return sock
    else:
        peerID = res
        globals.PEER_ID = peerID
        return sock

def indexServer():
    """ A thread that handles the connection with the index server. It also is in charge of keeping local files registered with index server

        Args:
            void

        Returns:
            0    - returns 0 on completion

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
            8/19    - lowered loop timer from 60s to 2s
    """
    #connect to index server
    sock = connectToIndexServer()
    if not isinstance(sock, socket.socket):
            print("- Peer Server: Gave up trying to connect to index server. Peer server shutting down.")
            return 0

    print("* Peer Server: Connected to index server")

    #TODO: make this event driven
    while 1:
        messages = []
        globals.MASTER_FILE_LIST, messages = diffInSharedSpace(globals.MASTER_FILE_LIST, globals.MASTER_FILE_SPACE)
        if sendMessagesToIndex(sock, messages) == -1: return -1
        messages = []
        globals.CACHED_FILE_LIST, messages = diffInSharedSpace(globals.CACHED_FILE_LIST, globals.CACHED_FILE_SPACE)
        if sendMessagesToIndex(sock, messages) == -1: return -1
        sleep(1)
    print("[ERROR] Peer Server: connection with super peer closed.")

def modifiyMetaData(meta):
    filesize = meta.filesize
    originIP = meta.originIP
    originPort = meta.originPort
    TTR = meta.TTR
    version = meta.version
    original = False
    experation = datetime.now() + timedelta(seconds = meta.TTR)
    return fileMetaData(filesize, originIP, originPort, TTR, version, original, experation)

def connectionHandler(con, addr):
    """ A thread that handles the connection with each individual client.
        The protocol is a three step protocol:
        1.  receive file name
              - looks for file and gets file size
        2.     send file size
              - if file does not exist, a file size of 0 is sent
        3.     send the file

        Args:
            con (socket.socket)    - The socket with an open connection to the client
            addr (Str)            - The address of the client

        Returns:
            0    - returns 0 on error or completion

        Globals:

        Calls:

        Called By:
            server()

        TODO:
            clean and comment

        Updates:
    """
    #get filename
    msg = con.recv(1024)
    msg = pickle.loads(msg)

    #look for file sent by message
    if pullServer.consistencyHandler(msg, con) != 0:
        return 1

    if msg in globals.VERSION_RECORDER:
        try:
            modifiedMetaData = modifiyMetaData(globals.VERSION_RECORDER[msg])
            con.send(pickle.dumps(modifiedMetaData))
        except socket.error as err:
            print("[ERROR] Peer Server: Failed to respond to file request.")
            return -1
    else:
        if msg in listdir(globals.MASTER_FILE_SPACE) + listdir(globals.CACHED_FILE_SPACE):
            print("[ERROR] Peer Server: Missing meta data for file " + str(msg))
        else:
            print("- Peer Server: client asked for nonexisting file")
        metaData = fileMetaData(0, "127.0.0.1", 1234, globals.TTR, 0, False, datetime.now())
        con.send(pickle.dumps(metaData))
        con.close()
        return 0



    #do a con.send for the file
    metaData = globals.VERSION_RECORDER[msg]
    directory = ""
    if metaData.original:
        directory = globals.MASTER_FILE_SPACE
    else:
        directory = globals.CACHED_FILE_SPACE
    with open(directory + "\\" + msg, 'rb') as file:
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
            -1     - returns -1 on failure

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
    # Create connection with index server
    print("* Peer Server: connecting to index server...")
    indexServerThread = Thread(target = indexServer)
    indexServerThread.start()

    # Wait for connection with index server
    while globals.INDEX_SERVER_CONNECTION == 0:
        sleep(1)
        if globals.INDEX_SERVER_CONNECTION == 1: break
        if globals.INDEX_SERVER_CONNECTION == -1:
            globals.PEER_SERVER_STATUS = -1
            exit()
            return -1


    # Create socket for Peer Server
    try:
        sock = socket.socket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', globals.PEER_SERVER_PORT))
        sock.listen(5)
        print("+ Peer Server: Now listening for other peers")
    except socket.error as err:
        print("- Peer Server: Error setting up server")
        print(err)
        globals.PEER_SERVER_STATUS = -1
        exit()
        return -1

    # Listen for clients
    globals.PEER_SERVER_STATUS = 1
    while True:
        con, addr = sock.accept()
        connection = Thread(target = connectionHandler, args = (con,addr))
        connection.start()
    sock.close()
