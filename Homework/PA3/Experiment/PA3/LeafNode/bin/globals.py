#############################
##
##	Global variables
##
#############################
def globalInit():
	global PEER_SERVER_STATUS, CONSISTENCY, PEER_SERVER_PORT, PEER_ID, INDEX_SERVER_CONNECTION, INDEX_SERVER_IP, INDEX_SERVER_PORT, MASTER_FILE_SPACE, CACHED_FILE_SPACE, MASTER_FILE_LIST, CACHED_FILE_LIST, REMOVE_FILE, ADD_MASTER, ADD_CACHE, SEARCH_FILES_BROADCAST, SEARCH_FILES_LINEAR, PEER_CLIENT_STATUS, TOPOLOGY, VERSION_RECORDER, TTR, RESULT_FILE, TEST, TEST_STATUS
	PEER_SERVER_STATUS = 0
	INDEX_SERVER_CONNECTION = 0
	PEER_ID = -1
	MASTER_FILE_LIST = []
	CACHED_FILE_LIST = []
	REMOVE_FILE 	= 0
	ADD_MASTER 		= 1
	ADD_CACHE         = 2
	SEARCH_FILES_BROADCAST 	= 3
	SEARCH_FILES_LINEAR = 4
	PEER_CLIENT_STATUS = 0
	TOPOLOGY = SEARCH_FILES_BROADCAST
	VERSION_RECORDER = {}
	TTR = 5
	CONSISTENCY = "PULL"
	RESULT_FILE = ""
	TEST = -1
	TEST_STATUS = 0