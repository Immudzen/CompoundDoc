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

class CalculatorWatcher(Base):
    "watch a calculator container for changes and apply them internally when they do"

    meta_type = "CalculatorWatcher"
    security = ClassSecurityInfo()
    overwrite=1
    calculatorPath = ''
    creationType = 'Money'

    classConfig = {}
    classConfig['creationType'] = {'name':'creationType', 'type':'list', 'values': ['Money','InputInt','InputFloat']}
    classConfig['calculatorPath'] = {'name':'Location of CalculatorContainer object:', 'type':'string'} 
    
    #TEST: See if calculator picks up changes in its config
    def after_manage_edit(self, dict):
        "Process edits."
        object = self.getRemoteObject(self.calculatorPath, 'CalculatorContainer')
        if object is not None:
            self.observerUpdate()
            object.observerAttached(self)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declarePrivate('observerUpdate')
    def observerUpdate(self, object=None):
        "Process what you were observing"
        calculatorcontainer = self.getRemoteObject(self.calculatorPath, 'CalculatorContainer')
        if calculatorcontainer is not None:
            creationType = self.creationType
            order = calculatorcontainer.objectOrder
            items = self.objectItems(['Money', 'InputFloat', 'InputInt'])
            list = [id for id, object in items if id not in order or object.meta_type != creationType]
            self.delObjects(list)
            for id in calculatorcontainer.objectOrder:
                if not self.hasObject(id):
                    self.addRegisteredObject(id, self.creationType)
            for id in calculatorcontainer.objectOrder:
                calculator = getattr(calculatorcontainer, id)
                calculated = getattr(self, id)
                calculated.setCalculationValue(calculator.calculate(self))
            paths = [i.getPhysicalPath() for i in self.objectValues(self.creationType)]
            for id in calculatorcontainer.objectOrder:
                traversedObject = getattr(calculatorcontainer, id).getTraversedObject(self)
                if traversedObject is not None and traversedObject.getPhysicalPath() not in paths:
                    traversedObject.observerAttached(self)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        format = "<p>ID: %s %s</p>"
        if self.calculatorPath:
            calculatorContainer = self.getRemoteObject(self.calculatorPath, 'CalculatorContainer')
            if calculatorContainer is not None:
                for id in calculatorContainer.objectOrder:
                    object = getattr(self, id, None)
                    if object is not None:
                        temp.append(format % (object.getId(), object.edit()))
        return ''.join(temp)

    security.declarePrivate('eventProfileLast')
    def eventProfileLast(self):
        "run this event as the last thing the object will do before the profile is returned"
        self.delObjects([id for id in self.objectIds(self.creationType)]+['observed'])
        self.observerUpdate()

Globals.InitializeClass(CalculatorWatcher)
import register
register.registerClass(CalculatorWatcher)