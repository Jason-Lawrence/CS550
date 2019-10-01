######################################################
#
#					NOTICE!!
#		This file was not meant to be part of the
#		assignment. This file is purely for 
#		administrative work. please ignore this file
#
######################################################

for x in range(10):
	y = 1
	filename = "superPeer" + str(x) + ".conf"
	config = open(filename, 'w+')
	config.write("LINEAR_LOCAL_PORT = " + str(8000+x) + "\n")
	config.write("LINEAR_NEIGHBOR_IP = 198.37.24.124\n")
	config.write("LINEAR_NEIGHBOR_PORT = " + str(8000 + x + y) + "\n")
	config.write("BROADCAST_SUPER_PEER_PORT = " + str(7000+x) + "\n")
	config.write("BROADCAST_SUPER_PEER_ID = " + str(x) +"\n")
	config.write("LEAF_NODE_PORT = " + str(5000 + x) + "\n")
	