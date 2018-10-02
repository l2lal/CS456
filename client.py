#CLIENT APPLICATION
#Computer Networks (CS 456)
#Number of parameters: 4
#Parameter:
#    $1: <server_address>
#    $2: <n_port>
#    $3: <req_code>
#    $4: message

# START UDP SOCKET TRANSACTION
import sys
import time
from socket import *

NUM_INPUTS = 4

#Function check_inputs(args):
#Parameters: 1
#	$1: <args> - all command line arguments minus script name
#Return: 0

def Check_Inputs(args):

	if len(args) != NUM_INPUTS:
		print "Improper number of arguments"
		exit(1)
	
	#if not isinstance(args[0], basestring) or not isinstance(int(args[1]), int) or not isinstance(int(args[2]), int) or not isinstance((args[3]), basestring):
	try:
		server_address = args[0]
		neg_port = int(args[1])
		req_code = int(args[2])
		message = args[3]

		if not message or not server_address:
			raise error

	except error:
		print "Empty string invalid"
		exit(1)

	except:
		print "Improper formatting of arguments"
		exit(1)


	return

#Function UDP_Handshake - carries UDP handshaking functionality on client side
#Parameters: 3
#	$1: <req_code> is the request code to initiate handshaking
#	$2: <server_address> the address of the target server
#	$3: <neg_port> UDP port that server UDP socket is binded to
#Return:
#	$1: <rand_port> TCP port number
#	$3: <serverAddr> a tuple containing server IP and port in the form (IP, port)

def UDP_Handshake(req_code, server_address, neg_port):
	#Create client UDP socket
	clientSocket = socket(AF_INET, SOCK_DGRAM)

	#Set timeout value to ensure no system hanging; Creating timeout value of 1 minute
	timeout = time.time() + 60

	#Send request code to server
	while True:
		clientSocket.sendto(str(req_code).encode(), (server_address, neg_port))
		#Receive TCP Port from server
		print "Waiting for TCP Port..."
		rand_port, serverAddr = clientSocket.recvfrom(1024)

		if (str(rand_port).decode() == ""):
			print "Unexpected TCP Port value received"
			if time.time() > timeout:
				exit(1)
		else:
			print "Received TCP Port"
			break

	#Set timeout value to ensure no system hanging; Creating timeout value of 1 minute
	timeout = time.time() + 60

	print "Sending confirm message..."

	while True:
		#Send TCP Port back to confirm
		confirm_msg = str(rand_port).decode()
		clientSocket.sendto(str(confirm_msg).encode(), serverAddr)

		#Verify ACK from Server
		print "Waiting for server ACK"
		ack_msg, serverAddr = clientSocket.recvfrom(1024)

		if str(ack_msg).decode().lower() != 'yes':
			print "Improper negotiation"
			if time.time() > timeout:
				exit(1)

		else:
			print("Server ACK received, closing UDP connection")
			clientSocket.close()
			break #Move on to creating TCP Connection

	return (rand_port, serverAddr)

#Function TCP_Transfer - carries out TCP transfer functionality from client side
#Parameters: 3
#	$1: <message> message to be sent
#	$2: <server_address> address of receiving server
#	$3: <rand_port> TCP port that server socket is binded to
#Return: 0

def TCP_Transfer(message, server_address, rand_port):
	print "Starting TCP Connection..."
	clientTCPSocket = socket(AF_INET, SOCK_STREAM)
	clientTCPSocket.connect((server_address, int(rand_port)))

	#Sending message to server
	clientTCPSocket.send(message.encode())

	#Waiting for reverse message
	reverseMessage = clientTCPSocket.recv(1024)
	print "CLIENT_RCV_MSG = ", reverseMessage
	clientTCPSocket.close()

#Function Main()
#Number of parameters: 0

def main():
	Check_Inputs(sys.argv[1:])
	server_address = sys.argv[1]
	neg_port = int(sys.argv[2])
	req_code = int(sys.argv[3])
	message = sys.argv[4]

	#Handshake
	rand_port, serverAddr = UDP_Handshake(req_code, server_address, neg_port)

	#TCP Transfer
	TCP_Transfer(message, server_address, rand_port)

	exit(0)


main()

