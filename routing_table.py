#
# file: routing_table.py
#
# author: Tim van Deurzen
#
###############################################################################
# 
# Based on the RoutingTable class from the entangled-0.1 kademlia
# implementation.
#
###############################################################################

import socket
import logging

import kbucket
import kademlia_constants


class RoutingTable(object):
    """A class implementation of the Kademlia routing protocol.
    """

    def __init__(self, nodeId):
        """Initialize the list of kbuckets and the node's id.
        """

        self._nodeId = nodeId
        self._kbuckets = [kbucket.KBucket(minRange=0, maxRange=2**6)]
        self.logger = logging.getLogger('RoutingTable')

    def addContact(self, contact):
        """Add a contact to the routing table.
        """

        # Ignore this request if the contact has the same node id as we have.

        # Find the kbucket that this contact belongs to.

        # Try adding the contact.
        #
        # If a KBucketException is thrown the bucket is full.
        #
        # Try to split the bucket and add the contact if this is successful.
        #
        # If we can't split, in order ping each node starting at the MOST
        # RECENTLY USED node. Ping each node and remove the node if it does not
        # respond.

    def getContact(self, contactId):
        """Retrieve a contact from our own routing table.
        """

        # Find the contact in the correct kbucket and return it. If the contact
        # cannot be found return None.

    def delContact(self, contact):
        """Remove a specific contact from the routing table if that contact
        is in the list.
        """

        # Remove the contact from the correct kbucket or just return if the
        # contact was not in any bucket.

    def pingContact(self, contact):
        """Send a PING message to a contact to check if the contact is
        still alive.
        """
        
        # Ping a contact returning True if the ping was answered, and false
        # otherwise.

    def findNClosestNodes(self, contactId, n):
        """Find the N closest nodes to contactId in our own routing table. 

        If there are less than n, we just return those.
        """

        # Select the n closest nodes to contactId that are available in our
        # routing table. Extend the list using nodes that are further away
        # until you have n. If there are fewer than n, return everything we
        # have.

    def _splitBucket(self, oldIndex):
        """Split a kbucket into two bucket covering the same range.
        """

        # Resize the range of the current (old) k-bucket.

        # Create a new k-bucket to cover the range split off from the old
        # bucket.

        # Now, add the new bucket into the routing table.

        # Finally, copy all nodes that belong to the new k-bucket into it...

        # ...and remove them from the old bucket

    def _kbucketIndex(self, contactId):
        """Find the index of the kbucket in which range the contactId lies.
        """

        # Check each kbucket to see of the contactId is in range of that
        # bucket. return the index of bucket that contains this contactId.

    def printContacts(self):
        """Print all the contact in all the kbuckets.
        """

        for kbucket in self._kbuckets:
            for contact in kbucket._contacts:
                print contact
