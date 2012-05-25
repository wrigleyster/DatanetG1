#
# file: contact.py
#
# author: Tim van Deurzen
#
###############################################################################
#
# Based on the Contact class from entangled-0.1
#
###############################################################################

import socket
import pickle

import kademlia_constants


class Contact(object):
    """A contact in the DHT.

    A contact has an IP address a dht_port and a chat_port as its contact
    information.
    """
    
    MAX_PACKET_SIZE = 1024

    def __init__(self, cid, ip, dht_port, chat_port):
        """Initialize a contact with an ip address a chat port and a dht port
        number.
        """

        self.cid = long(cid)
        self.ip = ip
        self.dht_port = int(dht_port)
        self.chat_port = int(chat_port)

    def __eq__(self, other):
        """Check for equality between this contact and another contact.

        The case where 'other' is a long may be used when looking for a
        specific contact id in a list of Contact objects.
        """

        if isinstance(other, Contact):
            return self.cid == other.cid
        elif isinstance(other, long):
            return self.cid == other
        else:
            return False

    def __ne__(self, other):
        """Check for inequality between this contact and another contact.

        The case where 'other' is a long may be used when looking for a
        specific contact id in a list of Contact objects.
        """

        if isinstance(other, Contact):
            return self.cid != other.cid
        elif isinstance(other, long):
            return self.cid != other
        else:
            return True

    def __str__(self):
        """Return a string representation of a contact.
        """
        
        return '<%s.%s object; IP address: %s, TCP dht_port: %d, id: %.5d >' % \
                (self.__module__, self.__class__.__name__, self.ip, self.dht_port, self.cid) 

    def distance(self, other):
        """Calculate the distance using XOR between two contacts.
        """

        # Make sure that 'other' is either a 'long' value or an object of type
        # Contact and calculate the distance between this contact and the
        # other.

        if type(other) == type(0L):
            return self.cid^other
        else:
            try:
                dist = self.cid^other.cid
                return dist
            except Exception as e:
                return None
            

    def _send(self, request):
        """Send a request to this contact.

        Return a dictionary upon result or None upon failure.
        """

        # Create a TCP socket to this socket.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.dht_port))        

        # Send the message as a serialized (pickled) dictionary.
        sock.sendall(pickle.dumps(request))

        # Wait for a response.
        data = None
        try:
            data = sock.recv(MAX_PACKET_SIZE)
        except Exception as e:
            sock.close()

        # Upon response deserialize the result (unpickle) and return the
        # dictionary.

        if data:
            msg = picke.loads(data)
            return msg
        else:
            return None
            
        # When an exception is thrown return None.

    def ping(self):
        """Send a ping request to this contact.
        """

        # Send a PING request using the _send method.

    def lookup(self, contactId, sender):
        """Send a look up request to this contact.
        """
        
        # Send a lookup request using the _send method, using 'sender' to
        # identify the sending contact. The 'sender' variable should be an
        # object of type Contact.

    def leave(self, contact):
        """Announce to this contact that the node/contact with contactId is
        leaving.
        """

        # Send a leave message to this contact using the _send method.
