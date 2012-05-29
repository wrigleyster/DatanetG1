#
# file: node.py
#
# author: Tim van Deurzen
#
###############################################################################
# 
# Based on the Node class from the entangled-0.1 kademlia implementation.
#
###############################################################################

import socket
import pickle
import logging

import contact
import routing_table
import kademlia_constants

class DHTMessage:
    def __init__(self, message = "", contact = None):
        self.message = message
        self.contact = contact

class Node(object):
    """A node in the Kademlia DHT.
    """

    def __init__(self, nid, ip, dht_port, chat_port):
        """Initialize a node with id, ip, port and possibly a (previously
        stored) routing table.

        The node id (nid) should be a 160 bit long value (e.g. the result of
        hashing something with the sha1 hash function).
        """

        self.nid = nid
        print("nid: ", nid)
        self._ip = ip
        self._dht_port = int(dht_port)
        self._chat_port = int(chat_port)

        # To be able to add a 'sender' to each message we need ourselves as
        # a contact.
        self.myself = contact.Contact(nid, ip, dht_port, chat_port)
        
        # Get the logger (configured in peer.py).
        self.logger = logging.getLogger('DHTNode')

        self._routing_table = routing_table.RoutingTable(self.nid)

    def addContact(self, contact):
        """Add a contact to the node's routing table.
        """

        # Add a new contact to the routing table.
        self._routing_table.addContact(contact)

    def delContact(self, contact):
        """Remove a contact from the node's routing table.
        """
        self._routing_table.delContact(contact)

        # Remove a contact from the routing table.

    def handle(self, listen_sock):
        """Handle requests that are received and routed to the DHT.
        """

        # Given the dht listening socket from the peer:
        #
        # - accept the connection.
        listen_sock.settimeout(0.1)
        conn = None
        try:
            conn, addr = listen_sock.accept()
        except Exception as e:
            pass
        #
        # - get the data.
        if conn:
            print("got a connection")
            try:
                data = conn.recv(kademlia_constants.MAX_PACKET_SIZE)
                message = pickle.loads(data)
                if message.contact:
                    self.addContact(message.contact)
                parts = message.message.split()
                if parts[0] == "PING":
                    print("PING from " + str(message.contact.cid))
                    response = DHTMessage("PONG")
                    conn.sendall(pickle.dumps(response))
                elif parts[0] == "LOOKUP":
                    if len(parts) <= 1:
                        return                        
                    contact = self._routing_table.getContact(long(parts[1]))
                    if contact:
                        response = DHTMessage("VALUE", contact)
                        conn.sendall(pickle.dumps(response))
                    else:
                        closer = self._routing_table.findNClosestNodes(long(parts[1]), kademlia_constants.k)
                        response = DHTMessage("REDIRECT", closer)
                        conn.sendall(pickle.dumps(response))
                elif parts[0] == "LEAVE":
                    self.delContact(message.contact)
                    
            except Exception as e:
                print e
            conn.close()
        #
        # - respond to the request following the Kademlia protocol.

    def printRoutingTable(self):
        """Print the contents of the routing table.
        """

        self._routing_table.printContacts()

    def findContact(self, contactId):
        """Lookup a contact.
        
        First look in the node's own routing table then in the rest of the DHT.
        This function returns None if no contact was found and a Contact object
        otherwise.
        """

        # Check our own routing table, return if the contact is found.
        contact = self._routing_table.getContact(contactId)
        if contact:
            return contact
        else:
            contact = self.findContactInDHT(contactId)
            if contact:
                return contact
            else:
                return None

        # If the previous search was unsuccessful search through the DHT (i.e.
        # use the overlay network).

    def findContactInDHT(self, contactId):
        """Lookup a contact in the DHT.

        Find a list of initial `close' nodes in our own routing table and
        contact those for information about our contact. The other DHTs may
        respond with the contact information or a list of `closer' nodes.
        """

        # Get a list of the 3 closest nodes in our own routing table. Or
        # simply the entire table if there are less than 3 nodes.
        closer = self._routing_table.findNClosestNodes(contactId, 3)
        print("closest nodes____________________:", closer)
        contacted = []

        # NOTE: Extending the list we are iterating over inside the loop body
        # could lead to an infinite loop. For this reason you should keep a
        # list of already contacted nodes to ensure that we always contact
        # nodes we haven't seen before. Due to the finiteness of the DHT list
        # of members this will ensure that we eventually stop looking.

        # Iterate of the the list of nodes extending it with the new nodes
        # provided by our neighboring nodes.

        while len(closer) > 0:
            print("while running")
            for contact in closer:
                self._routing_table.addContact(contact)
                message = contact.lookup(contactId, self.myself)
                if message:
                    parts = message.message.split()
                    if parts[0] == "VALUE":
                        self.addContact(message.contact)
                        return message.contact
                    elif parts[0] == "REDIRECT":
                        for redirect in message.contact:
                            if redirect not in contacted:
                                closer.append(redirect)
                else:
                    self._routing_table.delContact(contact)
                closer.remove(contact)
                contacted.append(contact)
        return None
                
            
            

            # Add the contact that you are handling now to your own routing
            # table. The first iteration this will simply do nothing other that
            # reorder the contacts in our routing table.

            # Send a lookup request to the current node.

            # If there is no answer, remove the node from your routing table.

            # If there is an answer, we can either get a list of other nodes we
            # have to try, extend the search list with these nodes, removing
            # those we've already seen.
            #
            # If we get back a contact return the contact.


    def joinDHTNetwork(self, knownContact):
        """Given a single known node, join the DHT.
        """

        # Add the known contact to your own routing table.
        self.addContact(knownContact)

        # Search the DHT for your own id.
        self.findContactInDHT(self.myself.cid)

    def leaveDHTNetwork(self):
        """Tell the k closest nodes that we are leaving.
        """
        closeNodes = self._routing_table.findNClosestNodes(self.nid, kademlia_constants.k)
        for contact in closeNodes:
            contact.leave(self.myself)
            

        # Tell your own k closest neighbors that you are leaving.
