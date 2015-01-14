__author__ = 'tr1b2669'
import sockethandler
import socket
import controls
import sys
import messages
import errno

class ClientConnector():
    def __init__(self, screen):
        self.client_socket = socket.socket()
        self.screen = screen
        self.received_msg = None
        self.connection = sockethandler.CommonSocketHandler(socket.gethostname(), 9991)
        self.connection_error_dialog = controls.ConnectionErrorDialog(screen)
        self.username_dialog = controls.UserNameDialog(screen)
        self.match_dialog = controls.MatchOrWatchDialog(screen)
        self.finding_dialog = controls.FindingDialog(screen, self.finding_fallback)
        self.username = None

    def connect_and_set_user(self):
        while not self.username:
            self.connection_routine()
            self.username = self.set_username_routine()
        return self.username, self.find_match_routine()

    def finding_fallback(self):
        timeout = self.connection.socket.gettimeout()
        self.connection.socket.settimeout(0.0)
        self.received_msg = self.receive_message()[1]
        self.connection.socket.settimeout(timeout)
        if self.received_msg is None:
            return False
        return True

    def find_match_routine(self):
        finished = False
        match = False
        while not finished:
            while not match:
                match = self.match_dialog.get_answer()

            find_match = messages.FINDMATCH()
            find_match.body.mode = 'match'
            self.send_message(find_match)
            self.finding_dialog.show()
            if self.received_msg:
                if isinstance(self.received_msg, messages.RSPFIRST) or \
                        isinstance(self.received_msg, messages.RSPSECOND):
                    return self.received_msg

    def connection_routine(self):
        while not self.connection.connect():
            if not self.connection_error_dialog.does_retry():
                sys.exit()

    def set_username_routine(self):
        username = self.username_dialog.get_username()
        if not username:
            return username
        connect_message = messages.CONNECT()
        connect_message.body.username = username
        if self.send_message(connect_message):
            response_message = self.connection.receive_msg()
            if not isinstance(response_message, messages.RSPOK):
                username = None
        return username

    def send_message(self, message):
        try:
            self.connection.send_message(message)
        except Exception, e:
            if e.args[0] != errno.EWOULDBLOCK:
                print'something\'s wrong with %s:%d. Exception type is %s' % (
                    self.connection.host, self.connection.port, repr(e))
                self.username = None

            return False
        return True

    def receive_message(self):
        try:
            message = self.connection.receive_msg()
        except Exception, e:
            if e.args[0] != errno.EWOULDBLOCK:
                print'something\'s wrong with %s:%d. Exception type is %s' % (
                    self.connection.host, self.connection.port, repr(e))
                self.username = None
                return False, None

            return True, None

        return True, message
