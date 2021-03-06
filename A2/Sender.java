/* Sender Program
Computer Networks (CS 456)
Number of parameters: 4
Parameter:
    $1: host address of network emulator
    $2: emulator UDP port to receive from Sender
    $3: Sender UDP port to receive acks from emulator
    $4: name of file to transfer

#Author: Lalit Lal
*/

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.File;
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

public class Sender {
  //constants
  private final static int N = 10; //Window size
  private final static  int Timeout_val = 1000; //milliseconds
  private final static int MaxDataLength = 500; 
  private final static int SeqNumModulo = 32;


  private static long file_length;

  //get file handle to get length, then close it. 
  static File target_file;

  //linked list buffer
  static LinkedList<packet> not_acked_packets = new LinkedList<packet>();

  //client UDP socket
  static DatagramSocket client_socket; 

  //create timer member
  static Waiter waiter; 

  //Filehandle
  static BufferedReader file_handle;

  // log file handles
  static BufferedWriter seq_log_handle;
  static BufferedWriter ack_log_handle;

  //send and receive threads
  static Thread sender;
  static Thread receive_acks;

  // set base to be zero - base is first element of window, or oldest unack'd message
  static int base = 0;

  // next index to send a message
  static int next_seq_num = 0;

  //placeholders for inputs
  static InetAddress emulator_addr;
  static int emulator_port; 
  static int sender_port;
  static String file_name;

  //globally used states
  static boolean expecting_EOT = false;
  static boolean eot_received = false; 


  /*Function main - validates input, initializes handles, and runs the send and rcv threads
  Parameters 4:
    $1: host address of network emulator
    $2: emulator UDP port to receive from Sender
    $3: Sender UDP port to receive acks from emulator
    $4: name of file to transfer
  Return: None
  */
  public static void main(String[] args) throws Exception {

    //validate args
    validateArgs(args); 

    // Take arguments from command line
    emulator_addr = InetAddress.getByName(args[0]); 
    emulator_port= Integer.parseInt(args[1]); 
    sender_port = Integer.parseInt(args[2]);
    file_name = args[3]; 

    //linked list buffer
    not_acked_packets = new LinkedList<packet>();

    //client UDP socket
    client_socket = new DatagramSocket(sender_port); 

    //create timer member
    waiter = new Waiter(Timeout_val);  

    //Filehandle
    target_file = new File(file_name); 
    file_handle = new BufferedReader(new FileReader(file_name), MaxDataLength);
    file_length = target_file.length();

    // log file handles
    seq_log_handle =new BufferedWriter(new FileWriter("seqnum.log"));
    ack_log_handle = new BufferedWriter(new FileWriter("ack.log"));


    //sender and receiver threads
    sender = new Thread(new Send_Thread()); 
    receive_acks = new Thread(new Ack_Receive()); 

    //initialize global state
    expecting_EOT = false;  
    
    //start threads
    sender.start();
    receive_acks.start();  
  } //main

