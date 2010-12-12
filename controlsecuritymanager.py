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

class ControlSecurityManager(BaseControlManager):
    "Input text class"

    meta_type = "ControlSecurityManager"
    security = ClassSecurityInfo()
    control_title = 'Security'
    drawMode = 'view'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        """This draws the inline forms for the objects present."""
        origin = self.getOrigin()
        object = origin.unrestrictedTraverse(self.getFixedUpPath(), None)
        format = '<div class="%(cssClass)s"><a href="%(url)s/manage_access">%(name)s</a></div>'
        if object is not None:
            lookup = {'cssClass':self.cssClass, 'url': object.absolute_url_path() ,
                'name': object.getId()}
            return format % lookup
        return ""

Globals.InitializeClass(ControlSecurityManager)