/* Receiver Program
Computer Networks (CS 456)
Number of parameters: 4
Parameter:
    $1: hostname of network emulator
    $2: emulator UDP port to receive from Receiver
    $3: Receiver UDP port to receive from emulator
    $4: output file name

#Author: Lalit Lal
*/

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Timer;
import java.util.TimerTask;
import java.util.LinkedList;
import java.net.DatagramSocket;
import java.net.DatagramPacket; 
import java.net.InetAddress;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.BufferedReader;
import java.io.BufferedWriter;

public class Receiver {
	//constants
	private final static int SeqNumModulo = 32;

	//file handles
	static BufferedWriter file_handle;
	static BufferedWriter ack_log_handle;

	//global check states
	static boolean isEOT = false;
	static int updated_seq_num = -1;
	
	/*Function main - validates input, initializes handles, and runs the receiver program
	Parameters: 4
	    $1: hostname of network emulator
	    $2: emulator UDP port to receive from Receiver
	    $3: Receiver UDP port to receive from emulator
	    $4: output file name
	Return: None
    */
	public static void main(String[] args) throws Exception {

		//validate arguments
		validateArgs(args);

		//assign inputs to variables
    	InetAddress emulator_addr = InetAddress.getByName(args[0]); 
		int emulator_port = Integer.parseInt(args[1]); 
		int receiver_port = Integer.parseInt(args[2]); 
		String file_name = args[3]; 

		//assign file handles to appropriate files
		file_handle = new BufferedWriter(new FileWriter(file_name));
		ack_log_handle =new BufferedWriter(new FileWriter("arrival.log"));

		//run receiver
		Receiver.run(emulator_addr, emulator_port, receiver_port, file_name);
	}

	/*Function validateArgs - validates input
	Parameters: 4
	    $1: hostname of network emulator
	    $2: emulator UDP port to receive from Receiver
	    $3: Receiver UDP port to receive from emulator
	    $4: output file name
	Return: None
	*/
	public static void validateArgs(String[] args) throws Exception {
		//check number of args
		if(args.length != 4) {
			System.out.println("Error: Wanted 4 arguments, got: " + args.length + "instead"); 
			System.exit(-1); 
		}

		//valid IP address and hostname
		if(!validHost(args[0]))
		{
			System.out.println("Error: Invalid hostname: " + args[0]);
			System.exit(-1); 
		}
		// validate emulator port
		try {
			int emulator_port = Integer.parseInt(args[1]); 
		} catch (NumberFormatException e) {
			System.out.println("Error: Wanted integer for emulator port, got: " + args[1] + "instead");
			System.exit(-1);  
		}

		// validate receiver port
		try {
			int receiver_port = Integer.parseInt(args[2]); 
		} catch (NumberFormatException e) {
			System.out.println("Error: Wanted integer for receiver port, got: " + args[1] + "instead");
			System.exit(-1);  
		}
	}

