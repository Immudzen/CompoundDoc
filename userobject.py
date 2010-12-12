#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class UserObject(Base):
    "Base for all User Objects"

    meta_type = "UserObject"
    security = ClassSecurityInfo()
    UserObject = 1 #Used to determine if items should be observable/observing/keep a userModificationTime

Globals.InitializeClass(UserObject)
