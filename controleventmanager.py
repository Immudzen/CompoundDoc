#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlEventManager(ControlBase):
    "ControlEventManager wrapper for the control panel for an event manager object"

    meta_type = "ControlEventManager"
    security = ClassSecurityInfo()
    control_title = 'Event'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        eventmanager = self.getCompoundDoc().EventManager
        temp = ['<div class="">']
        if eventmanager is not None:
            temp.append(eventmanager.addDeleteObjectsEdit())
            temp.append(self.submitChanges())
            temp.append(eventmanager.edit())
            temp.append(self.submitChanges())
        else:
            temp.append(self.create_button('addEventManager', 'Create EventManager'))
        temp.append('</div>')
        return ''.join(temp)
        
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        addEventManager = form.pop('addEventManager', None)
        if addEventManager is not None:
            self.getCompoundDoc().addRegisteredObject('EventManager', 'EventManager')

Globals.InitializeClass(ControlEventManager)
