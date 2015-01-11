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

    def connect_and_set_user(self):
        username = None
        while not username:
            self.connection_routine()
            username = self.set_username_routine()
        return username, self.find_match_routine()

    def finding_fallback(self):
        timeout = self.connection.socket.gettimeout()
        self.connection.socket.settimeout(0.0)
        try:
            self.received_msg = self.connection.receive_msg()
        except socket.error, e:
            pass
            # if e.args[0] == errno.EWOULDBLOCK:
        self.connection.socket.settimeout(timeout)
        if not self.received_msg:
            return False
        return True

    def find_match_routine(self):
        finished = False
        is_white = False
        match = False
        while not finished:
            while not match:
                match = self.match_dialog.get_answer()

            find_match = messages.FINDMATCH()
            find_match.body.mode = 'match'
            self.connection.send_message(find_match)
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
        try:
            self.connection.send_message(connect_message)
            response_message = self.connection.receive_msg()
            if not isinstance(response_message, messages.RSPOK):
                username = None
        except Exception, e:
            print'something\'s wrong with %s:%d. Exception type is %s' % (
                self.connection.host, self.connection.port, repr(e))
            return None

        return username


