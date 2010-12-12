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

class ControlLinkManager(BaseControlManager):
    "ControlPanel item for LinkManager"

    meta_type = "ControlLinkManager"
    security = ClassSecurityInfo()
    control_title = 'Links'
    drawMode = 'edit'
    startLoc = 'LinkManager'
    cssClass = 'display'

Globals.InitializeClass(ControlLinkManager)