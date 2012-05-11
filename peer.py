#!/usr/bin/python
#
# file: peer.py
#
# author: Tim van Deurzen
#
# A class that implements a simple chat peer.
#

import socket
import select
import logging
import sys
import time

class ChatPeer:
    """
    Simple chat client that uses a name-server to lookup the address for a
    certain nickname and makes a peer-to-peer connection with that user for the
    actual chat conversation.
    """



    def __init__( self
                , name_server_ip = '127.0.0.1'
                , name_server_port = 3456
                , client_listen_port = 1234
                , listen_queue_size = 5
                ):

        """
        Initialize the ChatPeer setting all the relevant variables to their
        given or default values.
        """

        self.nickname = None

        self.name_server_ip = name_server_ip
        self.name_server_port = name_server_port
        self.name_server_sock = None
        self.connected = False

        self.client_listen_port = client_listen_port
        self.listen_queue_size = listen_queue_size
        self.client_listen_sock = None

        self.BUFFER_SIZE = 1024
        self.TIMEOUT_S = 0
        self.TIMEOUT_L = 10

        # Mapping from peer nicknames to their connection information.
        self.peers = {}

        # Mapping from sockets to nicknames.
        self.socks2names = {}
        self.socks2address = {}
    
        #self.socks2names[sys.stdin] = "stdin"

        # Create a log object.
        logging.basicConfig( filename="ChatPeer.log"
                           , level=logging.DEBUG
                           , format = '[%(asctime)s] %(levelname)s: %(message)s'
                           , filemode='a'
                           )

        self.logger = logging.getLogger('ChatPeer')

        # You should setup the necessary sockets and data structures here. 
        #
        # A peer needs to be able to accept connections from other peers and
        # needs to be connected with the name server. The peer needs to
        # multiplex between all these sockets and respond according to the
        # protocol whenever a message is received.
        #
        # HINT: Have a look at all the imported modules to see which functions
        # they provide.
        #
        # HINT: stdin (for keyboard interaction) can be approached as a socket.


    def setup_name_server(self):
        """
        Try to connect with the name server.
        """

        # Setup the connection with the name server.

        # Use the logger object whenever a significant event occurs (such as
        # successfully or unsuccessfully connecting with the name server).
        try:
            self.name_server_sock = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
            self.name_server_sock.connect((self.name_server_ip,
                                           self.name_server_port))
            return 0
        except Exception as e:
            return 1

    def setup_client_listener(self):
        """
        Try to setup the peer to accept connections from other peers.
        """

        while True:            
            try:
                self.client_listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_listen_sock.bind(('127.0.0.1', self.client_listen_port))
                self.client_listen_sock.listen(self.listen_queue_size)
                break
            except socket.error:
                self.client_listen_port = self.client_listen_port + 1
                print("Port in use. Switching to ", self.client_listen_port)
                continue

        # Set the peer up to accept connections from other peers.      



    def run(self):
        """
        The main ChatPeer loop.
        """

        running = 1
        userinput_help = True

        self.setup_client_listener()
        self.name_server_sock = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
        
        while running:
            # Print a simple prompt.
            #sys.stdout.write('\n> ')
            #sys.stdout.flush()

            # In this loop you should:
            #
            # - Check if the name server is trying to send you a message.
            if self.connected:
                data = self.get_data(self.name_server_sock, True, self.TIMEOUT_S)
                if data:
                    self.parse_and_print(data, self.name_server_sock)
                
            # - Check if a peer is trying to send you a message.

            """ Check alle sockets om der ligger noget """
            for sock in self.socks2names.copy().iterkeys():
                data = self.get_data(sock, True, self.TIMEOUT_S)
                if data:
                    self.parse_and_print(data, sock)
               
               
            # - Check if a new peer is trying to connect with you.
            i, o, e = select.select([self.client_listen_sock], [], [], self.TIMEOUT_S)
            if i:
                conn, addr = self.client_listen_sock.accept()
                if conn:
                    print("PEER connected from: ", addr)
                    self.socks2address[conn] = addr
                    print("Waiting for HANDSHAKE")
                    data = self.get_data(conn, True, self.TIMEOUT_L)
                    if data:
                        self.parse_and_print(data, conn)
                    else:
                        print("HANDSHAKE timed out")
                        conn.sendall("201 REFUSED")
                        self.cleanup_lists(conn)
                        conn.close()
                    
            # - Check if anything was entered on the keyboard.
            if userinput_help:
                print("Press ENTER to input")
                """ Eller ANY key :-) """
                userinput_help = False

            i, o, e = select.select( [sys.stdin], [], [], self.TIMEOUT_S )
            if (i):
                sys.stdin.readline().strip()
                msg = raw_input("Enter Command now: ")
                if len(msg) > 0:
                    self.parse_msg(msg)
            time.sleep(1)
            


    def parse_and_print(self, msg, sock):
        """
        Interpret any commands sent by peers or the name server and
        (potentially) display a message to the user.
        """
        if msg != '':
            parts = msg.split()
            if parts[0] == "100":
                    print("HANDSHAKE with NAMESERVER succesful")
            elif parts[0] == "101":
                print("HANDSHAKE with NAMESERVER unsuccesful: nickname taken")
            elif parts[0] == "102":
                print("HANDSHAKE unsuccesful: server did not receive HELLO")
            elif parts[0] == "201":
                print("PEER refused connection")
                self.cleanup_lists(sock)
                sock.close()
            elif parts[0] == "202":
                print("A PEER expected a HANDSHAKE")
            elif parts[0] == "203":
                print("A PEER expected a HANDSHAKE, but received too few arguments")
            elif parts[0] == "500":
                print("Server says BYE")
            elif parts[0] == "501":
                print("The nameserver did not know the nickname")
            elif parts[0] == "600":
                print(self.socks2names[sock] + " has closed the connection")
            elif parts[0] == "601":
                print("The username was not registered with " + self.socks2names[sock])
            elif parts[0] == "HELLO":
                if len(parts) > 2:
                    self.handshake_peer(sock, self.socks2address[sock], parts[1], parts[2], False)
                else:
                    print("Received HELLO, but too few arguments")
                    sock.sendall("203 HANDSHAKE EXPECTED")
                    self.socks2address.pop(sock)
                    sock.close()
            elif parts[0] == "MSG" and len(parts) > 1:
                if self.socks2names[sock] in self.peers:
                    print(self.socks2names[sock] + ": " + self.concat_string(parts[2:]))
                else:
                    print("A PEER sent a message, but was not registered")
                    sock.sendall("202 REGISTRATION REQUIRED")
            elif parts[0] == "LEAVE" and len(parts) > 1:
                if parts[1] in self.peers:
                    print(parts[1] + " disconnected")
                    sock.sendall("600 BYE")
                    self.cleanup_lists(sock)
                    sock.close()
                else:
                    print("Got a leave request for unknown PEER " + parts[1])
                    sock.sendall("601 ERROR")
            else:
                print("Unknown response: ", msg)
        else:
            print("WARNING: received empty string in parse_and_print")
            self.cleanup_lists(sock)
            sock.close()
        
                

        # You should analyse the message and respond according to the protocol.
        # You may assume that any message that does not adhere to the protocol
        # is garbage and can be discarded.



    def handshake_name_server(self, nickname):
        """
        Register the user with the server using a specific nickname.
        """

        if not self.connected:
            self.logger.warn('Attempted handshake without being connected.')

            print "Not connected to the server."

            return
        
        # Perform the handshake protocol.
        self.name_server_sock.sendall('HELLO ' + self.nickname + ' ' + str(self.client_listen_port))


    def handshake_peer( self
                      , sock
                      , addr
                      , nick = None
                      , port = None
                      , caller = False
                      ):

        """
        Perform a handshake protocol with another peer, either as the caller or
        the callee.
        """
        print("HANDSHAKING with PEER")

        if caller:
            # This peer is initiating the connection and should start the
            # handshake protocol.
            sock.sendall('HELLO ' + self.nickname + ' ' + str(self.client_listen_port))
            data = self.get_data(sock, True, self.TIMEOUT_L)
            if data:
                parts = data.split()
                if parts[0] == "200":
                    self.socks2names[sock] = nick
                    self.peers[nick] = (sock, addr, port)
                    print("Succesfully connected to ", nick)
                    return 0
                else:
                    return 1
            else:
                print("HANDSHAKE with PEER timed out")
                return 1
            # We are responding to a handshake from another peer.
            
        else:
            sock.sendall('200 CONNECTED')
            self.socks2names[sock] = nick
            self.peers[nick] = (sock, addr, port)

    
    def parse_msg(self, msg):
        """
        Parse the user's input and perform the associated action.
        """

        parts = msg.split()

        if parts[0] == "/connect" and len(parts) >= 3:
            if self.connected:
                self.logger.info('Closing name-server connection and opening ' \
                                 'new connection.')

                print 'Disconnecting from name-server and connecting to new ' \
                      'name-server.'
                
                # Close the connection with the name server.
                self.name_server_sock.close()
                self.connected = False

            # Get the hostname and port number from the commandline entered by
            # the user.
            self.name_server_ip = socket.gethostbyname(parts[1])
            self.name_server_port = int(parts[2])

            if self.setup_name_server() is 0:
                self.connected = True
                print("Connected to: " + parts[1] + " using port: " + parts[2])

                if self.nickname is None and len(parts) == 4:
                    self.handshake_name_server(parts[3])
                    print("Registered with: " + parts[1] + " as: " +
                          self.nickname)

                elif self.nickname is None:
                    print "Please choose a nickname and use '/register' to " \
                          "register."

                else:
                    self.handshake_name_server(self.nickname)
            else:
                print "Couldn't establish connection to '%s'." % parts[1]

        elif parts[0] == "/nick" and len(parts) > 1:
            self.nickname = parts[1]
            print("Your nickname is now " + parts[1])

        elif parts[0] == "/register":
            self.handshake_name_server(self.nickname)

        elif parts[0] == "/msg" and len(parts) > 2:
            if parts[1] == self.nickname:
                print "Cannot send a private message to yourself."
                return 

            if parts[1] not in self.peers and self.connected:
                
                # Connect with the peer and peform the handshake protocol.
                output = self.get_nick_addr(parts[1])
                if output:
                    (addr, port) = output
                    print("Trying to get socket using", addr, port)
                    sock = self.connect_to_peer(addr, int(port))
                    print("Received socket: ", sock)
                    if self.handshake_peer(sock, addr, parts[1], int(port), True) is 1:
                        print("HANDSHAKE failed with PEER", parts[1])
                        return
                    else:
                        print("Successfully HANDSHAKED with " + parts[1])
                else:
                    return
                                        
            elif not self.connected:
                self.logger.error('Could not connect to peer because we are ' \
                                  'not connected to the name-server.')

                print "Could not connect to peer '%s'" % parts[1]
                return
                        
            # Send the message to the peer.
            self.send_private_msg(parts[1], ' '.join(parts[2:]))

        elif parts[0] == "/all" and len(parts) > 1:
            self.broadcast(' '.join(parts[1:]))
        
        elif parts[0] == "/leave":
            self.disconnect()

        elif parts[0] == "/quit":
            print 'Shutting down...'

            self.disconnect()
            sys.exit(0)

        
        elif parts[0] == "/auto":
            if self.setup_name_server() is 0:
                self.connected = True
                self.nickname = parts[1]
                self.handshake_name_server(self.nickname)
            else:
                print("Connection to server failed. It may be offline or port is in use")

                
                
            

        else:
            # Either we assume that normal messages (i.e. not commands) are
            # always sent to the last person that received a private mssage or
            # we make normal messages broadcasts.
            
            if self.connected:
                self.parse_msg("/all " + msg)
            else:
                print "Not connected!"


    def broadcast(self, msg):
        """
        Broadcast a message to all connected users.
        """

        # Acquire a list of users from the name server and send the message to
        # all users.
        if self.connected:
            self.name_server_sock.sendall("USERLIST")
            data = self.get_data(self.name_server_sock, True, self.TIMEOUT_L)
            if data:
                parts = data.split()
                if parts[0] == "300" and len(parts) > 3:
                    pointer = 3
                    loops_remaining = int(parts[2])
                    while loops_remaining > 0:
                        nick = parts[pointer]
                        if nick in self.peers:
                            self.send_private_msg(nick, msg)
                        else:
                            ip = parts[pointer + 1]
                            temp = parts[pointer + 2].split(',')
                            port = int(temp[0])
                            sock = self.connect_to_peer(ip, port)
                            if sock and (self.handshake_peer(sock, ip, nick, port, True) is 0):
                                self.send_private_msg(nick, msg)
                        pointer = pointer + 3
                        loops_remaining = loops_remaining - 1                        
                        
                elif parts[0] == "301":
                    print("There are no other users registered with the nameserver")
                else:
                    print("Unexpected response from server: ", data)      
        else:
            print("Please connect to the nameser before broadcasting")




    def disconnect(self):
        """
        Disconnect from the name server and all peers.
        """
        print("Disconnecting")
        # For all of the sockets currently active, except STDIN and our listening
        # socket perform the LEAVE protocol.
        for sock, nick in self.socks2names.copy().iteritems():
            sock.sendall("LEAVE " + self.nickname)
            data = self.get_data(sock, True, self.TIMEOUT_L)
            if data:
                self.parse_and_print(data, sock)
                sock.close()
            else:
                print("Response from " + nick + " timed out")
                sock.close()
        self.name_server_sock.sendall("LEAVE " + self.nickname)
        data = self.get_data(self.name_server_sock, True, self.TIMEOUT_L)
        if data:
            self.parse_and_print(data, self.name_server_sock)
        else:
            print("Response from nameserver timed out")
        self.name_server_sock.close()

        self.peers = {}
        self.socks2names = {}
        self.socks2address = {}
        self.connected = False


    def connect_to_peer(self, addr, port):
        """
        Establish a peer-to-peer connection with another peer.
        """

        # This function should return the newly created socket.
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        return sock

    def send_private_msg(self, nick, msg):
        """
        Send a private message to a peer.
        """

        sock, _, _ = self.peers[nick]

        sock.send('MSG %s %s\n;' % (nick, msg))

    
    def get_nick_addr(self, nick):
        """
        Get the address belonging to a specific nick name.
        """

        # This function should return the ip address and a port number that
        # user 'nick' can be reached at.

        print("Getting user info for " + nick)
        self.name_server_sock.sendall('LOOKUP ' + nick)
        data = self.get_data(self.name_server_sock, True, self.TIMEOUT_L)
        if data:
            print("Server sent this info for " + nick + ":", data)
            parts = data.split()
            if parts[0] == "400":
                return (parts[2], parts[3])
            elif parts[0] == "404":
                print(nick + " is not registered with the nameserver")
                return None
            print("Unkown response from server: ", data)
            return None
        else:
            print("LOOKUP timed out")
            return None
    
    def concat_string(self, string_list):
        max = len(string_list)
        counter = 0
        output = ''
        while counter < max:
            output += string_list[counter] + ' '
            counter = counter + 1
        return output

    def cleanup_lists(self, sock):
        try:
            self.socks2address.pop(sock)
        except Exception as e:
            print("Error cleaning up socks2address: ", e)
        try:
            self.peers.pop(self.socks2names[sock])
        except Exception as e:
            print("Error cleaning up peers: ", e)
        try:
            self.socks2names.pop(sock)
        except Exception as e:
            print("Error cleaning up socks2names: ", e)


    def get_data(self, sock, use_timeout, timeout):
        if use_timeout:
            i, o, e = select.select([sock], [], [], timeout)
            if e:
                print("Error in a socket, closing it")
                self.cleanup_lists(e[0])
                e[0].close()
            elif i:
                try:
                    data = sock.recv(self.BUFFER_SIZE)
                    if data:
                        return data
                    else:
                        return None
                except Exception as e:
                    return None
        else:   
            try:
                data = sock.recv(self.BUFFER_SIZE)
                if data:
                    return data
                else:
                    return None
            except Exception as e:
                return None
        

            

###
### Main method, run the peer with default values or a custom listening port.
###

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Interpret the first command-line argument as the port number this
            # peer will listen on.
            CP = ChatPeer(client_listen_port = int(sys.argv[1]))
            CP.run()
        else:
            CP = ChatPeer()
            CP.run()
    except KeyboardInterrupt:
        CP.disconnect()
        CP.client_listen_sock.close()
