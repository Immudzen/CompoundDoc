#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class MixAddRegistered:
    "this is a mixin class to give addition/removal capability of registered object types"

    meta_type = "MixAddRegistered"
    security = ClassSecurityInfo()

    security.declarePrivate('availableObjects')
    def availableObjects(self):
        "Return avaialble objects as a list"
        return sorted(self.classDict().keys())

    security.declarePrivate('deleteRegisteredObject')
    def deleteRegisteredObject(self, name, noremove):
        "Delete the object whose name is name subject to noremove"
        if name in self.__dict__ and not name in noremove:
            self.delObjects([name])
            self.afterDeleteRegisteredObject(name)

    security.declarePrivate('afterDeleteRegisteredObject')
    def afterDeleteRegisteredObject(self, name):
        "do something after a registered object is deleted"
        return None

    def createRegisteredObject(self, name, classType, **kw):
        "Create a registered object of this classType and return it but don't store it"
        item =None
        if kw:
            item = self.classDict()[classType](name, **kw)
        else:
            item = self.classDict()[classType](name)
        return item

    security.declarePrivate('addRegisteredObject')
    def addRegisteredObject(self, name, classType, **kw):
        "Add this object overwriting one we might already have"
        name = utility.cleanRegisteredId(name)
        if classType != "" and name != "" and classType in self.classDict():
            if name in self.__dict__:
                self.delObjects([name])
            item = self.createRegisteredObject(name, classType, **kw)
            self.setObject(name, item)
            self.afterAddRegisteredObject(name, classType)

    security.declarePrivate('afterAddRegisteredObject')
    def afterAddRegisteredObject(self, name, classType):
        "do something after a registered object has been added"
        return None

    security.declarePrivate('updateRegisteredObject')
    def updateRegisteredObject(self, name, classType, **kw):
        "Add this object if we don't already have one"
        name = utility.cleanRegisteredId(name)
        if classType != "" and name != "":
            if classType in self.classDict() and not name in self.__dict__:
                self.updateObject(name, self.createRegisteredObject(name, classType, **kw))
                self.afterAddRegisteredObject(name, classType)

Globals.InitializeClass(MixAddRegistered)
