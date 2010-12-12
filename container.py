#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class Container(UserObject):
    "Container class DELETED"

    """Lets be honest this class sucks and it has no useful purpose anymore the ObjectAdd and ObjectDel objects
    do a vastly superior job for this items most useful case. ContainerCompoundController is so much more advanced
    then this thing as a container that it is sad. This thing is just being put out of its misery so nobody uses it
    anymore this is just a stub class to remain so that the objects created that have this object will load long enough
    to have this object deleted from them which will have no real adverse affect on such objects which are very very few
    to begin with."""

    meta_type = "Container"
    security = ClassSecurityInfo()

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class which is to delete it"
        self.getCompoundDoc().delObjects([self.getId()])



Globals.InitializeClass(Container)
