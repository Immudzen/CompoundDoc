###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from commonradio import CommonRadio

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CheckBox(CommonRadio):
    "CheckBox class"

    security = ClassSecurityInfo()
    meta_type = "CheckBox"

    data = 0
    actionYes = ''
    actionNo = ''
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return self.radio_box('data', self.data, enableDefault=1)

Globals.InitializeClass(CheckBox)
import register
register.registerClass(CheckBox)
