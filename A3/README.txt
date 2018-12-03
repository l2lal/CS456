README.md

Implementation Method: Python 2.7

Instructions:
This is the README for Assignment 3 of CS456. You must first run the nse executable before your run the router.sh script 
---------------------------------
File Descriptions:

Filename: router.sh - executes python script router.py with given inputs

Parameters: 4
1. <server_address> [string] - the IP address of the server to contact, in the form "X.X.X.X"
2. <neg_port> [int] - the negotiating port used in stage 1 spec of the assignment; for the UDP socket
3. <req_code> [int] - the request code that the client will use to contact the server. This must match the request code that the client is looking for
4. <message> [string] - the message to be reversed (maximum of 1024 bytes)

Example script call:
sh router.sh 1 129.97.167.26 45669 43567

Executable: nselinux386
Parameters: 2
1. <nse_host> [string] - the IP address of the nse to contact, in the form "X.X.X.X"
2. <nse_port> [int] - the nse port used in future transactions

Example use:
./nselinux386 129.97.167.26 45669
---------------------------------
Example Execution - using the same HOST for the router and NSE:

You must first run the nse executable, an exapmle is shown below

./nselinux386 129.97.167.26 45669


Then you must run router.sh script for give unique routers :

sh router.sh 1 129.97.167.26 45669 43567
sh router.sh 2 129.97.167.26 45669 43568
sh router.sh 3 129.97.167.26 45669 43569
sh router.sh 4 129.97.167.26 45669 43571
sh router.sh 5 129.97.167.26 45669 43572

----------------------------------------
EXPECTED OUTPUTS: 

NSE: The NSE is fairly verbose, so its output is excluded from here.

ROUTER (in console):
	Sending INIT...
	Waiting for Hellos...
	Finished

LOGS (Example router2.log):
	INFO:root:Starting routing protocol for router 2
	INFO:root:R2 sends an INIT: router_id 2
	INFO:root:R2 receives a CIRCUIT_DB: nbr_link 3
	INFO:root:R2 sends a HELLO: router_id 2 link_id 1
	INFO:root:R2 sends a HELLO: router_id 2 link_id 2
	INFO:root:R2 sends a HELLO: router_id 2 link_id 6
	INFO:root:R2 receives a HELLO: router_id5 link_id6
	INFO:root:R2 receives a HELLO: router_id1 link_id1
	INFO:root:R2 receives a HELLO: router_id3 link_id2
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 1 cost 1 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 2 cost 2 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 6 cost 6 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 1 cost 1 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 2 cost 2 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 6 cost 6 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 1 cost 1 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 2 cost 2 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id 2 link_id 6 cost 6 via 2
	INFO:root:R2 receives a LSPDU: sender1 router_id 1 link_id 1 cost 1 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 1 cost 1 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 1 cost 1 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 1 cost 1 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 1
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender1 router_id 1 link_id 5 cost 5 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 5 cost 5 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 5 cost 5 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id1 link_id 5 cost 5 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender3 router_id 3 link_id 2 cost 2 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 2 cost 2 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 2 cost 2 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 2 cost 2 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 1
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender3 router_id 3 link_id 7 cost 7 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 7 cost 7 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 7 cost 7 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 7 cost 7 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 2
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender3 router_id 3 link_id 3 cost 3 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 3 cost 3 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 3 cost 3 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id3 link_id 3 cost 3 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender1 router_id 5 link_id 4 cost 4 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 4 cost 4 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 4 cost 4 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 4 cost 4 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 1
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender3 router_id 4 link_id 3 cost 3 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 3 cost 3 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 3 cost 3 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 3 cost 3 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 1
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 1
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender5 router_id 5 link_id 4 cost 4 via 6
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 1
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 1
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender1 router_id 5 link_id 7 cost 7 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 7 cost 7 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 7 cost 7 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 7 cost 7 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 1
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 2
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender5 router_id 5 link_id 7 cost 7 via 6
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 1
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 2
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender5 router_id 5 link_id 6 cost 6 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 6 cost 6 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 6 cost 6 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 6 cost 6 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 1
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R5 nbr link 3
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:R2 -> R5 link 6 cost 6
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender3 router_id 4 link_id 4 cost 4 via 2
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 4 cost 4 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 4 cost 4 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id4 link_id 4 cost 4 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 2
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R4 link 4 cost 4
	INFO:root:R2 -> R5 nbr link 3
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:R2 -> R5 link 6 cost 6
	INFO:root:------- # END Topology Database -------
	INFO:root:R2 receives a LSPDU: sender5 router_id 5 link_id 5 cost 5 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 5 cost 5 via 6
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 5 cost 5 via 1
	INFO:root:R2 sends a LSPDU: sender2 router_id5 link_id 5 cost 5 via 2
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 2
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R4 link 4 cost 4
	INFO:root:R2 -> R5 nbr link 4
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:R2 -> R5 link 6 cost 6
	INFO:root:R2 -> R5 link 5 cost 5
	INFO:root:------- # END Topology Database -------
	INFO:root:------- Final Prints -------
	INFO:root:------- # START Topology Database -------
	INFO:root:R2 -> R1 nbr link 2
	INFO:root:R2 -> R1 link 1 cost 1
	INFO:root:R2 -> R1 link 5 cost 5
	INFO:root:R2 -> R2 nbr link 3
	INFO:root:R2 -> R2 link 1 cost 1
	INFO:root:R2 -> R2 link 2 cost 2
	INFO:root:R2 -> R2 link 6 cost 6
	INFO:root:R2 -> R3 nbr link 3
	INFO:root:R2 -> R3 link 2 cost 2
	INFO:root:R2 -> R3 link 7 cost 7
	INFO:root:R2 -> R3 link 3 cost 3
	INFO:root:R2 -> R4 nbr link 2
	INFO:root:R2 -> R4 link 3 cost 3
	INFO:root:R2 -> R4 link 4 cost 4
	INFO:root:R2 -> R5 nbr link 4
	INFO:root:R2 -> R5 link 4 cost 4
	INFO:root:R2 -> R5 link 7 cost 7
	INFO:root:R2 -> R5 link 6 cost 6
	INFO:root:R2 -> R5 link 5 cost 5
	INFO:root:------- # END Topology Database -------
	INFO:root:------- # START RIB -------
	INFO:root:R2 -> 1 -> 1, 1
	INFO:root:R2 -> 2 -> Local, 0
	INFO:root:R2 -> 3 -> 3, 2
	INFO:root:R2 -> 4 -> 3, 5
	INFO:root:R2 -> 5 -> 5, 6
	INFO:root:------- # END RIB -------
	INFO:root:------- END OSPF -------
----------------------------------------
If you see something similar to this for all your routers (console and logs), your demonstration has run successfully, as expected. 

NOTE: DIJKSTRAS ALGORITHM IMPLEMENTATION WAS SOURCED FROM: 	
#https://dev.to/mxl/dijkstras-algorithm-in-python-algorithms-for-beginners-dkc

Undergraduate Machines Tested On:
Loopback Test Conducted on: ubuntu1604-006

