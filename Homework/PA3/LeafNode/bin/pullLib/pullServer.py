"""pullServer.py
  provides file consistency through polling

  Attributes:

  TODO:


   Author:
     Alec Buchanan - 10/2018

"""
import sys
sys.path.append('..\\utility')
sys.path.append('..\\')
from networkMessages import *
import globals
from threading import Thread
import socket
import pickle
import os

def consistencyHandler(poll, con):

    response = -1   # file is out of date
    if not isinstance(poll,versionControl):
        return 0
    filePath = globals.CACHED_FILE_SPACE + "\\" + poll.filename
    if os.path.isfile(filePath):
        os.remove(filePath)
        return 1
    if poll.filename not in globals.VERSION_RECORDER:
        response = -2   # file no longer exists
    elif globals.VERSION_RECORDER[poll.filename].version == poll.version:
        response = globals.VERSION_RECORDER[poll.filename].TTR # new TTR
    try:
        con.send(pickle.dumps(response))
        con.close()
    except socket.error as err:
        print("[ERROR] Pull Server: Failed to respond to version request.")
        return -1
    return 1