	/*Function validHost - uses regex to validate the hostname input
	Parameters: 1
	    $1: hostname of network emulator

	Return: 1
		$1: True if valid hostname, false otherwise
    */
  	private static boolean validHost(final String host) throws Exception {
    
	    // taken from https://stackoverflow.com/questions/22614349/checking-if-a-string-can-be-an-ip-address-in-java
	    String pattern = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])" +
	                     "(\\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9]))*$";
	      //see if hostname matches pattern
	      boolean isMatch = host.matches(pattern);
	      if(isMatch && host.length() <= 255)
	      {
	        return true;
	      }             
	      else
	      {
	        return false; 
	      }
  	}

	/*Function run - runs receiver application given validated inputs
	Parameters: 4
	    $1: hostname of network emulator
	    $2: emulator UDP port to receive from Receiver
	    $3: Receiver UDP port to receive from emulator
	    $4: output file name
	Return: None
    */
	public static void run(InetAddress emulator_addr, int emulator_port, int rcv_port, String file_name) {
		try 
		{
			//create socket and receive buffer
			DatagramSocket server_socket = new DatagramSocket(rcv_port);
	    	byte[] receive_data = new byte[512];

	    	//format buffer to datagram
	    	DatagramPacket receive_packet = new DatagramPacket(receive_data, receive_data.length);

	    	while(true && !isEOT)
	    	{
		    	//blocking call, wait for message
				server_socket.receive(receive_packet);

				//format data to a packet
				try {
					packet data_packet = packet.parseUDPdata(receive_packet.getData());
					
					//DEBUG
					//System.out.println("Rcv Seq: " + data_packet.getSeqNum() + " Exp Seq: " + ((updated_seq_num+1)%SeqNumModulo)); 

					//write packet sequence number to log file
					ack_log_handle.write(String.valueOf(data_packet.getSeqNum()));
					ack_log_handle.newLine();

					//parse packet
					parsePacket(data_packet);

				} catch (Exception e) {
					System.out.println("Error: Cannot parse incoming data.");
				}
				
				//validate sequence number
				if(updated_seq_num >= 0)
				{
					//if EOT received
					if(isEOT)
					{
						try {
							//create EOT packet
							packet ack_packet = packet.createEOT(updated_seq_num);
							
							//get into byte array format
							byte[] arr = ack_packet.getUDPdata(); 

							//create UDP datagram from byte array
							DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

							//UDP formatted datagram sent through receiver socket to emulator
							//System.out.println("Sending EOT with seqence: " + ack_packet.getSeqNum());
							server_socket.send(send_packet);
							//updated_seq_num = (updated_seq_num + 1) % SeqNumModulo;
						} catch (Exception e) {
							System.out.println("Error: Cannot create EOT packet.");
							System.exit(-1);
						}
					}
					//not EOT, just a data packet
					else
					{
						try {
							//create ack packet
							packet ack_packet = packet.createACK(updated_seq_num);
							
							//get into byte array format
							byte[] arr = ack_packet.getUDPdata(); 

							//create UDP datagram from byte array
							DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

							//UDP formatted datagram sent through receiver socket to emulator
							//System.out.println("Sending ack with seqence: " + ack_packet.getSeqNum());
							server_socket.send(send_packet);
							//updated_seq_num = (updated_seq_num + 1) % SeqNumModulo;
						} catch (Exception e) {
							System.out.println("Error: Cannot create ACK packet.");
							System.exit(-1); 
						}

					}
				}
				

				//if in-order packet received is EOT, quit listening
				if(isEOT)
				{
					System.out.println("Received EOT"); 
					break;
				}

	    	}

	    //close socket and file handles
	    System.out.println("EOT sent, closing connection"); 
	    server_socket.close();
	    ack_log_handle.close();
	    file_handle.close();  

		} catch (IOException e) {
		System.out.println(e);
		System.exit(-1); 
	  }
	}	

	/*Function parsePacket - parses incoming packets, writing appropriate packets to log files or output file
	Parameters: 1
	    $1: incoming packet
	Return: None
    */
	public static void parsePacket(packet data_packet) {

		//If data is right type - data or EOT
		if(data_packet.getType() == 1 || data_packet.getType() == 2)
		{
			//check to see we're getting the right ack, in order
			if(data_packet.getSeqNum() == (updated_seq_num+1) % SeqNumModulo)
			{
				updated_seq_num = (updated_seq_num+1) % SeqNumModulo; 

				//set EOT flag if we got an EOT in order
				if(data_packet.getType() == 2)
				{
					isEOT = true; 
				}

				//data packet, so write it to a file
				else if(data_packet.getType() == 1)
				{
					System.out.println("Writing to output file");	
					try {
						System.out.println("Data is :" + data_packet.getData());
						file_handle.write(new String(data_packet.getData(), "UTF-8")); 
					} catch (IOException e) {
						System.out.println("Error: Cannot write data to end file.");
						System.exit(-1); 
					}
					
				}
			}

		}
		return; 
	}
}
