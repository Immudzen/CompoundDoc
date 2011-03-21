###########################################################################
#    Copyright (C) 2007 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class ScriptTitleEmbed(UserObject):
    "Embed the title from a python script object"

    security = ClassSecurityInfo()
    meta_type = "ScriptTitleEmbed"

    security.declareProtected('View management screens', 'edit')
    def edit(self, script=None, *args, **kw):
        "Inline edit short object"
        if script is not None and script.meta_type =='Script (Python)':
            path = '/'.join(script.getPhysicalPath())
            return self.input_text('title', script.title, containers=['embedded',path])
        else:
            return 'This object only works on Script (Python)'

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        if 'embedded' in form:
            for path, value in form['embedded'].iteritems():
                script = self.restrictedTraverse(path, None)
                if script is not None:
                    script.ZPythonScript_setTitle(value['title'])

Globals.InitializeClass(ScriptTitleEmbed)
import register
register.registerClass(ScriptTitleEmbed)