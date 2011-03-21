# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class CalculatedValue(UserObject):
    "has a calculated value based on a callable object"

    security = ClassSecurityInfo()
    meta_type = "CalculatedValue"
    callableObjectPath = ''
    
    classConfig = {}
    classConfig[''] = {'name':'Path to a callable object', 'type':'path'}

    configurable = ('callableObjectPath')

    security.declareProtected('View', 'view')
    def view(self, *args, **kw):
        "Inline draw view"
        path = self.getConfig('callableObjectPath')
        if path:
            obj = self.restrictedTraverse(path, None)
            if obj is not None:
                try:
                    return self.changeCallingContext(obj)(*args, **kw)
                except TypeError:
                    pass

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.callableObjectPath.replace('\n','\\n')

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        self.setObject('callableObjectPath',string.replace('\\n','\n'))
        
    security.declareProtected('Access contents information', 'getPath')
    def getPath(self):
        "get the path this item is currently using"
        return self.getConfig('callableObjectPath')
    
    security.declareProtected('Change CompoundDoc', 'setPath')
    def setPath(self, path):
        "set the path for this item"
        if path:
            if self.unrestrictedTraverse(path, None) is not None:
                self.setObject('callableObjectPath', path)

Globals.InitializeClass(CalculatedValue)
import register
register.registerClass(CalculatedValue)