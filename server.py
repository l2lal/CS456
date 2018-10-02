#SERVER APPLICATION

#Assignment 1
#Computer Networks (CS 456)
#
#Number of parameters: 1
#Parameter:
#    $1: <req_code>
#

import sys
import time
from socket import *
from random import randint

NUM_INPUTS = 1

#Function check_inputs(args):
#Parameters: 1
#Parameter:
#	$1: <args> - all command line arguments minus script name
def Check_Inputs(args):

	if len(args) != NUM_INPUTS:
		print "Improper number of arguments"
		exit(1)
	
	try:
		req_code = int(args[0])

	except:
		print "Improper formatting of argument", args
		exit(1)

	return

#Function Create_UDP - creates server UDP socket
#Parameters: 0
#Return:
#	$1: <serverUDPSocket> handle to UDP Socket
#	$2: <neg_port> UDP port

def Create_UDP():
	#Create server UDP Socket and listen to the negotiate port
	serverUDPSocket = socket(AF_INET, SOCK_DGRAM)
	serverUDPSocket.bind(('', 0))
	serverUDPHost, neg_port = serverUDPSocket.getsockname()

	print "SERVER_PORT = ", str(neg_port)
	return (serverUDPSocket, neg_port)

#Function UDP_Handshake - carries UDP handshaking functionality on server side
#Parameters: 2
#	$1: <serverUDPSocket> is the handle to a UDP Socket
#	$2: <req_code> is the request code to initiate handshaking
#Return:
#	$1: <clientAddress> a tuple returning client IP address and port as (IP, port)
#	$2: <rand_port> TCP port
#	$3: serverTCPSocket a handle to the TCP socket

def UDP_Handshake(serverUDPSocket, req_code):
	#Set timeout value to ensure no system hanging; Creating timeout value of 1 minute
	timeout = time.time() + 60

	#Listen for the request code
	print "Waiting for request code..."
	while True:
		receive_code, clientAddress = serverUDPSocket.recvfrom(1024)

		if receive_code.decode() != str(req_code): # code isn't correct, keep listening
			print "Invalid request code"
			if time.time() > timeout:
				print "Timed out waiting for request code"
				exit(1)

		else: #code is correct, let's do stuff
			print "Request code received"
			break

	rand_port, serverTCPSocket = Create_TCP_Socket();

	#Set timeout value to ensure no system hanging; Create timeout value of 1 minute from current time
	timeout = time.time() + 60

	while True:
		serverUDPSocket.sendto(str(rand_port).encode(), clientAddress)
		print "Waiting for port confirmation..."
		confirm_port, clientAddress = serverUDPSocket.recvfrom(1024)

		if str(confirm_port).decode() != str(rand_port):
			if time.time() > timeout:
				exit(1)

		else: #code is correct, let's do stuff
			print "Port confirmed, sending ACK"
			ack_msg = "yes"
			serverUDPSocket.sendto(ack_msg.encode(), clientAddress)
			break

	#serverUDPSocket.close()
	print "SERVER_TCP_PORT = ", str(rand_port)

	return (clientAddress, rand_port, serverTCPSocket)

#Function Create_TCP_Socket - creates server TCP socket
#Parameters: 0
#Return:
#	$1: <rand_port> the port the socket is connected to
#	$2: <serverTCPSocket> handle to TCPSocket

def Create_TCP_Socket():
	#Send random port, and listen for piggy back
	serverTCPSocket = socket(AF_INET, SOCK_STREAM)
	serverTCPSocket.bind(('', 0))
	serverTCPSocket.listen(1)
	serverHost, rand_port = serverTCPSocket.getsockname()

	return (rand_port, serverTCPSocket)

#Function TCP_Transfer - carries out TCP transfer functionality from server side
#Parameters: 1
#	$1: <serverTCPSocket> is a handle to the TCP socket
#Return: 0

def TCP_Transfer(serverTCPSocket):
	
	print "Waiting incoming TCP messages..."

	while True:

		try:
			TCPSocket, addr = serverTCPSocket.accept()
			msg = TCPSocket.recv(1024).decode()
			print "SERVER_RCV_MSG = ", msg.encode('utf-8')
			reversemsg = msg[::-1] #https://dbader.org/blog/python-reverse-string
			TCPSocket.send(reversemsg.encode())
			TCPSocket.close()
			break

		except socket.error:
			print "Error occured."
			break

#Function Main()
#Number of parameters: 0

def main():
	#TAKE INPUTS
	Check_Inputs(sys.argv[1:])
	req_code = sys.argv[1]

	timeout = time.time() + 60 * 5

	#Create UDP Socket
	serverUDPSocket, neg_port = Create_UDP()

	while True:
		#UDP Handshake
		clientAddress, rand_port, serverTCPSocket = UDP_Handshake(serverUDPSocket, req_code)

		#TCP_Transfer
		TCP_Transfer(serverTCPSocket)

	#pythontops.com/ python socket network programming

main()


