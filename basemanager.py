#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class BaseManager(base.Base):
    "Base for all manager items abstract"

    meta_type = "BaseManager"
    security = ClassSecurityInfo()

Globals.InitializeClass(BaseManager)
