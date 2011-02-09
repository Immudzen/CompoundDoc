#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import os.path

class ControlLicense(ControlBase):
    "Input text class"

    meta_type = "ControlLicense"
    security = ClassSecurityInfo()
    control_title = 'License'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        path = os.path.join(os.path.dirname(__file__), 'LICENSE')
        try:
            temp = open(path, 'r').read()
        except IOError:
            temp = "The GPL LICENSE file could not be opened for some reason."
        return '<div class=""><pre>%s</pre></div>' % temp

Globals.InitializeClass(ControlLicense)
