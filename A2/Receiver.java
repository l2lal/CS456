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
	static BufferedWriter file_handle;
	static BufferedWriter ack_log_handle;

	static boolean isEOT = false;
	static int updated_seq_num = 0;
	private final static int SeqNumModulo = 32;
	
	public static void main(String[] args) throws Exception {

		//validate arguments
		validateArgs(args);


    	InetAddress emulator_addr = InetAddress.getByName(args[0]); 
		int emulator_port = Integer.parseInt(args[1]); 
		int receiver_port = Integer.parseInt(args[2]); 
		String file_name = args[3]; 

		file_handle = new BufferedWriter(new FileWriter(file_name));
		ack_log_handle =new BufferedWriter(new FileWriter("arrival.log"));

		Receiver.run(emulator_addr, emulator_port, receiver_port, file_name);
	}

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

		try {
			int receiver_port = Integer.parseInt(args[2]); 
		} catch (NumberFormatException e) {
			System.out.println("Error: Wanted integer for receiver port, got: " + args[1] + "instead");
			System.exit(-1);  
		}
	}

  	private static boolean validHost(final String host) throws Exception {
    
	    // taken from https://stackoverflow.com/questions/22614349/checking-if-a-string-can-be-an-ip-address-in-java
	    String pattern = "^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])" +
	                     "(\\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9]))*$";

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

	public static void run(InetAddress emulator_addr, int emulator_port, int rcv_port, String file_name) {
		try 
		{
			//create socket and receive buffer
			DatagramSocket server_socket = new DatagramSocket(rcv_port);
	    	byte[] receive_data = new byte[512];

	    	//format buffer to datagram
	    	DatagramPacket receive_packet = new DatagramPacket(receive_data, receive_data.length);

	    	while(true)
	    	{
		    	//blocking call, wait for message
				server_socket.receive(receive_packet);

				//format data to a packet
				try {
					packet data_packet = packet.parseUDPdata(receive_packet.getData());
					//write incoming packet to log file
					System.out.println("Got a packet with sequence" + data_packet.getSeqNum());
					System.out.println("Expecting a sequence of: " + updated_seq_num);

					ack_log_handle.write(String.valueOf(data_packet.getSeqNum()));
					ack_log_handle.newLine();

					//parse packet
					//if DATA type
					parsePacket(data_packet);
				} catch (Exception e) {
					System.out.println("Error: Cannot parse incoming data.");
				}
				 
				
				//if EOT type
				if(isEOT)
				{
					try {
						packet ack_packet = packet.createEOT(updated_seq_num);
						//get into byte array format
						byte[] arr = ack_packet.getUDPdata(); 

						//create UDP datagram from byte array
						DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

						//UDP formatted datagram sent through receiver socket to emulator
						System.out.println("Sending ack with seqence: " + ack_packet.getSeqNum());
						server_socket.send(send_packet);
					} catch (Exception e) {
						System.out.println("Error: Cannot create EOT packet.");
					}
				}
				else
				{
					try {
						packet ack_packet = packet.createEOT(updated_seq_num);
						//get into byte array format
						byte[] arr = ack_packet.getUDPdata(); 

						//create UDP datagram from byte array
						DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

						//UDP formatted datagram sent through receiver socket to emulator
						System.out.println("Sending EOT with seqence: " + ack_packet.getSeqNum());
						server_socket.send(send_packet);
					} catch (Exception e) {
						System.out.println("Error: Cannot create EOT packet.");
					}

				}

				
				if(isEOT)
				{
					break;
				}

      			try { Thread.sleep(1*1000); } catch (Exception e) { } 
	    	}

	    //close socket, sending only EOT once, assuming it doesn't get messed up along the way.
	    System.out.println("EOT sent, closing connection"); 
	    server_socket.close();
	    ack_log_handle.close(); 

		} catch (IOException e) {
		System.out.println(e);
	  }
	  // should close serverSocket in finally block 
	}	

	public static void parsePacket(packet data_packet) {

		if(data_packet.getType() == 1 || data_packet.getType() == 2)
		{
			int expected_ack = (updated_seq_num + 1) % SeqNumModulo;
			//check to see we're getting the right ack
			if(data_packet.getSeqNum() == expected_ack)
			{
				//update latest received ack and write data to input file
				updated_seq_num = expected_ack;

				if(data_packet.getType() == 2)
				{
					isEOT = true; 
				}

				//data packet, so write it to a file
				else
				{
					try {
						file_handle.write(new String(data_packet.getData())); 
					} catch (IOException e) {
						System.out.println("Error: Cannot write data to end file.");
					}
					
				}
			}

		}
		return; 
	}
}
