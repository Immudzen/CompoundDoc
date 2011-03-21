###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class FreightCompanyCreator(UserObject):
    "Provide a list of freight companys and freight classes that are FreightCompanyContainer can subscribe to to create what it needs"

    security = ClassSecurityInfo()
    meta_type = "FreightCompanyCreator"

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        temp.append('<p>Freight Companies</p>')
        temp.append(self.freightCompanies.edit())
        temp.append('<p>Freight Classes</p>')
        temp.append(self.freightClasses.edit())
        return ''.join(temp)

    security.declarePrivate('instance')
    instance = (('freightCompanies', ('create', 'ListText')),('freightClasses',('create', 'ListText')))

    security.declarePrivate('getFreightCompanies')
    def getFreightCompanies(self):
        "return the freight companies that we have"
        return self.freightCompanies.getAvailableListsContents()

    security.declarePrivate('getFreightClasses')
    def getFreightClasses(self):
        "return the freight classes that we have"
        return self.freightClasses.getAvailableListsContents()


Globals.InitializeClass(FreightCompanyCreator)
import register
register.registerClass(FreightCompanyCreator)