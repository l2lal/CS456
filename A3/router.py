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
	def __init__(self):
		self.router_id = None
		self.link_id = None

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
	def __init__(self):
		self.link = None
		self.cost = None

class circuit_DB(object):
	def __init__(self):
		self.nbr_link = None
		self.linkcost[NBR_ROUTER] = link_cost()

class Router(object):
	def __init__(self):
		self.LSDB = defaultdict(list);
		self.neighbors = 0




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
	circuitDB = struct.unpack('<44B', receive_pkt)
	num_links = circuitDB[0]
	ind_count = 4;
	for i in range(0,num_links):
		link_ind = ind_count
		cost_ind = ind_count + 4
		print link_ind, cost_ind
		router.LSDB[0].append([circuitDB[link_ind],circuitDB[cost_ind]])
		ind_count = ind_count + 8

	#print "num links.. = ", origsize[0]
	#print "link 1, cost 1: ", origsize[4], origsize[8]
	#PYTHON HOW TO APPEND TO LIST - WE WANT TO CREATE A CIRCUIT_DB and return that! 
	return router

def Send_Hello(routerUDPSocket, packet, nse_host, nse_port):
	print "Sending HELLO Packet..."
	buf = struct.pack('<II', packet.router_id, packet.link_id)
	routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))

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
	router = Router(); 
	#Create UDP Socket
	routerUDPSocket, routerPort = Create_UDP(router_port)

	#send 5 INIT packets to emulate 5 routers, need a way to make these LITTLE-ENDIAN 
	init_pkt = pkt_INIT(router_id)
	Send_Init(routerUDPSocket, init_pkt, nse_host, nse_port)

	#wait for a return packet
	router = Wait_Init(routerUDPSocket,router)
	if(router):
		print router.LSDB
	else:
		print "fail"

	#send Hello messages:

	#while True:

	#pythontops.com/ python socket network programming

main()
