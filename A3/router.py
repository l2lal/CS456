import sys
import socket
from socket import *
import time
import struct
from collections import defaultdict
from collections import deque, namedtuple
import logging
import os

NBR_ROUTER = 5
NUM_INPUTS = 4

#Function Check_Inputs - validates the inputs
#Parameters: 2
#	$1: all the arguments passed in from the terminal
#Return: None
def Check_Inputs(args):
	

	if len(args) != NUM_INPUTS:
		print "Improper number of arguments"
		exit(1)
	
	try:
		req_code = int(args[0])

	except:
		print "Improper formatting of argument", args
		exit(1)

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

#Hello Packet
class pkt_HELLO(object):
	def __init__(self, id, link):
		self.router_id = id
		self.link_id = link

#LSPDU Packet
class pkt_LSPDU(object):
	def __init__(self, sender, router_id, link, cost, via):
		self.sender = sender
		self.router_id = router_id
		self.link_id = link
		self.cost = cost
		self.via = via

#INIT Packet
class pkt_INIT(object):
	def __init__(self, id):
		self.router_id = id

#link_cost structure
class link_cost(object):
	def __init__(self, link, cost):
		self.link = link
		self.cost = cost

#circuit_db structure
class circuit_DB(object):
	def __init__(self):
		self.nbr_link = None
		self.linkcost[NBR_ROUTER] = link_cost()

#Router Class
class Router(object):
	def __init__(self,id):
		self.LSDB = defaultdict(list)
		self.id = id
		self.neighbor_list = []
		self.forwarded = []
		self.rib = defaultdict(list)
		self.edges = defaultdict(list)
		self.graph = None
		self.nbr_link = None

def Init_RIB(router):
	for rout in range(NBR_ROUTER):
		if(rout != router.id - 1):
			router.rib[rout] = [str(rout+1), "N/A", "INF"]

		elif(rout+1 == router.id):
			router.rib[rout] = [router.id, 'Local', 0]


#Function Create_UDP - creates router UDP socket
#Parameters: port to bind to
#Return: 2
#	$1: Handle to the router UDP socket
#	$2: router port
def Create_UDP(port):
	#Create server UDP Socket and listen to the negotiate port
	routerUDPSocket = socket(AF_INET, SOCK_DGRAM)
	routerUDPSocket.bind(('', port))
	routerUDPHost, routerPort = routerUDPSocket.getsockname()

	return (routerUDPSocket, routerPort)


#Function Send_Init - Sends INIT Packet to NSE
#Parameters: 5
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#	$2: <packet> init packet to send
#   $3: <nse_host> host name of nse
#   $4: <nse_port> port of nse
#   $5: <router> router handle
#Return: None
def Send_Init(routerUDPSocket, packet, nse_host, nse_port, router):
	#Set timeout value to ensure no system hanging; Creating timeout value of 1 minute
	#timeout = time.time() + 60
	#Listen for the request code
	print "Sending INIT..."
	buf = struct.pack('<I', packet.router_id)
	routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))
	logging.info('R' + str(router.id) + " sends an INIT: router_id " + str(packet.router_id))


#Function Wait_Init - wait for circuit_db from nse
#Parameters: 2
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#	$2: <router> handle to the router

#Return: 1
#   $1: <router> handle to the router to verify we received information
def Wait_Init(routerUDPSocket, router):
	while True: 
		receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)
		if(receive_pkt):
			break

	#serverUDPSocket.close()
	#print (len(receive_pkt))
	#origsize = struct.unpack('<%sI' % len(receive_pkt), receive_pkt)
	circuitDB = struct.unpack('<11I', receive_pkt)
	num_links = circuitDB[0]
	router.nbr_link = num_links
	logging.info('R' + str(router.id) + " receives a CIRCUIT_DB: nbr_link " + str(num_links))

	ind_count = 1;
	for i in range(0,num_links):
		link_ind = ind_count
		cost_ind = ind_count + 1
		#print link_ind, cost_ind
		router.LSDB[router.id-1].append([circuitDB[link_ind],circuitDB[cost_ind]])
		ind_count = ind_count + 2
		#router.neighbor_list.append[circuitDB[link_ind]]

	#PYTHON HOW TO APPEND TO LIST - WE WANT TO CREATE A CIRCUIT_DB and return that!
	return router

#Function Send_Hello - Sends HELLO Packet to neighbors
#Parameters: 4
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#   $2: <nse_host> host name of nse
#   $3: <nse_port> port of nse
#   $4: <router> router handle
#Return: None
def Send_Hello(routerUDPSocket, nse_host, nse_port, router):
	#print "Sending HELLO Packet..."
	for i in range(len(router.LSDB[router.id-1])):
		link_id = ((router.LSDB[router.id-1])[i])[0] 
		#create packet
		packet = pkt_HELLO(router.id,link_id)
		buf = struct.pack('<II', packet.router_id, packet.link_id)
		routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))
		logging.info('R' + str(router.id) + " sends a HELLO: router_id " + str(packet.router_id) + " link_id " + str(packet.link_id))

