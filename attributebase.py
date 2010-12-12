# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from base import Base

class AttributeBase(Base):
    "This is the AttributeBase object and it defines basic attribute types for compounddocs"

    meta_type = "AttributeBase"
    security = ClassSecurityInfo()
    configureable = 0
    data = ''

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return self.data
    
    security.declareProtected('View', 'view')
    def view(self):
        """This is the view dispatcher. It should dispatch to the appropriate
        object view."""
        return self.gen_html(self.data)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        """This is the edit dispatcher. It should dispatch to the appropriate
        object edit view."""
        return "<p>This object(%s) has not yet implemented this feature(edit).</p>" % self.getId()

    security.declarePrivate('dtmlFree')
    def dtmlFree(self):
        "return true if this object has no dtml in it"
        return 'dtml' not in self.data

Globals.InitializeClass(AttributeBase)
