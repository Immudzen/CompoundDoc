#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class BaseCatalog(UserObject):
    "Base for all catalog using items abstract"

    meta_type = "BaseCatalog"
    security = ClassSecurityInfo()

    security.declarePrivate('getAvailableCatalogs')
    def getAvailableCatalogs(self):
        "Return a list of all the available Catalogs"
        temp = []
        for catalog in self.superValues('ZCatalog'):
            name = catalog.getId()
            if name not in temp and name != 'CDocUpgrader':
                temp.append(name)
        return temp

    security.declarePrivate('getDefaultCatalog')
    def getDefaultCatalog(self):
        "Get the Catalog catalog if it exists otherwise return the first one we have worse case return a blank string"
        catalogs = self.getAvailableCatalogs()
        if 'Catalog' in catalogs:
            return 'Catalog'
        if len(catalogs):
            return catalogs[0]
        return ""

    security.declarePrivate('delayedInstance')
    delayedInstance = (('useCatalog', ('call', 'getDefaultCatalog')), )

Globals.InitializeClass(BaseCatalog)
