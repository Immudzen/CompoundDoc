#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlTabManager(ControlBase):
    "this class creates the control panel entry for a TabManager object"

    meta_type = "ControlTabManager"
    security = ClassSecurityInfo()
    control_title = 'Tab'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div class="">']
        tabManager = self.getCompoundDoc().TabManager
        if tabManager is not None:
            temp.append(self.submitChanges())
            temp.append(tabManager.edit())
        else:
            temp.append(self.create_button('addTabManager', 'Create TabManager'))
        temp.append('</div>')
        return ''.join(temp)
        
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        addTabManager = form.pop('addTabManager', None)
        if addTabManager is not None:
            self.getCompoundDoc().addRegisteredObject('TabManager', 'TabManager')

Globals.InitializeClass(ControlTabManager)
