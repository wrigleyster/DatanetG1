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
        self._kbuckets = [kbucket.KBucket(minRange=0, maxRange=2**160)]
        self.logger = logging.getLogger('RoutingTable')

    def addContact(self, contact):
        """Add a contact to the routing table.
        """
        
        # Ignore this request if the contact has the same node id as we have.        
        if (contact.cid == self._nodeId):
            return

        dist = contact.distance(self.nodeId)

        # Find the kbucket that this contact belongs to.
        i = 0;   
        for kB in self._kbuckets:
            if (kB.inRange(dist)):
                try:
                    # Try adding the contact.                    
                    kB.addContact(contact)
                except kbucket.KBucketException as e:
                    # If a KBucketException is thrown the bucket is full.                    
                                        
                    # Try to split the bucket and add the contact if this is successful.
                    # The buclet will only be splittet, if it contains our own key.
                    # Our own key have the distance 0 and the smallest buket size will
                    # be [2^0,2^1). Therefore
                    if (int(kB.minRange,16) == 0 and int(kB.maxRange,16) == 2):
                        self._splitBucket(i)
                        if (self._kbuckets[i].maxRange < contact.cid):
                            # The contact should be putted in the lowest bucket
                            self._kbuckets[i].addContact(contact)
                        else:
                            # The contact should be putted in the heighest bucket
                            self._kbuckets[i+1].addContact(contact)                            
                            
                    # If it's not possible to split the bucket
                    # ping the last used contacts first.
                    # To se if one of the connections are dead.
                    # We assume, that getCantacts returns the contacts in ascending order
                    # of the frequency of use.
                    else:
                        contacts = kB.getContacts(len(kB))
                        for c in contacts:
                            if not c.ping():
                                # Adding the contact
                                kB.delContact(c)
                                kB.addContact(contact)                                
                        # The contact could not be added to the bucket.                                            
                    return
            i = i+1
                
        
        
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
        
        '''We ensure that the list will remain sorted with the lowest range first.
        Therefore oldIndex should always be 0.'''
        firstPart = self._kbuckets[:oldIndex+1]
        lastPart = self._kbuckets[oldIndex+1:]
        
        self._kbuckets[oldIndex].min
        newBucket = kbucket.KBucket(minRange=0, maxRange=2**6)
        
        
        
        
        """Returning 1 on success. """
        return 0
        
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
