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

        # Else, add it if there is space left in the bucket.

        # If there is no space left raise a KBucketException.

    def delContact(self, contact):
        """Remove a contact from the bucket.
        """

        # Remove the contact from the kbucket.

    def getContact(self, contactId):
        """Get a contact from the bucket.

        As the contacts are stored as a flat list we must first find the index
        and then return the contact at that index.
        """

        # Return the contact belonging to a particular id. Be sure to take care
        # of exceptions.

    def getContacts(self, count):
        """Get count, but never more than K, contacts from this kbucket.

        Return all contacts if there are fewer than count.
        """

        # Ensuring the invariants (see the docstring), return count (or fewer)
        # contacts from this kbucket.

    def inRange(self, contactId):
        """Determine if the contactId is inside the range of this bucket.

        The contactId should be of type long.
        """
    
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
