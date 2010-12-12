#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import types

class Money(UserObject):
    "Money class"

    meta_type = "Money"
    security = ClassSecurityInfo()
    data = 0.0
    calculated = None

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        if self.calculated is not None:
            temp.append('%.2f' % self.calculated)
        temp.append(self.input_float('data', '%.2f' % self.data))
        return ''.join(temp)

    security.declareProtected("Access contents information", "float")
    def float(self):
        "Return the floating point of this number"
        if self.data:
            return float('%.2f' % self.data)
        elif self.calculated is not None:
            return float('%.2f' % self.calculated)
        else:
            return 0.00

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        if self.data:
            return '%.2f' % self.data
        elif self.calculated is not None:
            return '%.2f' % self.calculated
        else:
            return "0.00"

    security.declareProtected('Change CompoundDoc', 'setCalculationValue')
    def setCalculationValue(self, value):
        "set the calculation value of this object"
        if value and isinstance(value, types.FloatType):
            self.setObject('calculated', value)

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return '%.2f' % self.data

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        try:
            self.setObject('data', float(string))
        except ValueError:
            pass

    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, value):
        "set the calculation value of this object"
        self.populatorLoader(value)

Globals.InitializeClass(Money)
import register
register.registerClass(Money)
