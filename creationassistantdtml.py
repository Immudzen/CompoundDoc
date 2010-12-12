#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from creationassistantstring import CreationAssistantString

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CreationAssistantDTML(CreationAssistantString):
    "CreationAssistantDTML class can set string attributes of an object to a dtml rendered value after creation"

    meta_type = "CreationAssistantDTML"
    security = ClassSecurityInfo()

    security.declarePrivate('setupObject')
    def setupObject(self, object):
        "if this object is the kind we are looking for create the other items we need in it"
        if self.idValueMapping is not None and object.meta_type == self.metaType:
            for id, value in self.idValueMapping.items():
                object.updateObject(id, self.gen_html(value)) 

Globals.InitializeClass(CreationAssistantDTML)
import register
register.registerClass(CreationAssistantDTML)