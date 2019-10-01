#############################
##
##	Global variables
##
#############################
PEER_SERVER_STATUS = 0	# -1 = failed, 0 = starting, 1 = running
PEER_SERVER_PORT = 9696

INDEX_SERVER_CONNECTION = 0 # -1 = failed, 0 = starting, 1 = running
INDEX_SERVER_IP   = "198.37.24.124"
INDEX_SERVER_PORT = 6001

P2P_PORT = 9696

LOCAL_SHARED_FILE_SPACE = "D:\\Users\\Jason\\Documents\\School\\ComputerScience\\CS550\\Homework\\PA2\\Peer\\SharedSpace"
LOCAL_FILE_LIST = []

#message commands
REMOVE_FILE 	= 0
ADD_FILE 		= 1
SEARCH_FILES 	= 2

PEER_CLIENT_STATUS = 0

def set_PEER_SERVER_STATUS(new):
	global PEER_SERVER_STATUS
	PEER_SERVER_STATUS = new
def get_PEER_SERVER_STATUS():
	global PEER_SERVER_STATUS
	return PEER_SERVER_STATUS
	

def set_PEER_CLIENT_STATUS(new):
	global PEER_CLIENT_STATUS
	PEER_CLIENT_STATUS = new
def get_PEER_CLIENT_STATUS():
	global PEER_CLIENT_STATUS
	return PEER_CLIENT_STATUS