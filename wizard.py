###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class Wizard(base.Base):
    "Basic Wizard object it provides a continuation between displays"

    meta_type = "Wizard"
    security = ClassSecurityInfo()
    overwrite=1
    annonymousEditAccepted = 0
    order = None
    script = ''

    classConfig = {}
    classConfig['script'] = {'name':'Path to Script', 'type':'string'}

    security.declareProtected('View', 'getFormLocation')
    def getFormLocation(self):
        "give the url to the next location this item needs to submit to"
        displayId = self.getDisplayName()
        if self.script:
            script = self.getCompoundDoc().restrictedTraverse(self.script,None)
            if script is not None:
                return script(displayId)
        return ''

    security.declarePrivate('getDisplayName')
    def getDisplayName(self):
        "Get the name of the current display we are using that is in charge"
        displayFilter = self.REQUEST.other.get('DisplayFilter', None)
        if displayFilter is not None:
            return displayFilter.aq_parent.getId()

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        return self.editSingleConfig('script')

Globals.InitializeClass(Wizard)
import register
register.registerClass(Wizard)