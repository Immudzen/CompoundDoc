#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlRequest(ControlBase):
    "Input text class"

    meta_type = "ControlRequest"
    security = ClassSecurityInfo()
    control_title = 'REQUEST'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return '<div class="">%s</div>' % self.REQUEST

Globals.InitializeClass(ControlRequest)
