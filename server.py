#!/usr/bin/python
#
# file: server.py
#
# author: Tim van Deurzen
#
# A class that implements a simple chat server.
#
import time ###@@@ added
import socket
import select
import logging

class PeerHandle:
    def __init__(self,sock,ip,port=None,nick=None):
        print "Creating peerhandle"
        self.sock = sock
        self.ip = ip
        self.port = int(port) if port else None
        self.nick = nick
        self.scheduled_for_removal = False
        print "created peerhandle"
    def __str__(self):
        return "%s on %s:%d" % (self.nick,self.ip,self.port)
    
BUFFER_SIZE = 1024
    
class NameServer:
    """
    A simple name server used to map nick names to addresses.
    """
    
    def __init__(self, port = 3456, listen_queue_size = 5):
        """
        Initialize the variables required by the name server.
        """

        self.port = port
        self.CLIENT_TIMEOUT = 0 #client timeout for sockets

        # peer info stored here
        self.peerhandles = []
        
        

            
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
        # Set the socket options to allow reuse of the server address and bind
        # the socket.
        
        print('creating listen socket...')
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.bind(('127.0.0.1',port))
        self.listen_sock.listen(5);
        print('bind to port %d'% port)
        


    def get_peerhandle_by_nick(self, nick):
        """
        Get the info of a client by looking the client up by nickname.
        """
        for ph in self.peerhandles:
            if ph.nick == nick:
                return ph
        return None

    
    def handshake(self, peerhandle, parts):
        """
        Perform a handshake protocol with the new client.
        """
        if len(parts)<3 or int(parts[2])<1024:
            self.logger.info("From %s: Received HELLO but syntax invalid." % peerhandle.ip)
            peerhandle.sock.sendall("102 REGISTRATION REQUIRED\n;")
            #peerhandle.sock.close()
            #peerhandle.scheduled_for_removal = True
            return 102 # REGISTRATION REQUIRED
        for ph in self.peerhandles:
            if ph.nick == parts[1]:
                self.logger.info("%s tried to register %s, but that nick is taken" % (peerhandle.ip,parts[1]))
                peerhandle.sock.sendall("101 TAKEN\n;")
                #peerhandle.sock.close()
                #peerhandle.scheduled_for_removal = True
                return 101 # TAKEN
        peerhandle.nick = parts[1]
        peerhandle.port = int(parts[2])
        self.logger.info("Registered %s" % peerhandle)
        peerhandle.sock.sendall("100 CONNECTED\n;")
        return 100 # CONNECTED

    def wave(self,peerhandle,parts):
        if parts[1:2] and parts[1]!= peerhandle.nick:
            # parts[1:2] evaluates to parts[1] if set or [] if empty
            self.logger.info("%s tried to leave as %s" % (peerhandle,parts[1]))
            peerhandle.sock.sendall("501 ERROR\n;")
            return 501 # ERROR
        peerhandle.sock.sendall("500 BYE\n;")
        peerhandle.sock.close()
        peerhandle.scheduled_for_removal = True
        return 500 # BYE
        
    def lusers(self,peerhandle,parts):
        self.logger.info('Request for list of users.')

        # The requesting user is also in this list so we subtract 1.
        num_users = len(self.peerhandles) - 1
        if num_users:
            first = True
            msg = "300 INFO %d" % num_users
            for ph in self.peerhandles:
                if ph.nick == peerhandle.nick:
                    continue
                if not first:
                    msg += ","
                if first:
                    first = False
                msg += " %s %s %s" %(ph.nick, ph.ip, ph.port)
            self.logger.info('Sending list of %d users.' % num_users)
            peerhandle.sock.sendall(msg + "\n;")
            return 300 # INFO <num peers> <info array>
        self.logger.info('No users online save the requesting user')
        peerhandle.sock.sendall("301 ONLY USER\n;")
        return 301 # ONLY USER

        
    def client_accept(self, timeout):
        i , o, e = select.select([self.listen_sock], [], [], timeout)
        if i:
            try:
                conn, addr = self.listen_sock.accept()
                ip,port = addr
                print "connected: ",addr
                self.peerhandles.append(PeerHandle(conn,ip))
                print "Connect from ", addr
            except socket.error as e:
                return
            return 0
        
    
    def run(self):
        """
        The main loop of the chat server.
        """

        running = 1
        while running:
            # This loop should:             
        
            # - Accept new connections.
            self.client_accept(self.CLIENT_TIMEOUT)
            
            for ph in self.peerhandles:
                try:
                    sock = self.check_sock(ph, self.CLIENT_TIMEOUT)
                    if sock:
                        request = ph.sock.recv(BUFFER_SIZE)
                        if request == "":
                            print("Warning: a socket contained an empty string, closing it now")
                            sock.close()
                            self.peerhandles.remove(ph)
                        else:
                            print "Received: \n%s" % request
                            self.parse_data(request,ph)
                except socket.error as e:
                    print("Error in socket from ", ph.nick)
                    continue                
                
            
            for ph in self.peerhandles[:]:
                if ph.scheduled_for_removal:
                    self.peerhandles.remove(ph)
            time.sleep(1)
        
           
        
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


    def lookup_nick(self, peerhandle, nick):
        """
        Lookup a nickname and respond to the request appropriately.
        """

        info_ph = self.get_peerhandle_by_nick(nick)
        if info_ph:
            self.logger.info('Sending user info for %s.' % nick)
            peerhandle.sock.sendall('400 INFO %s %s\n;' % (info_ph.ip, info_ph.port))
            return 400 # INFO <ip_addr> <port>
        self.logger.info('User %s not found.' % nick)
        peerhandle.sock.sendall('404 USER NOT FOUND\n;')
        return 404 # USER NOT FOUND


    def parse_data(self, data, peerhandle):
        """
        Parse the incoming data and act accordingly.
        """
        
        parts = data.split()
        if not parts:
            return 000 # no response
        
        if parts[0] == "HELLO":
            return self.handshake(peerhandle,parts)
        elif peerhandle.nick:
        #elif reduce(lambda x,ph: x or ph.sock==peerhandle.sock,self.peerhandles):
        #'- Read: elif sock in peerhandles
            if parts[0] == "LOOKUP" and len(parts) > 1:
                self.logger.info('Lookup requested for nick %s.' % parts[1])
                self.lookup_nick(peerhandle, parts[1])

            elif parts[0] == "LEAVE":
                return self.wave(peerhandle,parts)

            elif parts[0] == "USERLIST":
                return self.lusers(peerhandle,parts)
            else:
                return 000 # no response
        else:
            self.logger.info("%s failed to register." % str(peerhandle.ip))
            peerhandle.sock.sendall("102 REGISTRATION REQUIRED\n;")
            #peerhandle.sock.close()
            #peerhandle.scheduled_for_removal = True
            return 102 # REGISTRATION REQUIRED

    def check_sock(self, peerhandle, timeout):
        i, o, e = select.select([peerhandle.sock], [], [], timeout)
        if e:
            print("Error in a socket, closing it")
            e[0].close
            self.peerhandles.remove(peerhandle)
            return None
        elif (i):
            return i[0]
        else:
            return None
                    
                
###
### Main method, run the server with all the default values.
###

if __name__ == "__main__":
    try:
        NS = NameServer()
        NS.run()
    except KeyboardInterrupt:
        print "\nInterrupted, exiting..."
        NS.listen_sock.close()
