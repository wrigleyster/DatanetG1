#!/usr/bin/python
#
# file: server.py
#
# author: Tim van Deurzen
#
# A class that implements a simple chat server.
#

import socket
import select
import logging


class NameServer:
    """
    A simple name server used to map nick names to addresses. 
    """


    BUFFER_SIZE = 1024


    def __init__(self, port = 3456, listen_queue_size = 5):
        """
        Initialize the variables required by the name server.
        """

        self.port = port

        # A mapping from names to the associated information (port, socket,
        # ip address, ...).
        self.names2info = {}

        # A mapping from sockets to names.
        self.socks2names = {}
        
        

        # Create a log object.
        # logging.basicConfig( filename="NameServer.log"
        #                    , level=logging.DEBUG
        #                    , format = '[%(asctime)s] %(levelname)s: %(message)s'
        #                    , filemode='a'
        #                    )

        # Or, for debugging purposes: log to the console.
        logging.basicConfig( level=logging.DEBUG
                           , format = '[%(asctime)s] %(levelname)s: %(message)s'
                           )

        self.logger = logging.getLogger('NameServer')

 
        # Initialize the socket and data structures needed for the server.
        #
        
        # A temporary mapping from socket to address used before handshake
        self.sock2address = {}
        
        # Set the socket options to allow reuse of the server address and bind
        # the socket.
        
        print('creating listen socket...')
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.bind(('127.0.0.1',port))
        self.listen_sock.listen(5);
        self.listen_sock.setblocking(0)
        print('bind to port %d'% port)
        


    def get_info_by_name(self, name):
        """
        Get the info of a client by looking the client up by nickname.
        """

        if name in self.names2info:
            return self.names2info[name]

        return None

    
    def handshake(self, sock, addr):
        """
        Perform a handshake protocol with the new client.
        """
        try:
            data  = sock.recv(NameServer.BUFFER_SIZE)
            parts = data.split()            
    
            if parts[0] == "HELLO" and len(parts) >= 3:
                if parts[1] in self.names2info:
                    sock.send('101 TAKEN')
                    sock.close()
                else:
                    self.name2info[parts[1]] = (pars[2],sock,addr)
                    self.sock2name[sock] = parts[1]
                    sock.send('100 CONNECTED')
            else:
                sock.send('102 REGISTRATION REQUIRED')
                sock.close()
            self.sock2address.remove(sock)
        except:
            return
        # Inspect the data and respond according to the protocol.
        
    def client_accept(self):
        try:
            while 1:
                conn, addr = self.listen_sock.accept()
                print "connected: ",addr
                #conn.setblocking(0)
                self.sock2address[conn] = addr
                print "Connect from ", addr
                self.handshake(conn, addr)
        except Exception as e:
            return 0
        
    
    def run(self):
        """
        The main loop of the chat server.
        """

        running = 1

        while running:
            # This loop should:
            # 
            # - Accept new connections.
            self.client_accept()
            # Handshaking with new connections 
            for sock, addr in self.socks2names.iteritems():
                self.handshake(sock,addr)
            
                
            # - Read any socket that wants to send information.
            #
            # - Respond to messages that are received according to the rules in
            # the protocol. Any message that does not adhere to the protocol
            # may be ignored.
            #
            # - Clean up sockets that are dead.
            #
            # This loop should perform multiplexing among all sockets that are
            # currently active. 
            #
            # HINT: Look at all the imported modules to see which functionality
            # they provide.

            running = 0
    
        # Close the server socket when exiting.


    def lookup_nick(self, sock, nick):
        """
        Lookup a nickname and respond to the request appropriately.
        """

        info = self.get_info_by_name(nick)
        if info:
            s, (a, _), p = info
            self.logger.info('Sending user info for %s.' % nick)
            sock.send('400 INFO %s %s\n;' % (a, p))
        else:
            self.logger.info('User %s not found.' % nick)
            sock.send('404 USER NOT FOUND\n;')


    def parse_data(self, data, sock):
        """
        Parse the incomming data and act accordingly.
        """

        parts = data.split()

        if parts[0] == "LOOKUP" and len(parts) > 1:
            self.logger.info('Lookup requested for nick %s.' % parts[1])
            self.lookup_nick(sock, parts[1])

        elif parts[0] == "LEAVE":
            if parts[1] in self.names2info.iterkeys():
                pass

                # self.logger.info('User %s disconnected from service.' \
                #                  % parts[1])

                # sock.send("500 BYE\n;")

                # Remove the socket from all relevant data structures and close
                # it.

        elif parts[0] == "USERLIST":
            self.logger.info('Request for list of users.')

            # The requesting user is also in this list so we subtract 1.
            num_users = len(self.names2info) - 1
            first = True

            msg = "300 INFO %d" % num_users

            for name in self.names2info:
                s, (ip, _), port = self.names2info[name]

                if s == sock:
                    continue

                if not first:
                    msg += ","

                msg += " %s %s %s" %(name, ip, port)

                if first:
                    first = False

            
            self.logger.info('Sending list of %d users.' % num_users)
            sock.send(msg + "\n;")
                
            
###
### Main method, run the server with all the default values.
###

if __name__ == "__main__":
    NameServer().run()
