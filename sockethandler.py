__author__ = 'tr1b2669'
import struct
import util
import socket
import errno

class CommonSocketHandler(util.LogMixin):

    def __init__(self,  host, port, common_socket=None):
        util.LogMixin.__init__(self)
        self.socket = common_socket
        self.host = host
        self.port = port

    def receive_msg(self):
        # Read message length and unpack it into an integer
        if not self.socket:
            return None
        raw_msg_len = self.receive_all(4)
        if not raw_msg_len:
            return None
        msg_len = struct.unpack('>I', raw_msg_len)[0]
        # Read the message data
        data = self.receive_all(msg_len)
        self.logger.info('Received')
        self.logger.info("%d bytes: '%s'" % (len(data), data))
        return util.parse(data)

    def receive_all(self, n):
        # Helper function to receive n bytes or return None if EOF is hit
        if not self.socket:
            return None
        data = ''
        while len(data) < n:
            packet = self.socket.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    # noinspection PyAugmentAssignment
    def send_message(self, message):
        if not self.socket:
            return None
        msg = message.deserialize()
        msg = struct.pack('>I', len(msg)) + msg
        self.socket.sendall(msg)



    def is_alive(self):
        connection_is_alive = False
        if not self.socket:
            return connection_is_alive

        timeout = self.socket.gettimeout()
        self.socket.settimeout(0.0)

        try:
            data = self.socket.recv(1024)
            if not data:
                return False
        except socket.error, e:
            if e.args[0] == errno.EWOULDBLOCK:
                connection_is_alive = True

        self.socket.settimeout(timeout)
        return connection_is_alive

    def connect(self,):
        if self.is_alive():
            return True

        try:
            self.socket = socket.socket()
            self.socket.connect((self.host, self.port))
            return True
        except Exception, e:
            print'something\'s wrong with %s:%d. Exception type is %s' % (self.host, self.port, repr(e))
        return False