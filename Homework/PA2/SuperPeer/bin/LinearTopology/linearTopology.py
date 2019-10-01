"""linearTopology.py
  This is the "api" for implementing the linear topology. Within this file there is an init function, a function to search for files, and a function to handle incoming connections

  Attributes:

  TODO:
   - record message IDs

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

#
# local imports
#
import GLOBALS
from classes import *
from utility import *


def init(localSearchForFile):
  """ intializes the linear topology setup and spawns a listener

    Args:
        localSearchForFile ([(char[15],int)] * (char[:])):    A pointer to a function that takes a file name as an arguemnt and returns a list of tuples that contain ip addresses and ports

    Returns:
      1:    success
      -1:    error

    Globals:
      none

    Calls:
      listener()

    Called By:


    TODO:
      none
    Updates:
      none

  """
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

  # Spawn thread to listen for incoming connections from neighbor
  superPeerListener = Thread(target = listener, args=[localSearchForFile])
  superPeerListener.daemon = True
  superPeerListener.start()
  return 1

def listener(localSearchForFile):
  """ Constantly listens for connections and only returns if socket fails

    Args:
        localSearchForFile ([(char[15],int)] * (char[:])):    A pointer to a function that takes a file name as an arguemnt and returns a list of tuples that contain ip addresses and ports

    Returns:
      -1:    error

    Globals:
      none

    Calls:
      none

    Called By:
      init()

    TODO:
      none
    Updates:
      none

  """
  for con in listenForConnection(GLOBALS.LOCAL_PORT):
    if con == -1: return -1

    if GLOBALS.DEBUG_MODE: print("[info] Linear lib: received connection")

    # spawn connection handler thread
    superPeer = Thread(target = superPeerConnection, args=[con, localSearchForFile])
    superPeer.daemon = True
    superPeer.start()

def findFileLinearly(filename):
  """  Starts the search for a file by asking the neighboring superpeer

    Args:
      filename (char[:]):    name of file to search for

    Returns:
      0:    success
      -1:    error

    Globals:
      GLOBALS.NEIGHBOR_IP
      GLOBALS.NEIGHBOR_PORT
      GLOBALS.TTL

    Calls:
      connectToSuperPeer
      receiveMessage
      generateUniqueID

    Called By:


    TODO:
      none
    Updates:
      none

  """
  #construct message
  id = generateUniqueID()
  msg = query(generateUniqueID(), GLOBALS.TTL, filename)

  #connect to neighbor
  neighbor = connectToSuperPeer(GLOBALS.NEIGHBOR_IP, GLOBALS.NEIGHBOR_PORT)
  if neighbor == -1: return -1
  if GLOBALS.DEBUG_MODE: print("[info] Linear lib: connected to neighbor")

  #send query
  sendMessage(neighbor, msg)

  #wait for query responces
  while True:
    responce = receiveMessage(neighbor)
    if responce == -1: break    # connection closed
    elif responce == 0: break	# connection shutdown
    yield responce
  neighbor.close()



def superPeerConnection(con, localSearchForFile):
  """ handles incoming connection from another super peer

    Args:
      con (socket.socket):                                    the connection object for the connection
      localSearchForFile ([(char[15],int)] * (char[:])):    the pointer to the function. better description provided in calling function

    Returns:
      1:    success
      0:    gracefully quiting
      -1:    error

    Globals:
      none

    Calls:
      receiveMessage
      localSearchForFile
      sendMessage
      connectToSuperPeer
      closeConnections

    Called By:


    TODO:
      - break up this function to make it cleaner and easier to read

    Updates:
      none

  """
  # Read message from neighbor
  message = receiveMessage(con)
  if message == -1: return -1
  elif message == 0: return 0

  # check owner of message
  if message.id in GLOBALS.SENT_MESSAGE_IDS:
    if GLOBALS.DEBUG_MODE: print("[info] Linear lib: loop detected. Received own message.")
    con.shutdown(socket.SHUT_RDWR)
    con.close()
    return 0

  #record query id
  if message.id not in GLOBALS.RECV_MESSAGE_IDS:
    GLOBALS.RECV_MESSAGE_IDS.append(message.id)
  else:
    if GLOBALS.DEBUG_MODE: print("[ERROR] Linear lib: loop detected")

  # get query hits on local leafs
  localMatches = localSearchForFile(message.fname)

  # Send query hits
  if len(localMatches) > 0:
    if GLOBALS.DEBUG_MODE: print("[info] Linear lib: " + str(len(localMatches)) + " query hit(s)")
    for match in localMatches:
      hit = queryHit(message.id, GLOBALS.TTL, message.fname, match[0], match[1])
      if sendMessage(con, hit) == -1:
        con.shutdown(socket.SHUT_RDWR)
        con.close()
        return -1

  # check TTL
  if message.TTL <= 0:
    if GLOBALS.DEBUG_MODE: print("[info] Linear lib: End of TTL, closing connection")
    con.shutdown(socket.SHUT_RDWR)
    con.close()
    return 1
  message.TTL = message.TTL - 1

  # Open connection with neighbor
  leftNeighbor = connectToSuperPeer(GLOBALS.NEIGHBOR_IP, GLOBALS.NEIGHBOR_PORT)
  if leftNeighbor == -1:
    print("[ERROR] Linear lib: Unable to forward message to neighbor.")
    closeConnections(leftNeighbor, con)
    return -1

  # forward query to neighbor
  if sendMessage(leftNeighbor, message) == -1:
    print("[ERROR] Linear lib: Unable to forward message to neighbor.")
    closeConnections(leftNeighbor, con)
    return -1

  #listen for query hits that need to be forwarded
  while True:
    message = receiveMessage(leftNeighbor)
    if message == -1 or message == 0:
      # query reached the end of query hit
      closeConnections(leftNeighbor, con)
      return 1

    #check queryhit TTL
    if message.TTL <= 0: continue
    else: message.TTL = message.TTL - 1

    if sendMessage(con, message) == -1:
      # For some reason the right neighbor connection failed
      closeConnections(leftNeighbor, con)
      return -1
