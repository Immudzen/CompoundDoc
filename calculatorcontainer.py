###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CalculatorContainer(Base):
    "This object holds calculator objects and serves and a place to watch for their changes"

    meta_type = "CalculatorContainer"
    security = ClassSecurityInfo()
    overwrite=1
    objectOrder = None

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        return ['Calculator']

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append('<div>')
        temp.append(self.addDeleteObjectsEdit())
        temp.append('</div>')
        if self.objectOrder is not None:
            for id in self.objectOrder:
                object = getattr(self, id, None)
                if object is not None:
                    temp.append(object.edit())
        return ''.join(temp)

    security.declarePrivate('afterAddRegisteredObject')
    def afterAddRegisteredObject(self, id, type):
        "do something after a registered object has been added"
        if self.objectOrder is None or id not in self.objectOrder:
            if self.objectOrder is None:
                self.objectOrder = []
            self.objectOrder.append(id)
            self._p_changed=1

    security.declarePrivate('afterDeleteRegisteredObject')
    def afterDeleteRegisteredObject(self, name):
        "do something after a registered object is deleted"
        if self.objectOrder is not None and name in self.objectOrder:
            self.objectOrder.remove(name)
            if not len(self.objectOrder):
                self.objectOrder = None
            self._p_changed=1

Globals.InitializeClass(CalculatorContainer)
import register
register.registerClass(CalculatorContainer)
