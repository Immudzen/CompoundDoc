import baseobject
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CatalogConfig(baseobject.BaseObject):
    "CatalogConfig tracks how this objects work with different Catalogs"
    """This object is now obsolete and when the CatalogManager is updated it will take the data
    it needs and then delete the CatalogConfig objects it has"""

    meta_type = "CatalogConfig"
    security = ClassSecurityInfo()
    overwrite=1
    useCatalog = ''
                
Globals.InitializeClass(CatalogConfig)
import register
register.registerClass(CatalogConfig)