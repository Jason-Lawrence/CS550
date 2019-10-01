"""
	Jason Lawrence - A20381993
	Alec Buchanan - A
	
"""
import sys
sys.path.append('.\\LinearTopology')

import linearTopology
import utility
from classes import *

from _thread import *
import threading
from threading import Thread
from time import sleep
import superPeer


 
def main():
	"""Main function. Starts the thread that is responsible for starting the Super Peer.
	
		Args:
			None
		
		Returns:
			None
			
		Globals:
			None
			
		Calls:
			superPeer.main()
			linearTopology.init()
			
		Called by:
	
	"""
	if linearTopology.init(superPeer.searchLocal) <= 0: return
	
	SuperPeerThread = Thread(target = superPeer.main)
	SuperPeerThread.daemon = True
	SuperPeerThread.start()
	while True:
		sleep(1)
	
		
if __name__ == '__main__':
	main()