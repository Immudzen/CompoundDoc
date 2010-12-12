#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlLog(ControlBase):
    "Input text class"

    meta_type = "ControlLog"
    security = ClassSecurityInfo()
    control_title = 'Log'

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class which is to delete it"
        self.ControlPanel.delObjects([self.getId()])

Globals.InitializeClass(ControlLog)
