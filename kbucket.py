#
# file: kbucket.py
# 
# author: Tim van Deurzen
#
###############################################################################
#
# Based on the KBucket class of entangled-0.1.
#
###############################################################################

import logging 

import kademlia_constants


class KBucket(object):
    """Represent a single KBucket in a Kademlia DHT. 
    """

    def __init__(self, minRange, maxRange):
        """Initialize a KBucket with a certain range.
        """

        self.k = kademlia_constants.k
        self.minRange = minRange
        self.maxRange = maxRange
        self._contacts = []

        self.logger = logging.getLogger('KBucket')

    def addContact(self, contact):
        """Add a contact to the bucket.

        The list of contacts is ordered as Least Recently Used. Within the
        Kademlia protocol this ensures that long-lived contacts do not get
        replaced.
        """

        # If the contact is already in the kbucket, move it to keep the correct
        # order.

        try:
            self._contacts.remove(contact)
            self._contacts.append(contact)

        # Else, add it if there is space left in the bucket.
        except Exception as e:
            print("Kbucket: unkown contact, adding " + str(contact.dht_port))
            if len(self._contacts) >= self.k:
                print("Bucket was full")
                raise KBucketException("Bucket full")
            else:
                self._contacts.append(contact)
        print("kbucket now contains: ")
        for c in self._contacts:
            print c.cid
            

        # If there is no space left raise a KBucketException.

    def delContact(self, contact):
        """Remove a contact from the bucket.
        """

        try:
            self._contacts.remove(contact)
        except Exception as e:
            pass

        # Remove the contact from the kbucket.

    def getContact(self, contactId):
        """Get a contact from the bucket.

        As the contacts are stored as a flat list we must first find the index
        and then return the contact at that index.
        """

        for i in range(0, len(self._contacts)):
            if self._contacts[i].cid == contactId:
                return self._contacts[i]
        raise KBucketException("No such contact")

        # Return the contact belonging to a particular id. Be sure to take care
        # of exceptions.

    def getContacts(self, count):
        """Get count, but never more than K, contacts from this kbucket.

        Return all contacts if there are fewer than count.
        """

        length = len(self._contacts)
        if count >= length:
            return self._contacts
        else:
            list = []
            i = 0
            while i < count:
                list.append(self._contacts[i-1])
                i += 1
            return list
                

        # Ensuring the invariants (see the docstring), return count (or fewer)
        # contacts from this kbucket.

    def inRange(self, contactId):
        """Determine if the contactId is inside the range of this bucket.

        The contactId should be of type long.
        """

        if type(contactId) == type(0L):
            if contactId >= self.minRange and contactId <= self.maxRange:
                return True
            else:
                return False
        else:
            raise KBucketException("contactId was not of type long")
        
        # noget i retning af contact.cid >= kB.minRange && contact.cid < kB.maxRange

        
        # Ensure the contact is inside the range of this bucket.

    def __len__(self):
        """Determine the size of this bucket.
        """

        return len(self._contacts)

class KBucketException(Exception):
    """An exception class to accompany the KBucket class.

    We only want a specific Exception class, no specific behaviour, hence no
    extra implementation effort.
    """
