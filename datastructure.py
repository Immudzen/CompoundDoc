###########################################################################
#    Copyright (C) 2004 by kosh
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

class DataStructure(UserObject):
    """This object is used to hold a python data structure.
    The primary intent is so that structures can be calculated and stored.
    It is designed to only be used from python (script,external method, product) and not
    dtml/zpt etc."""

    security = ClassSecurityInfo()
    meta_type = "DataStructure"
    data = None

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return str(self.data)

    edit = view

    security.declarePrivate('createDataLoader')
    def createDataLoader(self):
        "return the data needed to rebuild this object as a dictionary that it can then take back to restore its information"
        return {'data': self.data}

    security.declarePrivate('dataLoader')
    def dataLoader(self, dict):
        "load the data from this dict into this object"
        if 'data' in dict:
            self.setObject('data', dict['data'])

    security.declareProtected('Python Record Addition', 'setDataStructure')
    def setDataStructure(self, data):
        "set a data structure in this object"
        self.setObject('data', data)
        
    security.declareProtected('Change CompoundDoc', 'store')        
    store = setDataStructure

    security.declareProtected('Python Record Addition', 'getDataStructure')
    def getDataStructure(self):
        "set a data structure in this object"
        return self.data


Globals.InitializeClass(DataStructure)
import register
register.registerClass(DataStructure)