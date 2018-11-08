from resources import Packet, Tools
import socket
from threading import Thread
import signal
import sys

class Emulator(object):
    _AUTO_PORT = 0 # binding socket to port 0 ensures that an available port is selected
    _LOCAL_ADDRESS = "" # binding socket to address "" inidicates localhost
    _MAX_PACKET_SIZE = 512 # assumed maximum size of data expected
    _TIMEOUT = 0.5
    def __init__(self, send_addr, send_port_in, send_port_out, recv_addr, recv_port_in, recv_port_out):
        self._send_addr = send_addr
        self._send_port_in = send_port_in
        self._send_port_out = send_port_out
        self._recv_addr = recv_addr
        self._recv_port_in = recv_port_in
        self._recv_port_out = recv_port_out

        self._running = False
        self._data_thread = Thread(target=self._data_thread_helper)
        self._ack_thread = Thread(target=self._ack_thread_helper)

        self._data_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._data_udp_sock.bind((self._LOCAL_ADDRESS, self._send_port_in))

        self._ack_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._ack_udp_sock.bind((self._LOCAL_ADDRESS, self._recv_port_in))
        
        self._ack_send_later = []
        self._data_send_later = []

        self._data_count = 0
        self._ack_count = 0

        self._skip = True
        self._case = None

    def is_running(self):
        return self._running

    def run(self, case=1):
        self._case = case
        self._running = True

        # start threads
        self._data_thread.start()
        self._ack_thread.start()
    
    def kill(self):
        self._running = False

        # start threads
        self._data_thread.join()
        self._ack_thread.join()

    def _data_thread_helper(self):
        self._data_udp_sock.settimeout(self._TIMEOUT)
        while(self._running):
            # wait for data
            try:
                data, _unused_ = self._data_udp_sock.recvfrom(self._MAX_PACKET_SIZE)
            except socket.timeout:
                continue

            packet = Packet.parse_udp_data(data)
            print "Sender: ", packet.get_seqnum()

            self._data_count += 1
            # Simulate cases

            if self._case == 1:
                # Case 1
                if packet.get_seqnum() == 0 and self._skip:
                    self._skip = False
                    continue
            elif self._case == 2:
                # Case 2
                if packet.get_seqnum() == 2:
                    self._data_send_later.append(packet)
                    continue
                
                if packet.get_seqnum() == 4:
                    for p in self._data_send_later:
                        buffer = p.get_udp_data()
                        self._data_udp_sock.sendto(buffer, (self._recv_addr, self._recv_port_out))
                    self._data_send_later = []

                if packet.get_seqnum() == 5 and self._skip:
                    self._skip = False
                    continue
            elif self._case == 3:
                # Case 3
                if packet.get_seqnum() == 5 and self._skip:
                    self._skip = False
                    continue
            elif self._case == 5:
                # Case 5
                if self._data_count == 11:
                    print "discarding", packet
                    continue
            
                if self._data_count == 36:
                    print "delaying", packet
                    self._data_send_later.append(packet)
                    continue
                
                if self._data_count == 38:
                    for p in self._data_send_later:
                        print  "resending", packet
                        buffer = p.get_udp_data()
                        self._data_udp_sock.sendto(buffer, (self._recv_addr, self._recv_port_out))
                    self._data_send_later = []
            
            # forward if necessary
            buffer = packet.get_udp_data()
            self._data_udp_sock.sendto(buffer, (self._recv_addr, self._recv_port_out))
            
    def _ack_thread_helper(self):
        self._ack_udp_sock.settimeout(self._TIMEOUT)
        while(self._running):
            # wait for data
            try:
                data, _unused_ = self._ack_udp_sock.recvfrom(self._MAX_PACKET_SIZE)
            except socket.timeout:
                continue

            packet = Packet.parse_udp_data(data)
            print "Receiver: ", packet.get_seqnum()

            self._ack_count += 1

            # decide to drop
            if self._case == 4:
                # Case 4
                if packet.get_seqnum() == 1:
                    self._ack_send_later.append(packet)
                    continue 

                if packet.get_seqnum() == 3:
                    for p in self._ack_send_later:
                        print p
                        buffer = p.get_udp_data()
                        self._ack_udp_sock.sendto(buffer, (self._send_addr, self._send_port_out))
                    self._send_later = []
                
                if packet.get_seqnum() == 4:
                    continue
                
                if packet.get_seqnum() == 6 and self._skip:
                    self._skip = False
                    continue
            elif self._case == 5:
                # Case 5
                if self._ack_count == 6:
                    print "discarding", packet
                    continue
                
                if self._ack_count == 47:
                    print "delaying", packet
                    self._ack_send_later.append(packet)
                    continue
                
                if self._ack_count == 49:
                    for p in self._ack_send_later:
                        print  "resending", p
                        buffer = p.get_udp_data()
                        self._ack_udp_sock.sendto(buffer, (self._send_addr, self._send_port_out))
                    self._ack_send_later = []

            # forward if necessary
            buffer = packet.get_udp_data()
            self._ack_udp_sock.sendto(buffer, (self._send_addr, self._send_port_out))

            if (packet.is_eot_packet()):
                self._running = False

global em
global running
def signal_handler(sig, frame):
    global running
    print('You pressed Ctrl+C!')
    em.kill()
    running = False

def main():
    signal.signal(signal.SIGINT, signal_handler)
    global em
    global running

    running = True

    # get test case
    test_case = Tools.to_int(sys.argv[1])

    # Change this to fit your situation
    send_addr = "localhost"
    send_port_in = 2001 # sender port coming in
    send_port_out = 2004 # sender port going out
    recv_addr = "localhost" 
    recv_port_in = 2003
    recv_port_out = 2002

    em = Emulator(send_addr, send_port_in, send_port_out, recv_addr, recv_port_in, recv_port_out)
    em.run(test_case)

    while(em.is_running()):
        pass

if __name__ == '__main__':
    main()