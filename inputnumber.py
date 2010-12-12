###########################################################################
#    Copyright (C) 2008 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class InputNumber(UserObject):
    "Input number class for items common to float and int"

    meta_type = "InputNumber"
    security = ClassSecurityInfo()

    security.declareProtected("Access contents information", "float")
    def float(self):
        "Return the floating point of this number"
        if self.data:
            return float(self.data)
        elif self.calculated is not None:
            return float(self.calculated)
        else:
            return 0.0

    security.declareProtected("Access contents information", "int")
    def int(self):
        "Return the floating point of this number"
        if self.data:
            return int(self.data)
        elif self.calculated is not None:
            return int(self.calculated)
        else:
            return 0

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.data

    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, value):
        "set the calculation value of this object"
        self.populatorLoader(value)

Globals.InitializeClass(InputNumber)
