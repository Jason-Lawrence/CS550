"""pullClient.py
  provides file consistency through polling

  Attributes:

  TODO:


   Author:
     Alec Buchanan - 10/2018

"""

import sys
from datetime import *
sys.path.append('..\\utility')
sys.path.append('..\\')
from networkMessages import *
import globals
from threading import Thread
import socket
from time import sleep
import pickle
import os





def init():
    pullListener = Thread(target = validator)
    pullListener.daemon = True
    pullListener.start()

def validator():
    while True:
        file = getNextExpiration()
        if file == 0:
            sleep(globals.TTR)
            continue
        # find the next expiring TTR
        #sleep until TTR expires
        waitTime = globals.VERSION_RECORDER[file].experation - datetime.now()
        waitTime = waitTime.total_seconds()
        if waitTime > 0: sleep(waitTime)
        # ask peer server new TTR
        sock = createPullSocket()
        pollOrigin(file, sock)
        # if TTR is neg then file is out of Update
        # update TTR or del file
        msg = receiveResponse(sock)
        if msg == -2 or msg == -1:
            os.remove(globals.CACHED_FILE_SPACE + "\\" + file)
            del globals.VERSION_RECORDER[file]
            print("[info] Pull Lib: Found out of date cached file " + file)
        elif msg > 0:
            #TODO: Add semiphore lock to prevent concurency issues
            globals.VERSION_RECORDER[file].TTR = msg
            globals.VERSION_RECORDER[file].experation = datetime.now() + timedelta(seconds = globals.VERSION_RECORDER[file].TTR)
        else:
            print("[ERROR] Pull Lib: client response error")

def createPullSocket():
    try:
        #connect to peer server
        sock = socket.socket()
        return sock
    except socket.error as err:
        print("[ERROR] Pull Lib: Client could not generate socket.")
        return -1


def getNextExpiration():
    #nextExpiration = next(iter(globals.VERSION_RECORDER))
    nextExpiration = 0
    for file, meta in globals.VERSION_RECORDER.items():
        if meta.original == False:
            if nextExpiration == 0:
                nextExpiration = file
            elif meta.experation < globals.VERSION_RECORDER[nextExpiration].experation:
                nextExpiration = file
    return nextExpiration

def receiveResponse(sock):
    try:
        msg = sock.recv(1024)
        msg = pickle.loads(msg)
        sock.close()
        return msg
    except socket.error as err:
        print("[ERROR] Pull Lib: Client could not poll origin server")
        return -1

def pollOrigin(file, sock):
    msg = versionControl(globals.VERSION_RECORDER[file].version, file, os.stat(globals.CACHED_FILE_SPACE + "\\" + file).st_mtime)
    msg = pickle.dumps(msg)
    ip = globals.VERSION_RECORDER[file].originIP
    port = globals.VERSION_RECORDER[file].originPort
    try:
        sock.connect((ip, port))
        sock.send(msg)
    except socket.error as err:
        print("[ERROR] Pull Lib: Client could not poll origin server - " + str(err))
    return sock
