#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from inputnumber import InputNumber
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import types

class InputFloat(InputNumber):
    "Input float class"

    meta_type = "InputFloat"
    security = ClassSecurityInfo()
    data = 0.0
    calculated = None

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        if self.calculated is not None:
            temp.append(str(self.calculated))
        temp.append(self.input_float('data', self.data))
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.float()

    security.declareProtected('Change CompoundDoc', 'setCalculationValue')
    def setCalculationValue(self, value):
        "set the calculation value of this object"
        if value and isinstance(value, types.FloatType):
            self.setObject('calculated', value)

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        try:
            self.setObject('data', float(string))
        except ValueError:
            pass

Globals.InitializeClass(InputFloat)
import register
register.registerClass(InputFloat)