#Function Wait_Hello - Waits for return hellos from all neighbors in circuit_db
#Parameters: 2
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#   $2: <router> router handle
#Return: None
def Wait_Hello(routerUDPSocket, router):
	print "Waiting for Hellos..."
	while len(router.neighbor_list) != len(router.LSDB[router.id-1]): 
		receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)
		if(receive_pkt):
			if(len(receive_pkt) != 8):
				print "packet is not correct size..."
				continue
			#disect packet and get where it came from
			packet = struct.unpack('<II', receive_pkt)
			incoming_router_id = packet[0]
			via = packet[1]

			logging.info('R' + str(router.id) + " receives a HELLO: router_id" + str(incoming_router_id) + " link_id" + str(via))
			#print "Hello from ", incoming_router_id

			#add new neighbor to router's list for future communications
			Add_Neighbor(router, incoming_router_id, via)

	#print "Got everything, here's my neighbors: ", router.neighbor_list


#Function Send_LSPDU - Sends an LSPDU packet
#Parameters: 5
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#	$2: <router> router handle
#   $3: <nse_host> host name of nse
#   $4: <nse_port> port of nse
#   $5: <packet> LSPDU packet to send
#Return: None
def Send_LSPDU(routerUDPSocket, router, nse_host, nse_port, packet):
	buf = struct.pack('<5I', packet.sender, packet.router_id, packet.link_id, packet.cost, packet.via)
	routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))

#Function Send_ALL_LSPDU - Sends an LSPDU packet to all neighbors
#Parameters: 4
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#	$2: <router> router handle
#   $3: <nse_host> host name of nse
#   $4: <nse_port> port of nse
#Return: None
def Send_All_LSPDU(routerUDPSocket, router, nse_host, nse_port):
	sender = router.id
	for u in range(len(router.neighbor_list)):
		via = (router.neighbor_list[u])[1]
		for i in range(NBR_ROUTER):
			#for all router entries
			router_id = i + 1 #indexing is from 0, so offset
			for j in range(len(router.LSDB[i])):
				if len((router.LSDB[i])[j]) > 0:
					#for all link_cost entries in the router
					link = ((router.LSDB[i])[j])[0]
					cost = ((router.LSDB[i])[j])[1]
					linkcost = link_cost(link, cost)
					packet = pkt_LSPDU(sender, router_id, link, cost, via)
					Send_LSPDU(routerUDPSocket, router, nse_host, nse_port, packet)
					logging.info('R' + str(router.id) + " sends a LSPDU: sender" + str(sender) + " router_id " + str(router_id) + " link_id " + str(link) + " cost " + str(cost) + " via " + str(via))
					#print 'Sending a LS_PDU packet...'
				else:
					#router has no entries in this index of its LSDB
					continue

#Function Add_Neighbor - adds neighbor to router's safe sender list
#Parameters: 3
#	$1: <router> router handle
#	$2: <new_router_id> id of new router
#   $3: <via> link id used with this neighbor
#Return: None
def Add_Neighbor(router, new_router_id, via):
	#print "Adding Neighbor..."
	#neighbor_ind = new_router_id - 1 #shift to start from 0
	#router.LSDB[neighbor_ind].append([via,200])
	if [new_router_id,via] not in router.neighbor_list:
		router.neighbor_list.append([new_router_id,via])

	#print(router.neighbor_list)
	#print(router.LSDB)

#Function Check_Full - Checks if the router's LSPDU is complete
#Parameters: 1
#   $1: <router> router handle
#Return: Boolean - true if full, false otherwise
def Check_Full(router):
	num_vals = [2,3,3,2,4]
	for i in range(len(router.LSDB)):
		if len(router.LSDB[i]) != num_vals[i]:
			return False
	return True

# --------------------- DIJKSTRAS ALGORITHM - SOURCED FROM 	#https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc
# DIDNT WANT TO REINVENT THE WHEEL HERE, SORRY. 
# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')

def make_edge(start, end, cost=1):
  return Edge(start, end, cost)


