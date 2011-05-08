#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import pydoc
import com.javascript
import com.css
import com.detection
import com.html
import com.form
import com.catalog
import com.parsers

class ControlComHelp(ControlBase):
    "Input text class"

    meta_type = "ControlComHelp"
    security = ClassSecurityInfo()
    control_title = 'Help'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        seq  = [com.javascript, com.css, com.detection, com.html, com.form, com.catalog, com.parsers]
        seq = [(pydoc.html.document(mod), mod.__name__) for mod in seq]
        temp = [com.javascript.document_ready([com.javascript.tabs_init('control_help')])]
        temp.append('<div class="">')
        temp.append(com.javascript.tabs_html_data('control_help', seq))
        temp.append('</div>')
        return ''.join(temp)

Globals.InitializeClass(ControlComHelp)
