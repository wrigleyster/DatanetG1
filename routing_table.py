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

"""In this framework we have to  """
import math


class RoutingTable(object):
    """A class implementation of the Kademlia routing protocol.
    """

    def __init__(self, nodeId):
        """Initialize the list of kbuckets and the node's id.
        """

        self._nodeId = nodeId
        self._kbuckets = [kbucket.KBucket(minRange=0, maxRange=2**160)]
        self.logger = logging.getLogger('RoutingTable')


    def __str__(self):
        
        out = "\n--------------\nPrinting routing table"
        for kB in self._kbuckets:
            out += "\n kbucket range [" + str(kB.minRange) + "," + str(kB.maxRange) + "]"
            for c in kB._contacts:
                out += "\nCid = " + str(c.cid) + "\n\tdistance =  " + str(c.distance(self._nodeId)) + "\n\tIn range = " + str(kB.inRange(c.distance(self._nodeId)))
            out +="\n"
        return out

    def addContact(self, contact):
        """Add a contact to the routing table.
        """
        
        # Ignore this request if the contact has the same node id as we have.        
        if (contact.cid == self._nodeId):
            return

        dist = contact.distance(self._nodeId)

        # Find the kbucket that this contact belongs to.
        i = 0;   
        for kB in self._kbuckets:
            if (kB.inRange(dist)):
                try:
                    # Try adding the contact.                    
                    kB.addContact(contact)
                except kbucket.KBucketException as e:
                    print e
                    # If a KBucketException is thrown the bucket is full.                    
                                        
                    # Try to split the bucket and add the contact if this is successful.
                    # The bucket will only be split, if it contains our own key.
                    # Our own key have the distance 0 and the smallest bucket size will
                    # be [2^0,2^1). Therefore
                    print("Splitting a bucket")
                    if (kB.minRange == 0 and kB.maxRange >= 4):
                        self._splitBucket(i)
                        
                        # Since bucket i have lower range than i+1 then we only have to
                        # check maxRange.
                        if (self._kbuckets[i].maxRange > contact.distance(self._nodeId)):
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
                                return
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
        """

        for kB in self._kbuckets:
            for c in kB._contacts:
                if c.cid == contactId:
                    return c
        return None
    """
        index = self._kbucketIndex(contactId)
        kB = self._kbuckets[index]
        try:
            return kB.getContact(contactId)
        except kbucket.KBucketException:
            return None
        
        
        # Find the contact in the correct kbucket and return it. If the contact
        # cannot be found return None.

    def delContact(self, contact):
        """Remove a specific contact from the routing table if that contact
        is in the list.
        """
        
        index = self._kbucketIndex(contact.cid)
        kB = self._kbuckets[index]
        kB.delContact(contact)
        return

        # Remove the contact from the correct kbucket or just return if the
        # contact was not in any bucket.

    def pingContact(self, contact):
        """Send a PING message to a contact to check if the contact is
        still alive.
        """
        return contact.ping()
        
        # Ping a contact returning True if the ping was answered, and false
        # otherwise.

    def findNClosestNodes(self, contactId, n):
        """Find the N closest nodes to contactId in our own routing table. 

        If there are less than n, we just return those.
        """
        
        # Finding the bucket which should containg the contact and it's neightbours
        index = self._kbucketIndex(contactId)
        kB = self._kbuckets[index]      
        contacts = kB.getContacts(kademlia_constants.k)
        
        # Sortin the contacts from kB after the distance to contactId
        contacts = sorted(contacts,key=lambda c: c.distance(contactId))
        
        if n < len(contacts):
            return contacts[:n]
            
        while (index >= 0):
            index = index - 1
            contacts = contacts + self._kbuckets[index].getContacts(kademlia_constants.k)
                
        contacts = sorted(contacts,key=lambda c: c.distance(contactId))
        return contacts[:n]
    
    
        # Select the n closest nodes to contactId that are available in our
        # routing table. Extend the list using nodes that are further away
        # until you have n. If there are fewer than n, return everything we
        # have.

    def _splitBucket(self, oldIndex):
        """Split a kbucket into two bucket covering the same range.
        """
        
        # We ensure that the list will remain sorted with the lowest range first.
        # Therefore oldIndex should always be 0.
        if oldIndex != 0:
            Print("Trying to split kbucket with incorrect index: " + str(oldIndex))
            return
        oldBucket = self._kbuckets[oldIndex]
        lastPart = self._kbuckets[oldIndex+1:]

        # Minimum range is always 0. There fore the "cut range" will be
        # 2**(log2(maxRange)/2)      
        cutRange = oldBucket.maxRange/2

        # Create a new k-bucket to cover the range split off from the old
        # bucket.
        newBucket = kbucket.KBucket(cutRange+1, oldBucket.maxRange)

        # Resize the range of the current (old) k-bucket.
        oldBucket.maxRange = cutRange
        
        print("Moving contacts from old bucket to new bucket")
        
        print(str(len(oldBucket._contacts)))
        contacts = oldBucket.getContacts(kademlia_constants.k)
        print("LENGTH CONTACTS == " + str(len(contacts)))

        for c in contacts:
            print("-----")
            print("Distance to nodeId: " + str(c.distance(self._nodeId)))
            print("Range from " + str(newBucket.minRange) + " to " + str(newBucket.maxRange))
            print("-->" + str(newBucket.inRange(c.distance(self._nodeId))))
            if newBucket.inRange(c.distance(self._nodeId)):
                # Finally, copy all nodes that belong to the new k-bucket into it...
                newBucket.addContact(c)
                # ...and remove them from the old bucket
                oldBucket.delContact(c)
                
        # Now, add the new bucket into the routing table.
        self._kbuckets = [oldBucket, newBucket] + lastPart;        



    def _kbucketIndex(self, contactId):
        """Find the index of the kbucket in which range the contactId lies.
        """
        
        i = 0
        for kB in self._kbuckets:
            if (kB.inRange(contactId)):
                return i
            i = i+1
        
        # Check each kbucket to see of the contactId is in range of that
        # bucket. return the index of bucket that contains this contactId.