class Graph:
    def __init__(self, edges):
        # let's check that the data is right
        wrong_edges = [i for i in edges if len(i) not in [2, 3]]
        if wrong_edges:
            raise ValueError('Wrong edges data: {}'.format(wrong_edges))

        self.edges = [make_edge(*edge) for edge in edges]

    @property
    def vertices(self):
        return set(
            sum(
                ([edge.start, edge.end] for edge in self.edges), []
            )
        )

    def get_node_pairs(self, n1, n2, both_ends=True):
        if both_ends:
            node_pairs = [[n1, n2], [n2, n1]]
        else:
            node_pairs = [[n1, n2]]
        return node_pairs

    def remove_edge(self, n1, n2, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        edges = self.edges[:]
        for edge in edges:
            if [edge.start, edge.end] in node_pairs:
                self.edges.remove(edge)

    def add_edge(self, n1, n2, cost=1, both_ends=True):
        node_pairs = self.get_node_pairs(n1, n2, both_ends)
        for edge in self.edges:
            if [edge.start, edge.end] in node_pairs:
                return ValueError('Edge {} {} already exists'.format(n1, n2))

        self.edges.append(Edge(start=n1, end=n2, cost=cost))
        if both_ends:
            self.edges.append(Edge(start=n2, end=n1, cost=cost))

    @property
    def neighbours(self):
        neighbours = {vertex: set() for vertex in self.vertices}
        for edge in self.edges:
            neighbours[edge.start].add((edge.end, edge.cost))

        return neighbours

    def dijkstra(self, source, dest):
        assert source in self.vertices, 'Such source node doesn\'t exist'
        distances = {vertex: inf for vertex in self.vertices}
        previous_vertices = {
            vertex: None for vertex in self.vertices
        }
        distances[source] = 0
        vertices = self.vertices.copy()

        while vertices:
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])
            vertices.remove(current_vertex)
            if distances[current_vertex] == inf:
                break
            for neighbour, cost in self.neighbours[current_vertex]:
                alternative_route = distances[current_vertex] + cost
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path
# -------END DIJKSTRAS ALGORITHM AND FUNCTIONS ---------------------

#Function Update_Graph - uses the updated LSPDU to generate a graph represented the cost between routers
#Parameters: 1
#	$1: <router> router handle
#Return: None
def Update_Graph(router):
	for i in range(len(router.LSDB)):
		a = i + 1
		for j in range(len(router.LSDB[i])):
			for k in range(len(router.LSDB)):
				if(k != i and ((router.LSDB[i])[j] in router.LSDB[k])):
					#if you find a match
					ind = (router.LSDB[k].index((router.LSDB[i])[j]))
					b = k + 1
					cost = ((router.LSDB[i])[j])[1]
					if ([a,b,cost] not in router.edges[0]): #and ([b,a,cost] not in router.edges[0]):
						router.edges[0].append([a, b, cost])

#Function Build_RIB - Builds an RIB by running dijkstra's algorithm on the router's graph member
#Parameters: 1
#	$1: <router> router handle
#Return: None
def Build_RIB(router):
	r_a = router.id
	source_in_edges = False
	for rout in range(NBR_ROUTER):
		dest_in_edges = False
		if(rout != router.id-1):
			r_b = rout + 1
			# Check if source node, r_a exists
			print(router.LSDB)
			print(router.edges[0])
			for check in range(len(router.edges[0])):
				if(r_a == ((router.edges[0])[check])[0]):
					source_in_edges = True
				if(r_b == ((router.edges[0])[check])[1]):
					dest_in_edges = True
					print ("source is in edges!")
			if (len(router.LSDB[rout]) > 0) and (len(router.LSDB[r_a-1]) > 0) and (len(router.edges[0]) > 0) and (source_in_edges) and (dest_in_edges):
				print("Dijkstra: passing in ", r_a, " and ", r_b)
				path = (router.graph.dijkstra(r_a, r_b))
				total_cost = 0 
				for i in range(len(path)-1):
					a = path[i]
					b = path[i+1]
					for j in range(len(router.edges[0])):
						if (((router.edges[0])[j])[0] == a) and (((router.edges[0])[j])[1] == b):
							total_cost = total_cost + ((router.edges[0])[j])[2]
							break

				router.rib[rout] = [r_b, path[1], total_cost] #[dest, first hop, cost]

		elif(rout+1 == router.id):
			router.rib[rout] = [r_a, 'Local', 0]


