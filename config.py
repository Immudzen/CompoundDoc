#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

#Get Entry class
from entry import Entry
from base import Base
import types
import utility

class Config(Base):
    "This is the basic config class"

    security = ClassSecurityInfo()
    meta_type = 'Config'
    configureable = 0

    security.declarePrivate('__init__')
    def __init__(self, id, dict=None):
        "Initialize the class"
        self.id = id
        if dict is not None and hasattr(dict, 'items'):
            for i, j in dict.items():
                if isinstance(j, types.DictType):
                    self.addEntry(i, j) 

    security.declarePrivate('addEntry')
    def addEntry(self, name, dict):
        "Add an entry to this config"
        if name == 'id':
            name = 'showId'
        self.setObject(name, Entry(name, dict))

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeData()
        self.setParentObjectConfig()

    security.declarePrivate('setParentObjectConfig')
    def setParentObjectConfig(self):
        "set the parent objectConfig"
        self.aq_parent.setObject('objectConfig', self.convertToDict())
    setParentObjectConfig = utility.upgradeLimit(setParentObjectConfig, 141)
    
    security.declarePrivate('removeData')
    def removeData(self):
        "remove the data member of this object"
        if 'data' in self.__dict__:
            if hasattr(self.data, 'items'):
                for key, object in self.data.items():
                    if key == 'id':
                        key = 'showId'

                    if hasattr(object, 'meta_type') and object.meta_type == 'Entry':
                        self.setObject(key, object)
                        getattr(self, key).upgrader()
                    else:
                        self.addEntry(key, object)
            self.delObjects(['data'])
    removeData = utility.upgradeLimit(removeData, 141)
    
    security.declarePrivate('convertToDict')
    def convertToDict(self):
        "Convert this object to the new dict config format"
        temp = {}
        for name, entry in self.objectItems('Entry'):
            temp[name] = entry.value
        return temp

Globals.InitializeClass(Config)
import register
register.registerClass(Config)