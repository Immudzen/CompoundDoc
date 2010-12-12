######s#####################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from BTrees.IOBTree import IOBTree

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import Persistence

class ZODBList(Persistence.Persistent):
    "smart list structure that only saves changed data in an IOBTree"

    meta_type = "ZODBList"
    security = ClassSecurityInfo()

    def __init__(self, initlist=None):
        self.data = IOBTree()
        if initlist is not None:
            for i, element in enumerate(initlist):
                self.data.insert(i, element)

    def __contains__(self, item):
        return self.data.has_key(item)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, i, item):
        if item != self.data[i]:
            self.data[i] = item

    def __delitem__(self, i):
        del self.data[i]

    def append(self, item):
        self.data[self.data.maxKey()+1] = item

    def set(self, list):
        self.data.clear()
        for i, element in enumerate(list):
            if self.data.get(i, None) is not element:
                self.data.__setitem__(i, element)    

    def __str__(self):
        return ''.join([str(string) for string in self.data.values()])

Globals.InitializeClass(ZODBList)
