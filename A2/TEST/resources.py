import struct
from datetime import datetime
from datetime import timedelta
from threading import Lock


class Tools(object):
    @classmethod
    def to_int(cls, val):
        try:
            val = int(val)
        except:
            print "Data is not an integer"
            val = None

        return val

# Timer class for handling timeout for sender application
class Timer(object):
    _DAY_TO_SECS = 24 * 60 * 60 
    _SECS_TO_MS = 1000.0
    _US_TO_MS = 1/1000.0

    def __init__(self):
        self._start_time = None
        self._timeout = None # timeout in ms
        self._mutex = Lock() # neeede to keep thread safety

    def start(self, timeout):
        self._mutex.acquire()
        self._timeout = timeout
        self._start_time = datetime.now()
        self._mutex.release()
    
    # Check it given timer has timed out
    def timedout(self):
        # Timer has been stopped
        self._mutex.acquire()
        if self._start_time == None:
            self._mutex.release()
            return False

        dt = datetime.now() - self._start_time
        ms = (dt.days * self._DAY_TO_SECS + dt.seconds) * self._DAY_TO_SECS + dt.microseconds * self._US_TO_MS
        timedout = ms > self._timeout
        self._mutex.release()
        
        return timedout

    # Restart timer with current timeout value
    def restart(self):
        self._mutex.acquire()
        if self._timeout == None:
            self._mutex.release()
            print "Error: no timeout value is set"
            return
        
        self._start_time = datetime.now()

        self._mutex.release()

    # Stop timer
    def stop(self):
        self._mutex.acquire()
        self._start_time = None
        self._mutex.release()
        
class Packet(object):
    # Packet types
    _TYPE_ACK = 0
    _TYPE_DATA = 1
    _TYPE_EOT = 2

    _TYPE_DICT = {
        _TYPE_ACK: "ACK",
        _TYPE_DATA: "DATA",
        _TYPE_EOT: "EOT"
    }

    _HEADER_SIZE = 12
    def __init__(self, type_, seqnum, data):
        self._type = type_
        self._seqnum = seqnum
        self._data = data

    def __repr__(self):
        return "<Packet type:%s seqnum:%d  size:%d data:%s>" % (self._TYPE_DICT[self._type], self._seqnum, len(self._data), self._data)

    # Class members accessors
    def get_type(self):
        return self._type
    
    def get_seqnum(self):
        return self._seqnum
    
    def get_length(self):
        return len(self._data)
    
    def get_data(self):
        return self._data
    
    # Check if packet is EOT
    def is_eot_packet(self):
        return self._type == self._TYPE_EOT
    
    # Check if packet is DATA
    def is_data_packet(self):
        return self._type == self._TYPE_DATA

    # Generate udp bytes from class
    def get_udp_data(self):
        n_data = self.get_length()
        buf = bytearray(self._HEADER_SIZE + n_data)
        struct.pack_into(">III%ds"%n_data, buf, 0, self._type, self._seqnum, n_data, self._data)

        return buf
    
    # Class functions to creat the different kinds of packets
    @classmethod
    def create_ack_packet(cls, seqnum):
        return cls(cls._TYPE_ACK, seqnum, "")

    @classmethod
    def create_data_packet(cls, seqnum, data):
        return cls(cls._TYPE_DATA, seqnum, data)

    @classmethod
    def create_eot_packet(cls, seqnum):
        return cls(cls._TYPE_EOT, seqnum, "")

    # Class function to convert udp bytes to packet class
    @classmethod
    def parse_udp_data(cls, udp_data):
        type_, seqnum, data_size = struct.unpack(">III", udp_data[0:12])
        data, = struct.unpack("%ds"%data_size, udp_data[12:12+data_size])
        return cls(type_, seqnum, data)


def main():
    c = Packet.create_data_packet(0, "asdf")
    d = c. get_udp_data()
    # d = "".join(map(chr, d))
    # print d
    print Packet.parse_udp_data(d)    
    

if __name__ == '__main__':
    main()