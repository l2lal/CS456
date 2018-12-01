import sys
import socket
from socket import *
import time
import struct
from collections import defaultdict

NBR_ROUTER = 5
NUM_INPUTS = 4

def Check_Inputs(args):
	

	if len(args) != NUM_INPUTS:
		print "Improper number of arguments"
		exit(1)
	
	try:
		req_code = int(args[0])

	except:
		print "Improper formatting of argument", args
		exit(1)

	#try:
		#if (isinstance(args[1], basestring) == True):
		#	socket.inet_aton(args[1])
		#else:
		#	print "Not a string"
	    # legal
	#except:
	 #   print "Invalid IP"
	  #  exit(1)

	try:
		arg3 = int(args[2])

	except:
		print "Improper formatting of argument", args
		exit(1)

	try:
		arg4 = int(args[3])

	except:
		print "Improper formatting of argument", args
		exit(1)

	return 

class pkt_HELLO(object):
	def __init__(self, id, link):
		self.router_id = id
		self.link_id = link

class pkt_LSPDU(object):
	def __init__(self):
		self.sender = None
		self.router_id = None
		self.link_id = None
		self.cost = None
		self.via = None

class pkt_INIT(object):
	def __init__(self, id):
		self.router_id = id

class link_cost(object):
	def __init__(self, link, cost):
		self.link = link
		self.cost = cost

class circuit_DB(object):
	def __init__(self):
		self.nbr_link = None
		self.linkcost[NBR_ROUTER] = link_cost()

class Router(object):
	def __init__(self,id):
		self.LSDB = defaultdict(list);
		self.neighbors = 0
		self.id = id




#Function Create_UDP - creates server UDP socket
#Parameters: 0
#Return:
#	$1: <serverUDPSocket> handle to UDP Socket
#	$2: <neg_port> UDP port
def Create_UDP(port):
	#Create server UDP Socket and listen to the negotiate port
	routerUDPSocket = socket(AF_INET, SOCK_DGRAM)
	routerUDPSocket.bind(('', port))
	routerUDPHost, routerPort = routerUDPSocket.getsockname()

	return (routerUDPSocket, routerPort)

def Send_Init(routerUDPSocket, packet, nse_host, nse_port):
	#Set timeout value to ensure no system hanging; Creating timeout value of 1 minute
	#timeout = time.time() + 60

	#Listen for the request code
	print "Sending INIT Packet..." 
	buf = struct.pack('<I', packet.router_id)
	routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))

def Wait_Init(routerUDPSocket, router):
	while True: 
		receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)
		if(receive_pkt):
			break

		# if receive_pkt.decode().nbr_link <= str(NBR_ROUTER): # code isn't correct, keep listening
		# 	print "Invalid request code"
		# 	if time.time() > timeout:
		# 		print "Timed out waiting for request code"
		# 		got_msg = False
		# 		exit(1)

		# 	else: #code is correct, let's do stuff
		# 		print "Something received"
		# 		got_msg = True
		# 		break

	#serverUDPSocket.close()
	print (len(receive_pkt))
	#origsize = struct.unpack('<%sI' % len(receive_pkt), receive_pkt)
	circuitDB = struct.unpack('<11I', receive_pkt)
	num_links = circuitDB[0]
	print (circuitDB)
	# ind_count = 4;
	# for i in range(0,num_links):
	# 	link_ind = ind_count
	# 	cost_ind = ind_count + 4
	# 	print link_ind, cost_ind
	# 	router.LSDB[0].append([circuitDB[link_ind],circuitDB[cost_ind]])
	# 	ind_count = ind_count + 8

	#print "num links.. = ", origsize[0]
	#print "link 1, cost 1: ", origsize[4], origsize[8]
	#PYTHON HOW TO APPEND TO LIST - WE WANT TO CREATE A CIRCUIT_DB and return that! 
	return router

def Send_Hello(routerUDPSocket, nse_host, nse_port, router):
	print "Sending HELLO Packet..."
	for i in range(len(router.LSDB[0])):
		link_id = ((LSDB[0])[i])[0] 
		#create packet
		packet = pkt_HELLO(router.id,link_id)
		buf = struct.pack('<II', packet.router_id, packet.link_id)
		routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))
	print "Finished first Hello"

def Wait_Hello(routerUDPSocket, router):
	print "Waiting for Hellos..."
	while True: 
		receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)
		if(receive_pkt):
			#disect packet and get where it came from
			via = 0
			Send_LSPDU(via)


def Send_LSPDU(routerUDPSocket, router, via):
	sender = router.id
	for i in range(len(router.LSDB)):
		#for all router entries
		router_id = router.LSDB[i] + 1 #indexing is from 0, so offset
		for j in range(len(router.LSDB[i])):
			#for all link_cost entries in the router
			link = ((router.LSDB[i])[j])[0]
			cost = ((router.LSDB[i])[j])[1]
			linkcost = link_cost(link, cost)
			packet = pkt_LSPDU(sender, router_id, link, cost, via)

def main():
	#validate inputs
	Check_Inputs(sys.argv[1:])

	#assign inputs
	router_id = int(sys.argv[1])
	nse_host = str(sys.argv[2])
	nse_port = int(sys.argv[3])
	router_port = int(sys.argv[4])

	timeout = time.time() + 60 * 5

	#create router:
	router = Router(router_id); 
	#Create UDP Socket
	routerUDPSocket, routerPort = Create_UDP(router_port)

	#send 5 INIT packets to emulate 5 routers, need a way to make these LITTLE-ENDIAN 
	init_pkt = pkt_INIT(router_id)
	Send_Init(routerUDPSocket, init_pkt, nse_host, nse_port)

	#wait for a circuit_DB
	router = Wait_Init(routerUDPSocket,router)
	if(router):
		print router.LSDB
	else:
		print "fail"

	#send Hello messages to neighbors:
	#Send_Hello(routerUDPSocket, nse_host, nse_port, router)

	#Wait_Hello

	#while True:

	#pythontops.com/ python socket network programming

main()
