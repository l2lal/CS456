import sys
import socket
from socket import *
import time
import struct
from collections import defaultdict
from collections import deque, namedtuple

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
		self.LSDB = defaultdict(list)
		self.id = id
		self.neighbor_list = []
		self.forwarded = []
		self.rib = defaultdict(list)
		self.spf_link = []
		self.edges = defaultdict(list)
		self.graph = None



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
		#router.neighbor_list.append[circuitDB[link_ind]]

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

			print "Hello from ", incoming_router_id

			#add new neighbor to router's list for future communications
			Add_Neighbor(router, incoming_router_id, via)

	print "Got everything, here's my neighbors: ", router.neighbor_list

def Send_LSPDU(routerUDPSocket, router, nse_host, nse_port, packet):
	buf = struct.pack('<5I', packet.sender, packet.router_id, packet.link_id, packet.cost, packet.via)
	routerUDPSocket.sendto(str(buf).encode(), (nse_host, nse_port))

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
					print 'Sending a LS_PDU packet...'
				else:
					#router has no entries in this index of its LSDB
					continue

def Add_Neighbor(router, new_router_id, via):
	print "Adding Neighbor..."
	#neighbor_ind = new_router_id - 1 #shift to start from 0
	#router.LSDB[neighbor_ind].append([via,200])
	if [new_router_id,via] not in router.neighbor_list:
		router.neighbor_list.append([new_router_id,via])

	print(router.neighbor_list)
	#print(router.LSDB)

def Check_Full(router):
	num_vals = [2,3,3,2,4]
	for i in range(len(router.LSDB)):
		if len(router.LSDB[i]) != num_vals[i]:
			return False
	return True

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

def Build_RIB(router):
	r_a = router.id
	for rout in range(NBR_ROUTER):
		if(rout != router.id-1):
			r_b = rout + 1
			path = (router.graph.dijkstra(r_a, r_b))
			total_cost = 0 
			for i in range(len(path)-1):
				a = path[i]
				b = path[i+1]
				for j in range(len(router.edges[0])):
					if (((router.edges[0])[j])[0] == a) and (((router.edges[0])[j])[1] == b):
						total_cost = total_cost + ((router.edges[0])[j])[2]
						break

			router.rib[rout] = [r_b, path[1], total_cost] #[dest, path, cost]

		else:
			router.rib[rout] = [r_a, 'Local', 0]

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
				updated = True
				count = 0
				#print [router_id, link_id], router.forwarded
			#Send_All_LSPDU(routerUDPSocket, router, nse_host, nse_port)

		if(updated):
			router.forwarded.append([router_id, link_id])
			#Run SPF Algorithm and put in RIB


	print "Fully updated our LSPDU"

def main():
	#validate inputs
	Check_Inputs(sys.argv[1:])

	#assign inputs
	router_id = int(sys.argv[1])
	nse_host = str(sys.argv[2])
	nse_port = int(sys.argv[3])
	router_port = int(sys.argv[4])

	#setup log file
	filename = "router(" + str(router_id) + ").log"
	logging.basicConfig(filename=filename, level=logging.INFO)
	logging.info('Starting routing protocol for router' + str(router_id))


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

	#Waits for hellos from neighbors - assignment specs doesn't say whether to send LSPDU responses to hellos right away
	Wait_Hello(routerUDPSocket, router)

	#sends a LSPDU back to its neighbors
	Send_All_LSPDU(routerUDPSocket, router, nse_host, nse_port)
	print "Done sending PDUs"
	#Update LSPDUs 
	Update_and_Foward_LSPDU(routerUDPSocket,router,nse_host,nse_port)
	#print router.LSDB

	Update_Graph(router)
	router.graph = Graph(router.edges[0])
	Build_RIB(router)
	print(router.rib)

	#path = (router.graph.dijkstra(4, 2))


	#while True:

	#pythontops.com/ python socket network programming
	#https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc

main()
