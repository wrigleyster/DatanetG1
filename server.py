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
import time
import sys


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
        self.counter = 0

        # A mapping from names to the associated information (socket, ip,
        # port, ...).
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
        print('creating listen socket...')
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.bind(('',self.port))
        self.listen_sock.listen(5)
        
        
        # Set the socket options to allow reuse of the server address and bind
        # the socket.        


    def get_info_by_name(self, name):
        """
        Get the info of a client by looking the client up by nickname.
        """

        print("length_______", len(self.names2info))
        print("The data is___________", self.names2info[name])
        if name in self.names2info:
            return self.names2info[name]

        return None

    def check_sock(self, sock, timeout):
        i, o, e = select.select( [sock], [], [], timeout)
        if (i):
            return True
        else:
            return False

    def build_line(self, counter):
        self.counter = counter + 1
        if counter < 0:
            self.counter = 0
        else:
            if counter >= 7:
                self.counter = 0
            output = "-----"
            while counter > 0:
                output = output + " -----"
                counter = counter - 1
            
            return output
                

    
    def handshake(self, sock, addr):
        """
        Perform a handshake protocol with the new client.
        """
        try:
            print("HANDSHAKING for ", sock, addr)
            data  = sock.recv(self.BUFFER_SIZE)
            parts = data.split()
    
            if parts[0] == "HELLO" and len(parts) >= 3:
                if parts[1] in self.names2info:
                    sock.sendall('101 TAKEN')
                    sock.close()
                else:                    
                    self.socks2names[sock] = parts[1]
                    print ("HANDSHAKE accepted for ", parts[1])
                    self.names2info[parts[1]] = (sock, addr, parts[2])
                    sock.sendall('100 CONNECTED')
            else:
                sock.sendall('102 REGISTRATION REQUIRED')
            
        except:
            return
        # Inspect the data and respond according to the protocol.
        
    
    def run(self):
        """
        The main loop of the chat server.
        """

        running = 1
        while running:
            
            sys.stdout.write('\n> ')
            sys.stdout.flush()
            
            # This loop should:             
        
            # - Accept new connections.
            
            if self.check_sock(self.listen_sock, 1):
                sock, addr = self.listen_sock.accept()
                if sock:
                    print("Getting CONNECTION from ", addr)
                    self.handshake(sock, addr)
            else:
                print("No new CONNECTIONS")
            time.sleep(1)
            # Handshaking with new connections
        
            # - Read any socket that wants to send information.
            print("socks2names LENGTH: ", len(self.socks2names))

            i, o, e = select.select( self.socks2names.iterkeys(), [], [], 1)
            if (i):
                for sock in i:                            
                    print("checking for DATA")
                    data = sock.recv(self.BUFFER_SIZE)
                    if data != '':
                        print("OMG, i got data: ", data)
                        self.parse_data(data,sock)
                    else:
                        print("Warning: received '', socket probably dead")
                        self.names2info.pop(self.socks2names[sock])
                        self.socks2names.pop(sock)
            else:
                print("No new MESSAGES in socks2names")

            time.sleep(1)                
            print("Sleeping 2 sec and LOOPING " + self.build_line(self.counter))
            time.sleep(2)
               
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
            # running = 0
     
        # Close the server socket when exiting.


    def lookup_nick(self, sock, nick):
        """
        Lookup a nickname and respond to the request appropriately.
        """

        info = self.get_info_by_name(nick)
        print("lookup_nick running")
        if info:
            s, (a, _), p = info
            print("logging info")
            self.logger.info('Sending user info for %s.' % nick)
            print('400 INFO %s %s\n;' % (a, p))
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
        else: sock.send('999 ERROR Data not recognized')
            
                
            
###
### Main method, run the server with all the default values.
###

if __name__ == "__main__":
    try:
        NS = NameServer()
        NS.run()
    except KeyboardInterrupt:
        NS.listen_sock.close()
    