#Function Update_and_Forward_LSPDU - blocking call, continuously updates LSPDU and forwards packets until router LSPDU is full 
#Parameters: 4
#	$1: <routerUDPSocket> is the handle to a UDP Socket
#	$2: <router> router handle
#   $3: <nse_host> host name of nse
#   $4: <nse_port> port of nse
#Return: None
def Update_and_Foward_LSPDU(routerUDPSocket, router, nse_host, nse_port):
	updated = False
	count = 0

	while Check_Full(router) != True:
		receive_pkt, nseAddress = routerUDPSocket.recvfrom(1024)

		if(receive_pkt):
			if(len(receive_pkt) != 20):
				print "packet is not correct size...", len(receive_pkt)
				continue

		packet = struct.unpack('<5I', receive_pkt)

		sender = packet[0]
		router_id = packet[1]
		link_id = packet[2]
		cost = packet[3]
		via = packet[4]
		logging.info('R' + str(router.id) + " receives a LSPDU: sender" + str(sender) + " router_id " + str(router_id) + " link_id " + str(link_id) + " cost " + str(cost) + " via " + str(via))

		if [link_id,cost] not in router.LSDB[router_id - 1]:

			router.LSDB[router_id - 1].append([link_id,cost])
			sender = router.id

		else:
			count = count + 1
		
		for u in range(len(router.neighbor_list)):
			via = (router.neighbor_list[u])[1]
			if [router_id,link_id] not in router.forwarded:
				new_packet = pkt_LSPDU(sender, router_id, link_id, cost, via)
				Send_LSPDU(routerUDPSocket, router, nse_host, nse_port , new_packet)
				logging.info('R' + str(router.id) + " sends a LSPDU: sender" + str(sender) + " router_id" + str(router_id) + " link_id " + str(link_id) + " cost " + str(cost) + " via " + str(via))
				updated = True
				count = 0
				#print [router_id, link_id], router.forwarded
			#Send_All_LSPDU(routerUDPSocket, router, nse_host, nse_port)

		if(updated):
			router.forwarded.append([router_id, link_id])
			Update_Graph(router)
			router.graph = Graph(router.edges[0])
			Build_RIB(router)
			Print_RIB(router)
			Print_LSDB(router)
			#Run SPF Algorithm and put in RIB


	#print "Fully updated our LSPDU"

#Function Print_LSDB - prints updated LSDB in log file
#Parameters: 1
#	$1: <router> router handle
#Return: None
def Print_LSDB(router):
	logging.info("------- # START Topology Database -------")
	for i in range(len(router.LSDB)):
		for j in range(len(router.LSDB[i])):
			if j == 0:
				logging.info("R" + str(router.id) + " -> R" + str(i+1) + " nbr link " + str(len(router.LSDB[i])))

			link = ((router.LSDB[i])[j])[0]
			cost = ((router.LSDB[i])[j])[1]
			logging.info("R" + str(router.id) + " -> R" + str(i+1) + " link " + str(link) + " cost " + str(cost))
	logging.info("------- # END Topology Database -------")

#Function Print_RIB - prints updated RIB in log file
#Parameters: 1
#	$1: <router> router handle
#Return: None
def Print_RIB(router):
	logging.info("------- # START RIB -------")
	for i in range(len(router.rib)):
		dest = ((router.rib[i])[0])
		first_hop = ((router.rib[i])[1])
		tot_cost = ((router.rib[i])[2])
		logging.info("R" + str(router.id) + " -> " + str(dest) + " -> " + str(first_hop) + ", " + str(tot_cost))
	logging.info("------- # END RIB -------")	

#MAIN FUNCTION
def main():
	#validate inputs
	Check_Inputs(sys.argv[1:])

	#assign inputs to variables for later on
	router_id = int(sys.argv[1])
	nse_host = str(sys.argv[2])
	nse_port = int(sys.argv[3])
	router_port = int(sys.argv[4])

	#setup log file, removing existing one if necsesary
	filename = "router" + str(router_id) + ".log"
	try:
		os.remove(filename)
	except OSError:
		pass
	logging.basicConfig(filename=filename, level=logging.INFO)
	logging.info('Starting routing protocol for router ' + str(router_id))

	#create router:
	router = Router(router_id);
	Init_RIB(router)

	#Create UDP Socket
	routerUDPSocket, routerPort = Create_UDP(router_port)

	#creates and sends an init packet to NSE 
	init_pkt = pkt_INIT(router_id)
	Send_Init(routerUDPSocket, init_pkt, nse_host, nse_port, router)

	#wait for a circuit_DB from NSE
	router = Wait_Init(routerUDPSocket,router)
	if(not router):
		print "failed waiting for inits"
		exit(1)

	#send Hello messages to neighbors:
	Send_Hello(routerUDPSocket, nse_host, nse_port, router)

	#Waits for hellos from neighbors - assignment specs doesn't say whether to send LSPDU responses to hellos right away, so I wait for all neighbors to say hello
	Wait_Hello(routerUDPSocket, router)

	#sends a LSPDU back to all neighbors, since I know I've gotten hellos from them
	Send_All_LSPDU(routerUDPSocket, router, nse_host, nse_port)
	#print "Done sending PDUs"

	#Update LSPDUs 
	Update_and_Foward_LSPDU(routerUDPSocket,router,nse_host,nse_port)
	#print router.LSDB

	#Build a graph out of LSDB and from there use sourced DIJKSTRAS algorithm to build an RIB
	Update_Graph(router)
	router.graph = Graph(router.edges[0])
	Build_RIB(router)

	#Final prints
	logging.info("------- Final Prints -------")
	Print_LSDB(router)
	Print_RIB(router)
	logging.info("------- END OSPF -------")

	print "Finished"

	#pythontops.com/ python socket network programming
	#https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc

# Calling function
main()
