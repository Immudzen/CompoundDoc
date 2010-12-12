#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from inputnumber import InputNumber
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import types

class InputInt(InputNumber):
    "Input text class"

    meta_type = "InputInt"
    security = ClassSecurityInfo()
    data = 0
    calculated = None

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        if self.calculated is not None:
            temp.append(str(self.calculated))
        temp.append(self.input_number('data', self.data))
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.int()

    security.declareProtected('Change CompoundDoc', 'setCalculationValue')
    def setCalculationValue(self, value):
        "set the calculation value of this object"
        if value and isinstance(value, types.FloatType):
            self.setObject('calculated', int(value))

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        try:
            self.setObject('data', int(string))
        except ValueError:
            pass

Globals.InitializeClass(InputInt)
import register
register.registerClass(InputInt)
