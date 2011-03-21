#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ObjectAdd(Base):
    "ObjectAdd class this calls allows adding objects of a specific type from the edit interface"

    meta_type = "ObjectAdd"
    security = ClassSecurityInfo()

    typeToAdd = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        if self.typeToAdd:
            return self.getCompoundDoc().addObjectsEdit([self.typeToAdd])
        return ''

    security.declarePrivate('configAddition')
    def configAddition(self):
        "create an addition that allows setting the type of objects to add and the text before we add"
        return self.option_select(self.getCompoundDoc().restrictedUserObject(), 'typeToAdd', [self.typeToAdd])

Globals.InitializeClass(ObjectAdd)
import register
register.registerClass(ObjectAdd)