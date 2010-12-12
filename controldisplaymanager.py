#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html
from basecontrolmanager import BaseControlManager

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlDisplayManager(BaseControlManager):
    "ControlPanel item for drawing the display items"

    meta_type = "ControlDisplayManager"
    security = ClassSecurityInfo()
    control_title = 'Display'
    drawMode = 'edit'
    startLoc = 'DisplayManager'
    cssClass = 'display'

Globals.InitializeClass(ControlDisplayManager)
