#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from baseevent import BaseEvent

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class EventBlankDTML(BaseEvent):
    "Run a dtml command on a blank item when this event is called"

    meta_type = "EventBlankDTML"
    security = ClassSecurityInfo()

    dtmlstring = ''
    allowedIds = None

    security.declarePrivate('processEvent')
    def processEvent(self, object):
        "check if this objects main piece of data is blank and if so set it to the value of the dtml"
        string = object.data
        if string == '':
            if self.allowedIds is not None and self.getId() not in self.allowedIds:
                return None
            object.setObject('data',self.outputDTML())

    security.declarePrivate('outputDTML')
    def outputDTML(self):
        "Return the rendered DTML for this object"
        return self.gen_html(self.getDTMLString())

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "process the edits"
        allowedIds = dict.pop('allowedIds', None)
        if allowedIds is not None:
            formAllowedIds = allowedIds.split()
            if not len(formAllowedIds):
                formAllowedIds = None
            self.setObject('allowedIds',formAllowedIds)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        return '<p>DTML string to run: %s </p><p>Allowed Object Ids: %s </p>' % (
          self.input_text('dtmlstring', self.getDTMLString()),
          self.input_text('allowedIds', ' '.join(self.getAllowedIds())))

    security.declarePrivate('getAllowedIds')
    def getAllowedIds(self):
        "Return all the allowed object ids"
        if self.allowedIds is not None:
            return self.allowedIds
        return []

    security.declarePrivate('getDTMLString')
    def getDTMLString(self):
        "return the dtml string that can be run"
        return getattr(self, 'dtmlstring')

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

Globals.InitializeClass(EventBlankDTML)
import register
register.registerClass(EventBlankDTML)