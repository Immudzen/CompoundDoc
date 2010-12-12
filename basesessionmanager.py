#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class BaseSessionManager(UserObject):
    "Base for all session items"

    meta_type = "BaseSessionManager"
    security = ClassSecurityInfo()

    security.declarePrivate('getAvailableSessionManagers')
    def getAvailableSessionManagers(self):
        "Return a list of all the available session managers"
        return ['/'.join(i.getPhysicalPath()) for i in self.superValues('Session Data Manager')]

    security.declarePrivate('getDefaultSessionManager')
    def getDefaultSessionManager(self):
        "Get the first one we have worse case return a blank string"
        managers = self.getAvailableSessionManagers()
        if len(managers):
            return managers[0]
        return ""

    security.declarePrivate('delayedInstance')
    delayedInstance = (('sessionManager', ('call', 'getDefaultSessionManager')), )

    security.declarePrivate('getSessionManager')
    def getSessionManager(self):
        "get the session manager object"
        return self.unrestrictedTraverse(self.sessionManager, None)

Globals.InitializeClass(BaseSessionManager)
