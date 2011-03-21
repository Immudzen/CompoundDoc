###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class Calculator(UserObject):
    "Calculator class basic ops are defined for an object to be used elsewhere"

    security = ClassSecurityInfo()
    meta_type = "Calculator"
    operator = ''
    ammount = 0.00
    objectPath = ''

    operatorMapping = {'Add/Subtract Percent':'percentAddSubtract',
                'Add/Subtract Ammount':'ammountAddSubtract',
                'Multiply by Ammount':'ammountMultiply'}

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div>']
        temp.append('ID: %s Path:' % self.getId())
        temp.append(self.input_text('objectPath', self.objectPath))
        temp.append(self.option_select(self.operatorList(), 'operator', [self.operator]))
        temp.append('Ammount:')
        temp.append(self.input_float('ammount', self.ammount))
        temp.append('</div>')
        return ''.join(temp)

    security.declarePrivate('calculate')
    def calculate(self, remote):
        "calculate this object"
        if self.operator and self.ammount and self.objectPath:
            return getattr(self, self.operatorMapping[self.operator])(remote)
        return 0.00

    security.declarePrivate('operatorList')
    def operatorList(self):
        "return the list of operators sorted"
        return sorted(self.operatorMapping.keys())

    security.declarePrivate('percentAddSubtract')
    def percentAddSubtract(self, remote):
        "add/subtract a percent to the object and return it"
        return self.getTraversedObjectValue(remote)*(self.ammount+100.0)/100.0

    security.declarePrivate('ammountAddSubtract')
    def ammountAddSubtract(self, remote):
        "add/subtract an absolute ammount to this item"
        return self.getTraversedObjectValue(remote) + self.ammount

    security.declarePrivate('ammountMultiply')
    def ammountMultiply(self, remote):
        "multiply the item by this ammount"
        return self.getTraversedObjectValue(remote) * self.ammount

    security.declarePrivate('getTraversedObjectValue')
    def getTraversedObjectValue(self, remote):
        "return the floating point value of the returned object"
        object = self.getTraversedObject(remote)
        if object is None:
            return 0.0
        if object.hasObject('float'):
            return object.float()
        elif callable(object):
            return float(object())
        else:
            return float(object)

    security.declarePrivate('getTraversedObject')
    def getTraversedObject(self, remote):
        "get the remote object and return it"
        if not self.objectPath:
            return None
        object = remote.restrictedTraverse(self.objectPath)
        if object is not None:
            return object

Globals.InitializeClass(Calculator)
import register
register.registerClass(Calculator)