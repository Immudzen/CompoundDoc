###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from Acquisition import aq_base

class ControlShared(ControlBase):
    "Show the status of which items are shared"

    meta_type = "ControlShared"
    security = ClassSecurityInfo()
    control_title = 'Shared'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div class="">']
        temp.append(self.checkMasterLocation())
        temp.append('</div>')
        return ''.join(temp)

    security.declarePrivate('checkMasterLocation')
    def checkMasterLocation(self):
        "check if this item is sharing with its master profile if it has one"
        temp = []
        cdoc = self.getCompoundDoc()
        if cdoc.masterLocation is not None:
            if cdoc.masterLocation != cdoc.getPath():
                master = self.unrestrictedTraverse(cdoc.masterLocation, None)
                if master is not None and master.meta_type == 'CompoundDoc':
                    if cdoc.DisplayManager is None:
                        temp.append("<p>I don't have a DisplayManager</p>")
                    else:
                        if aq_base(cdoc.DisplayManager) is aq_base(master.DisplayManager):
                            temp.append('<p>I am sharing DisplayManager</p>')
                        else:
                            temp.append('<p>I am not sharing DisplayManager</p>')
            else:
                temp.append('<p>Sharing is enabled and I am the master document</p>')
        return ''.join(temp)

Globals.InitializeClass(ControlShared)
