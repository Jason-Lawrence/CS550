######################################################
#
#					NOTICE!!
#		This file was not meant to be part of the
#		assignment. This file is purely for 
#		administrative work. please ignore this file
#
######################################################

import os
y = 0
for x in range(20):
	if x%2 == 0 and x>1:
		y+=1
	filename = "peer" + str(x) + ".conf"
	config = open(filename, 'w+')
	config.write("PEER_SERVER_PORT = " + str(4000 + x) + "\n")
	config.write("INDEX_SERVER_IP = 198.37.24.124\n")
	config.write("INDEX_SERVER_PORT = " + str(5000+y) + "\n")
	path = "C:\\Users\\abuch\\Desktop\\PA2\\LeafNode\\SharedSpace\\SharedSpace" + str(x)
	#os.mkdir(path)
	config.write("LOCAL_SHARED_FILE_SPACE = D:\\Users\\Jason\\Documents\\School\\ComputerScience\\CS550\\Homework\\PA2\\tmp\\PA2\\LeafNode\\SharedSpace\\SharedSpace" + str(x))
										  ##C:\\Users\\abuch\\Desktop\\PA2\\LeafNode\\SharedSpace\\SharedSpace
	                                      ##D:\\Users\\Jason\\Documents\\School\\ComputerScience\\CS550\\Homework\\PA2\\LeafNode\\SharedSpace\\SharedSpace0
	