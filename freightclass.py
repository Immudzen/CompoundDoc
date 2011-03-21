###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class FreightClass(UserObject):
    "hold the freight class for this object it contains the class and the price"

    security = ClassSecurityInfo()
    meta_type = "FreightClass"
    freightClass = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        temp.append('<p>')
        temp.append(self.freightClass)
        temp.append(self.price.edit())
        temp.append('</p>')
        return ''.join(temp)

    security.declarePrivate('editOutput')
    def editOutput(self):
        "return a structure that another object can use to render the information relevent to this document"
        return [self.freightClass, self.price.edit()]

    security.declarePrivate('instance')
    instance = (('price', ('create', 'Money')),)

Globals.InitializeClass(FreightClass)
import register
register.registerClass(FreightClass)