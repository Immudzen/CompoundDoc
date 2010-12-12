###########################################################################
#    Copyright (C) 2005 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from basecontrolmanager import BaseControlManager

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlMethodManager(BaseControlManager):
    "ControlPanel item for drawing the display items"

    meta_type = "ControlMethodManager"
    security = ClassSecurityInfo()
    control_title = 'Method'
    drawMode = 'edit'
    startLoc = 'MethodManager'
    cssClass = 'display'

Globals.InitializeClass(ControlMethodManager)