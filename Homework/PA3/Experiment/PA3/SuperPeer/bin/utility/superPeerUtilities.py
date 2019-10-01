"""superPeerUtilities.py
  utility functions for superpeer

  Attributes:

  TODO:


   Author:
     Alec Buchanan - 10/2018

"""
import socket
import sys
import pickle

def sendACK(con):
    try:
        m = pickle.dumps(1)
        con.send(m)
        return 1
    except:
        print("[ERROR] Super Peer: Super Peer: Failed to send")
        return -1
