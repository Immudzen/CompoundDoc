#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ObjectDelete(Base):
    "ObjectDelete class this calls allows deleting objects of a specific type from the edit interface"

    meta_type = "ObjectDelete"
    security = ClassSecurityInfo()

    typeToDelete = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        if self.typeToDelete:
            return self.getCompoundDoc().deleteObjectsEdit([self.typeToDelete])
        return ''

    security.declarePrivate('configAddition')
    def configAddition(self):
        "create an addition that allows setting the type of objects to add and the text before we add"
        return self.option_select(self.getCompoundDoc().restrictedUserObject(), 'typeToDelete', [self.typeToDelete])

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return ''

Globals.InitializeClass(ObjectDelete)
import register
register.registerClass(ObjectDelete)