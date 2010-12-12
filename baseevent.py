#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class BaseEvent(Base):
    "Base for all event items abstract"

    meta_type = "BaseEvent"
    security = ClassSecurityInfo()

    security.declarePrivate('__call__')
    def __call__(self, object):
        "Process the specifics of this event on this object"
        self.processEvent(object)

Globals.InitializeClass(BaseEvent)
