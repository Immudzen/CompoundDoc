#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from base import Base
import utility

class Entry(Base):
    "This is the entry class"

    security = ClassSecurityInfo()
    meta_type = 'Entry'
    configureable = 0

    security.declarePrivate('__init__')
    def __init__(self, id, dict=None):
        self.id = id
        self.name = ""
        self.value = ""
        if dict:
            for i,j in dict.items():
                self.setObject(i,j)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.cleanupData()
        self.cleanupId()
        self.upgraderEntryType()
        self.cleanupType()
        self.cleanupValues()

    security.declarePrivate('upgraderEntryType')
    def upgraderEntryType(self):
        "upgrade config objects to use the optional type system"
        try:
            config = self.aq_parent.aq_parent.classConfig
        except AttributeError:
            return None
        id = self.getId()
        if id in config and 'type' in config[id] and getattr(self,'type',None) != config[id]['type']:
            self.setObject('type', config[id]['type'])
    upgraderEntryType = utility.upgradeLimit(upgraderEntryType, 141)

    security.declarePrivate('cleanupData')
    def cleanupData(self):
        "clean up the data attribute"
        if 'data' in self.__dict__:
            if hasattr(self.data, 'items'):
                for key,object in self.data.items():
                    self.setObject(key, object)
            del self.data
    cleanupData = utility.upgradeLimit(cleanupData, 141)
            
    security.declarePrivate('cleanupId')
    def cleanupId(self):
        "clean up the id of this object"
        if 'name' in self.__dict__:
            if self.name == 'id':
                self.name == 'showId'
        if not self.getId():
            self.id = self.name
        if self.getId() == 'id':
            self.id = 'showId'
    cleanupId = utility.upgradeLimit(cleanupId, 141)
            
    security.declarePrivate('cleanupType')
    def cleanupType(self):
        "set type to None if we have it and it has no info"
        if 'type' in self.__dict__ and self.type is None:
            self.delObjects(['type'])
    cleanupType = utility.upgradeLimit(cleanupType, 141)
            
    security.declarePrivate('cleanupValues')
    def cleanupValues(self):
        "set the values to None if we have it and it has no info"
        if 'values' in self.__dict__ and not self.values:
            self.delObjects(['values'])    
    cleanupValues = utility.upgradeLimit(cleanupValues, 141)
        
Globals.InitializeClass(Entry)