  /*Function validateArgs - validates input
  Parameters: 4
    $1: host address of network emulator
    $2: emulator UDP port to receive from Sender
    $3: Sender UDP port to receive acks from emulator
    $4: name of file to transfer
  Return: None
  */
  private static void validateArgs(String[] args) throws Exception {
    //check number of args
    if(args.length != 4) {
      System.out.println("Error: Wanted 4 arguments, got: " + args.length + "instead"); 
      System.exit(-1); 
    }

    //valid IP address and hostname
    if(!validIP(args[0]) && !validHost(args[0]))
    {
      System.out.println("Error: Cannot identify IP address or Hostname: " + args[0]);
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

  /*Function validIP - uses regex to validate the host ip address input
  Parameters: 1
      $1: ip address of network emulator

  Return: 1
    $1: True if valid hostname, false otherwise
    */
  private static boolean validIP(final String ip) throws Exception {
    
    // taken from https://stackoverflow.com/questions/22614349/checking-if-a-string-can-be-an-ip-address-in-java
    String pattern = 
        "^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\." +
        "([01]?\\d\\d?|2[0-4]\\d|25[0-5])$";

    boolean isMatch = ip.matches(pattern); 
    return isMatch;             
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

  // Custom class that implements timer
  public static class Waiter {
    Timer timer;
    int milliseconds;
    TimerTask waiter_task; 

    /*Function constructor
    Parameters: 1
      $1: timeout in milliseconds

    Return: waiter object
    */
    public Waiter(int milliseconds) {
        timer = new Timer();
        this.milliseconds = milliseconds; 
    }

     /*Function startTimerTask - starts timer
    Parameters: None

    Return: None
    */
    public void startTimerTask()
    {
      System.out.println("Starting Timer...");
      waiter_task = new WaiterTask(); 
      timer.schedule(waiter_task, this.milliseconds);
    }

    /*Function stopTimerTask - stops timer
    Parameters: None

    Return: None
    */
    public void stopTimerTask()
    {
      //System.out.println("Stopping timer...");
      if(waiter_task != null) {
        //System.out.println("Timer isn't null");
        waiter_task.cancel(); 
      }
      //System.out.println("Timer stopped."); 
    }

    //subclass that builds from a task
    class WaiterTask extends TimerTask {
        public void run() {
            reTransmit();
            return;  
        }
    }
  }

  //sending thread
  public static class Send_Thread implements Runnable {

    public void run(){
      System.out.println("Sender thread kickoff");

      //get file data!! 
       rdtSend();
       return;  
    }
  }

  //receiving thread
  public static class Ack_Receive implements Runnable {

    public void run(){
      System.out.println("Ack Receive thread kickoff");
      rdtReceive();
      return;   
    }
  }

    /*Function rdtSend - function executed by sending thread; this sends input file data to emulator
    Parameters: None

    Return: None
    */
  public static void rdtSend() {

    //create file reading buffer
    char[] cbuf = new char[MaxDataLength];
    //store result of each file read; successful reads will contain length of bytes read, -1 otherwise.  
    int read_result = 0; 
    
    try {
      //read 500byte chunk of file into buffer
      read_result = file_handle.read(cbuf);
    } catch (IOException e) {
      System.out.println("Cannot read file");
      e.printStackTrace();
      System.exit(-1); 
    }

    //while file still has data, send stuff
    while(read_result != -1)
    {
      //while window is full, wait. Sleep for a bit
      while(!windowNotFull())
      {
        try { Thread.sleep(1*1000); } catch (Exception e) { e.printStackTrace(); System.exit(-1); }  
      }

      //verify window isn't open before sending chunk
      if(windowNotFull())
      {
        //place file read buffer into a string
        try {
          //copy buffer  to string, only create string of length that was rad
          String strData = String.copyValueOf(cbuf, 0, read_result);

          //placeholder for sending packet
          packet orig_packet = packet.createPacket(next_seq_num, strData);

          //convert it to an array and then into datagram format
          byte[] arr = orig_packet.getUDPdata();
          DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

          //send packet through client socket, logging the sequence and managing list of unack'd packets
          client_socket.send(send_packet);
          seq_log_handle.write(String.valueOf(orig_packet.getSeqNum()));
          seq_log_handle.newLine();
          addToList(orig_packet);
          System.out.println("List size: " + not_acked_packets.size()); 
          
          //check if sent item is first unack'd in window, then we'll need to kick off the timer 
          if(timerNeeded())
          {
            waiter.stopTimerTask();
            waiter.startTimerTask(); 
          }

          //update index of next packet sequence
          next_seq_num = (next_seq_num + 1) % SeqNumModulo;

          //read next chunk of file for next iteration
          read_result = file_handle.read(cbuf);
         
  
        } catch (IOException e) {
          System.out.println("Error: Failed read of file");
          e.printStackTrace(); 
          System.exit(-1); 
        } catch (Exception e) {
          System.out.println("Error: Cannot create packet");
          e.printStackTrace();
          System.exit(-1); 
        }
        
      }

    }//while

    //file data all sent, now send EOT
    //send EOT, let receiver deal with sending appropriate ACKs and its own EOT
    //wait for window to open space, sleep for a bit if full
    while(not_acked_packets.size() != 0)
    {
      try { Thread.sleep(1*1000); } catch (Exception e) {e.printStackTrace(); System.exit(-1);}
    }

    try { 
      packet eot_packet = packet.createEOT(next_seq_num); 
    
      //get into byte array format
      byte[] arr = eot_packet.getUDPdata();
      //create UDP datagrapm from this
      DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

      //UDP formatted datagram sent through client socket to emulator
      client_socket.send(send_packet);
      seq_log_handle.write(String.valueOf(eot_packet.getSeqNum()));
      seq_log_handle.newLine(); 

      //update sequence
      next_seq_num = (next_seq_num + 1) % SeqNumModulo;
      //add EOT packet to unack'd list
      addToList(eot_packet);
    } catch (Exception e) { e.printStackTrace(); System.exit(-1); }

    //set global state - we are waiting for EOT return
    setEotExpected(); 

    //wait for EOT to be received, sleep for a bit. 
    while(!eot_received) 
    {
      try { Thread.sleep(1*1000); } catch (Exception e) { System.exit(-1); }
    }
    //EOT was received, close handle of outbound sequence log
    try { 
      System.out.println("Closing sequence log handle");
      if(seq_log_handle != null) seq_log_handle.close(); 
    } catch (IOException e) {
      System.out.println("Error: Cannot close file");
      System.exit(-1); 
    }
    return;  

  } //rdtSend

    /*Function rdtReceive - function executed by ack receiving thread; this sends input file data to emulator
    Parameters: None

    Return: None
    */
  public static void rdtReceive() {

    try {

        //create buffer to store data in
        byte[] receive_data = new byte[512];

        // convert buffer to UDP format
        DatagramPacket receive_packet = new DatagramPacket(receive_data, receive_data.length);

        //always-on receiver thread for client
        while(true)
        {
          //blocking call to receive ack packet from emulator
          client_socket.receive(receive_packet);
          System.out.println("Receiver got something!");
          try {
            //packet is received, format it and parse it, updating buffer and indexes
            packet ack_packet = packet.parseUDPdata(receive_packet.getData());
            parseAck(ack_packet); 

            
          } catch (Exception e) {
            System.out.println("Error: Receiver thread failure");
            System.exit(-1); 
          }
          
          //if we were expecting and received an EOT packet
          if(eot_received && isEotExpected())
          {
            System.out.println("EOT RECEIVED!"); 
            break;
          } 
        }

        //close socket and log handles
        client_socket.close();
        ack_log_handle.close();
        waiter.timer.cancel(); 
        file_handle.close();

      } catch (IOException e) {
          System.exit(-1);
          e.printStackTrace();
      }
    // should close serverSocket in finally block
    // close socket HERE
    System.out.println("EOT Received. Closing client socket"); 

    return;  
      
  } 

  // THE FOLLOWING ARE SYNCHRONIZED METHODS TO ENSURE THREAD SYNCHRONIZATION //
  
    /* Function reTransmit - function triggered by timer task in Waiter class to retransmit unack'd packets in buffer
    Parameters: None

    Return: None
    */
  public static synchronized void reTransmit() {

    //kick off another timer; first stop current one
    waiter.stopTimerTask(); 
    waiter.startTimerTask(); 
    System.out.println("Time out. Retransmitting " + not_acked_packets.size() + " packets"); 

    for(int i = 0; i < not_acked_packets.size(); i++)
    {

      //retrieve list item
      packet list_packet = not_acked_packets.get(i); 
      //get into byte array format
      byte[] arr = list_packet.getUDPdata(); 

      //create UDP datagrapm from this
      DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

      //UDP formatted datagram sent through client socket to emulator
      try { client_socket.send(send_packet); } catch (IOException e) {System.out.println("Error: Cannot send packet"); System.exit(-1); } 

      try { 
        // log the sequence number of the packet you're sending
        seq_log_handle.write(String.valueOf(list_packet.getSeqNum()));
        seq_log_handle.newLine(); 
      } catch (IOException e) {
        System.out.println("Error: Cannot write seq");
        System.exit(-1);  
      } 
 
    }

  }


  /* Function parseAck - function called by rdtReceive to process incoming packets
  Parameters: packet ack_packet - packet to parse

  Return: none
  */
  public static synchronized void parseAck(packet ack_packet) {
    // Status of finding packet
    boolean found_in_list = false; 

    // write ack packets to log file
    try{
      System.out.println("Writing to ack log");
      ack_log_handle.write(String.valueOf(ack_packet.getSeqNum()));
      ack_log_handle.newLine();
    } catch (IOException e) {
      e.printStackTrace();
      System.exit(-1); 
    }

    // check if packet is ack type
    int index = 0;
    //System.out.println("type of packet is " + ack_packet.getType()); 

    if(ack_packet.getType() == 0) { //type is an ACK, as we expected
      System.out.println("Got ack with sequence: " + ack_packet.getSeqNum()); 

      //go through buffer to see if and where ack packet is in buffer; if found, set found state
      for(int i = 0; i < not_acked_packets.size(); i++)
      {
        if(not_acked_packets.get(i).getSeqNum() == ack_packet.getSeqNum())
        {
          System.out.println("found ack at index: " + i);
          index = i;
          found_in_list = true;  
          break;
        }
      }

      //return if not found in list (ignore the ack)
      if(!found_in_list)
      {
        return; //ignore duplicate or ack's that don't reflect our window packets
      }

      //ack is found, update the base of our buffer and check if we need to restart the timer
      base = (ack_packet.getSeqNum() + 1) % SeqNumModulo; 
      waiter.stopTimerTask();

     //restart timer if more unacked messages
      if(base != next_seq_num)
      {
        waiter.startTimerTask(); 
      }

      
      //starting from beginning, remove up until sequence number you've received. This works because we add packets sequentially. 
      int j = 0; 
      while(j <= index)
      {
        not_acked_packets.remove(0);
        j++; 
      }
      
    } //if
    
    // Check if packet is EOT type, then remove all other packets and set global state that eot is received
    else if(ack_packet.getType() == 2) // got EOT, means everything received. 
    {
      int j = 0; 
      while(j <= not_acked_packets.size())
      {
        not_acked_packets.removeFirst(); 
        j++; 
      }
      eot_received = true; 
    }    
  }

  /* Function timerNeeded - function to check if we need to start the timer
  Parameters: None

  Return: boolean - true if timer is needed, false otherwise
  */
  public static synchronized boolean timerNeeded() {
    
    if(base == next_seq_num)
    {
      return true;
    }

    return false; 
  }

  /* Function windowNotFull - function to check if packet buffer is full
  Parameters: None

  Return: boolean - true if window is not full, false if it is full
  */
  public static synchronized boolean windowNotFull() {
    if(not_acked_packets.size() < N)
    {
      return true; 
    }

    return false; 
  }

  /* Function addToList - function to add packet to end of buffer
  Parameters: packet orig_packet - packet to insert into list

  Return: None
  */
  public static synchronized void addToList(packet orig_packet) {
    not_acked_packets.addLast(orig_packet);
  }

  /* Function setEotExpected - function to set global boolean state (expecting EOT packet)
  Parameters: None

  Return: None
  */
  public static synchronized void setEotExpected() {
    expecting_EOT = true; 
  }

  /* Function isEotExpected - function to evaluate value of expecting_EOT global state
  Parameters: None

  Return: boolean - true if expecting an EOT, false otherwise
  */
  public static synchronized boolean isEotExpected() {
    return expecting_EOT;  
  }

}
