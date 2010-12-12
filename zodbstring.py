###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import Persistence

class ZODBString(Persistence.Persistent):
    "wrapper for a string to many object can point to it as it changed"

    meta_type = "ZODBString"
    security = ClassSecurityInfo()

    def __init__(self, string=''):
        self.data = string

    def set(self, string):
        if self.data != string:
            self.data = string

    def __str__(self):
        return self.data

Globals.InitializeClass(ZODBString)
