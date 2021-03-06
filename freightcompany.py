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
import utility

class FreightCompany(UserObject):
    "The FreightCompany object holds freightclass objects"

    security = ClassSecurityInfo()
    meta_type = "FreightCompany"

    freightCompanyName = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        freightItems = self.objectItems('FreightClass')
        freightItems.sort()
        editFreightItems = [freightclass.editOutput() for name, freightclass in freightItems]
        format = '<p>%s</p>%s'
        return format % (self.freightCompanyName, self.createTable(editFreightItems))

    security.declarePrivate('getFreightCompanyListing')
    def getFreightCompanyListing(self):
        "return the freight company and the class listing as a dict with the value as the floating point number"
        listing = {}
        format = "%s - %s"
        for freightClass in self.objectValues('FreightClass'):
            listing[format % (self.freightCompanyName,freightClass.freightClass)] = freightClass.price.float()
        return listing

    security.declarePrivate('syncFreightClasses')
    def syncFreightClasses(self, seq=None):
        "sync the FreightClass objects that we have with what is in the list"
        if seq is not None:
            cleanNames = [utility.cleanRegisteredId(name) for name in seq]
            self.delObjects([name for name in self.objectIds('FreightClass') if name not in cleanNames])
            for clean, name in zip(cleanNames, seq):
                if clean is not None and not self.hasObject(clean):
                    self.addRegisteredObject(clean, 'FreightClass')
                    getattr(self, clean).freightClass = name

Globals.InitializeClass(FreightCompany)
import register
register.registerClass(FreightCompany)