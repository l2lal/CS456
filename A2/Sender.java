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
  private final static int N = 10;
  private final static  int Timeout_val = 10;
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

  static Thread sender;
  static Thread receive_acks;

  // set base to be zero - base is first element of window, or oldest unack'd message
  static int base = 0;

  // next index to send a message
  static int next_seq_num = 0;

  static InetAddress emulator_addr;
  static int emulator_port; 
  static int sender_port;
  static String file_name;
  static boolean expecting_EOT = false;
  static boolean eot_received = false; 

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
    file_handle = new BufferedReader(new FileReader(file_name));
    file_length = target_file.length();

    // log file handles
    seq_log_handle =new BufferedWriter(new FileWriter("seqnum.log"));
    ack_log_handle = new BufferedWriter(new FileWriter("ack.log"));


    //sender and receiver threads
    sender = new Thread(new Send_Thread()); 
    receive_acks = new Thread(new Ack_Receive()); 

    expecting_EOT = false;  
    
    sender.start();
    receive_acks.start();  
  } //main

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

  public static class Waiter {
    Timer timer;
    int seconds;
    TimerTask waiter_task; 

    public Waiter(int seconds) {
        timer = new Timer();
        this.seconds = seconds; 
    }

    public void startTimerTask()
    {
      System.out.println("Starting Timer...");
      waiter_task = new WaiterTask(); 
      timer.schedule(waiter_task, this.seconds*1000);
    }

    public void stopTimerTask()
    {
      System.out.println("Stopping timer...");
      if(waiter_task != null) {
        System.out.println("Timer isn't null");
        waiter_task.cancel(); 
      }
      System.out.println("Timer stopped."); 
    }

    class WaiterTask extends TimerTask {
        public void run() {
            reTransmit();
            return;  
        }
    }
  }

  public static class Send_Thread implements Runnable {

    public void run(){
      System.out.println("Sender thread kickoff");

      //get file data!! 
       rdtSend();
       return;  
    }
  }

  public static class Ack_Receive implements Runnable {

    public void run(){
      System.out.println("Ack Receive thread kickoff");
      rdtReceive();
      return;   
    }
  }

  public static void rdtSend() {
    int off = 0; 
    char[] cbuf = new char[MaxDataLength]; 
    
    while(file_length - off > 0)
    {
      System.out.println("Still have stuff to send");

      if(windowNotFull())
      {
        //determine length of file left to send
        long len = (file_length - off) > MaxDataLength ? MaxDataLength : (file_length - off);

        //read file using file handle and place into string
        try {
          System.out.println("File size is: " + file_length); 
          System.out.println("Amount to read is: " + len); 
          System.out.println("Offset it " + off);
          System.out.println("Index is " + off+(int)len); 
          int read_len = file_handle.read(cbuf, off, (int)len);
        } catch (IOException e) {
          System.out.println("Error: Failed read of file");
          System.exit(-1); 
        }
        
        String strData = String.copyValueOf(cbuf);
        System.out.println("Data to send: " + strData);
        packet orig_packet;  

        try {
          orig_packet = packet.createPacket(next_seq_num, strData);
          byte[] arr = orig_packet.getUDPdata();
          //create UDP datagrapm from this
          DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

          System.out.println("Sending data packet with sequence: " + orig_packet.getSeqNum()); 

          client_socket.send(send_packet);
          seq_log_handle.write(String.valueOf(orig_packet.getSeqNum()));
          seq_log_handle.newLine();
          next_seq_num = (next_seq_num + 1) % SeqNumModulo;
          addToList(orig_packet);
          System.out.println("Size of list is now: " + not_acked_packets.size()); 
          
          if(timerNeeded())
          {
            System.out.println("We are about to kickoff timer");
            waiter.stopTimerTask();
            waiter.startTimerTask(); 
          }
  
          off = off + (int)len; 
        } catch (Exception e) {
          System.out.println("Error: Failed to create and send packet HERE");
          e.printStackTrace(); 
          System.exit(-1); 
        } 
      }

      try { Thread.sleep(1*1000); } catch (Exception e) { } 

    }//while

    //send EOT, let receiver deal with sending appropriate ACKs and its own EOT
    packet eot_packet; 
    try { 
      eot_packet = packet.createEOT(next_seq_num); 
    
      //get into byte array format
      byte[] arr = eot_packet.getUDPdata();
      //create UDP datagrapm from this
      DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

      System.out.println("Sending EOT packet with sequence: " + eot_packet.getSeqNum()); 

      //UDP formatted datagram sent through client socket to emulator
      client_socket.send(send_packet);
      seq_log_handle.write(String.valueOf(eot_packet.getSeqNum()));
      seq_log_handle.newLine(); 
      next_seq_num = (next_seq_num + 1) % SeqNumModulo;
      addToList(eot_packet);
    } catch (Exception e) { }

    setEotExpected(); 

    while(!eot_received) 
    {
      System.out.println("Waiting for buffer to empty");
      System.out.println("size of linked list is " + not_acked_packets.size());
    }
    try { 
      System.out.println("Closing sequence log handle");
      seq_log_handle.close(); 
    } catch (IOException e) {
      System.out.println("Error: Cannot close file"); 
    }
    return;  

  }

  public static void rdtReceive() {

    try {

        //create buffer to store data in
        byte[] receive_data = new byte[512];

        // convert buffer to UDP format
        DatagramPacket receive_packet = new DatagramPacket(receive_data, receive_data.length);

        //always-on receiver thread for client
        while(true)
        {
          System.out.println("Receiver still on...");
          client_socket.receive(receive_packet);
          System.out.println("Receiver got something!");
          try {
            packet ack_packet = packet.parseUDPdata(receive_packet.getData());

            parseAck(ack_packet); 

            
          } catch (Exception e) {
            System.out.println("Error: Receiver thread failure"); 
          }
          

          try { Thread.sleep(1*1000); } catch (Exception e) { }
          if(eot_received)
          {
            break;
          } 
        }
      } catch (IOException e) {
          System.out.println(e);
      }
    // should close serverSocket in finally block
    //close socket HERE
    System.out.println("EOT Received. Closing client socket"); 

    client_socket.close();
    try { ack_log_handle.close(); } catch (IOException e) {System.out.println("Error: Cannot close ack log file"); }
    waiter.timer.cancel(); 
    return;  
      
  } 
  
  public static synchronized void reTransmit() {

    //kick off another timer
    waiter.stopTimerTask(); 
    waiter.startTimerTask(); 

    for(int i = 0; i < not_acked_packets.size(); i++)
    {

      //retrieve list item
      packet list_packet = not_acked_packets.get(i); 
      //get into byte array format
      byte[] arr = list_packet.getUDPdata(); 

      //create UDP datagrapm from this
      DatagramPacket send_packet = new DatagramPacket(arr, arr.length, emulator_addr, emulator_port);

      //UDP formatted datagram sent through client socket to emulator
      try { client_socket.send(send_packet); } catch (IOException e) {System.out.println("Error: Cannot send packet"); } 

      try { 
        seq_log_handle.write(String.valueOf(list_packet.getSeqNum()));
        seq_log_handle.newLine(); 
      } catch (IOException e) {
        System.out.println("Error: Cannot write seq"); 
      } 
 
    }

  }

  public static synchronized boolean eotParsed(packet ack_packet) { 

    if(ack_packet.getType() == 2 && not_acked_packets.size() == 1) {
      System.out.println("Got EOT of sequence: " + ack_packet.getSeqNum()); 
      not_acked_packets.removeFirst();
      return true; 
    }
    return false; 
  }

  // synchronized methods, only one can happen at a time
  public static synchronized void parseAck(packet ack_packet) {

    try{
      ack_log_handle.write(String.valueOf(ack_packet.getSeqNum()));
      ack_log_handle.newLine();
    } catch (IOException e) {
      e.printStackTrace(); 
    }

    int index = 0;
    System.out.println("type of packet is " + ack_packet.getType()); 

    if(ack_packet.getType() == 0) { //type is an ACK, as we expected
      System.out.println("Got ack with sequence: " + ack_packet.getSeqNum()); 

      for(int i = 0; i < not_acked_packets.size(); i++)
      {
        if(not_acked_packets.get(i).getSeqNum() == ack_packet.getSeqNum())
        {
          index = i; 
          break;
        }
      }

      if(index >= not_acked_packets.size())
      {
        return; //ignore duplicate or ack's that don't reflect our window packets
      }

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
        not_acked_packets.removeFirst();
        j++; 
      }
      
    }
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

  public static synchronized boolean timerNeeded() {
    
    if(base != next_seq_num)
    {
      return true;
    }

    return false; 
  }

  public static synchronized boolean windowNotFull() {
    if(not_acked_packets.size() < N)
    {
      return true; 
    }

    return false; 
  }

  public static synchronized void addToList(packet orig_packet) {
    not_acked_packets.addLast(orig_packet);
  }

  public static synchronized void setEotExpected() {
    expecting_EOT = true; 
  }

  public static synchronized boolean isEotExpected() {
    return expecting_EOT;  
  }

}
