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
	def __init__(self, sender, router_id, link, cost, via):
		self.sender = sender
		self.router_id = router_id
		self.link_id = link
		self.cost = cost
		self.via = via

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

	#serverUDPSocket.close()
	print (len(receive_pkt))
	#origsize = struct.unpack('<%sI' % len(receive_pkt), receive_pkt)
	circuitDB = struct.unpack('<11I', receive_pkt)
	num_links = circuitDB[0]
	ind_count = 1;
	for i in range(0,num_links):
		link_ind = ind_count
		cost_ind = ind_count + 1
		print link_ind, cost_ind
		router.LSDB[router.id-1].append([circuitDB[link_ind],circuitDB[cost_ind]])
		ind_count = ind_count + 2

	#PYTHON HOW TO APPEND TO LIST - WE WANT TO CREATE A CIRCUIT_DB and return that! 
	return router

def Send_Hello(routerUDPSocket, nse_host, nse_port, router):
	print "Sending HELLO Packet..."
	for i in range(len(router.LSDB[router.id-1])):
		link_id = ((router.LSDB[router.id-1])[i])[0] 
		#create packet
		packet = pkt_HELLO(router.id,link_id)
		buf = struct.pack('<II', packet.router_id, packet.link_id)
		routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))
	print "Finished first Hello"

def Wait_Hello(routerUDPSocket, router):
	print "Waiting for Hellos..."
	#while True: 
	receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)
	if(receive_pkt):
		#disect packet and get where it came from
		packet = struct.unpack('<II', receive_pkt)
		incoming_router_id = packet[0]
		via = packet[1]

		print "Hello from ", incoming_router_id
		#send a LSPDU back through this link
		Send_LSPDU(routerUDPSocket, router, incoming_router_id, via, nseAddress)

		#add new neighbor to router's list for future communications
		Add_Neighbor(router, incoming_router_id, via)

def Send_LSPDU(routerUDPSocket, router, incoming_router_id, via, nse_address):
	sender = router.id
	for i in range(NBR_ROUTER):
		#for all router entries
		print i
		router_id = i + 1 #indexing is from 0, so offset
		for j in range(len(router.LSDB[i])):
			if len((router.LSDB[i])[j]) > 0:
				#for all link_cost entries in the router
				link = ((router.LSDB[i])[j])[0]
				cost = ((router.LSDB[i])[j])[1]
				linkcost = link_cost(link, cost)
				packet = pkt_LSPDU(sender, router_id, link, cost, via)
				buf = struct.pack('<5I', packet.sender, packet.router_id, packet.link_id, packet.cost, packet.via)
				routerUDPSocket.sendto(str(buf).encode(), nse_address)
				print 'Sending a LS_PDU packet...'
			else:
				#router has no entries in this index of its LSDB
				continue

def Add_Neighbor(router, new_router_id, via):
	print "Adding Neighbor..."
	neighbor_ind = new_router_id - 1 #shift to start from 0
	router.LSDB[neighbor_ind].append([via,200])
	print(router.LSDB)


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
	Send_Hello(routerUDPSocket, nse_host, nse_port, router)

	Wait_Hello(routerUDPSocket, router)

	#while True:

	#pythontops.com/ python socket network programming

main()
