#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class WatchDog(UserObject):
    """WatchDog class This class is designed to monitor other objects and
    keep information about who changed it and when etc."""

    security = ClassSecurityInfo()
    meta_type = "WatchDog"

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class which is to delete it"
        self.getCompoundDoc().delObjects([self.getId()])

Globals.InitializeClass(WatchDog)
import register
register.registerClass(WatchDog)