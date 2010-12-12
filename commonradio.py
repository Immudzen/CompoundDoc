###########################################################################
#    Copyright (C) 2008 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CommonRadio(UserObject):
    "CommonRadio class"

    security = ClassSecurityInfo()
    meta_type = "CommonRadio"

    data = 0
    
    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return self.data

    security.declareProtected("Access contents information", "checked")
    def checked(self):
        "return 1/0 based on the item being checked or not"
        return self.data

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ""

    security.declareProtected('Change CompoundDoc','setYes')
    def setYes(self):
        "set the radio to true"
        self.setObject('data', 1)
    
    security.declareProtected('Change CompoundDoc','setNo')
    def setNo(self):
        "set the radio to true"
        self.setObject('data', 0)
        
    security.declareProtected('Change CompoundDoc','clear')
    clear = setNo

Globals.InitializeClass(CommonRadio)
