###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class IssueChoice(UserObject):
    "this object represents a choice within an issue"

    security = ClassSecurityInfo()
    meta_type = "IssueChoice"
    data = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return '<p>Choice Text: %s</p>' % self.editDataStructure()

    security.declarePrivate('editDataStructure')
    def editDataStructure(self):
        "return a data structure that contains what is needed to edit this object instead of a string"
        return self.input_text('data', self.data)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.data

Globals.InitializeClass(IssueChoice)
import register
register.registerClass(IssueChoice)