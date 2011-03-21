# -*- coding: utf-8 -*-
import basemanager

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from selection import Selection

import utility

class CatalogManager(Selection, basemanager.BaseManager):
    "CatalogManager manages all displays"

    meta_type = "CatalogManager"
    security = ClassSecurityInfo()
    overwrite=1
    multipleSelect = 1
    rowsVisible = 10
    allowClear = 1
    UserObject = 0
    catalogScriptPath = ""
    
    classConfig = {}
    classConfig['catalogScriptPath'] = {'name':'Path to Catalog Script', 'type':'path'}

    security.declarePrivate('getChoices')
    def getChoices(self):
        'get the available choices to select from'
        for i in self.superValues('ZCatalog'):
            name = i.getId()
            if name != 'CDocUpgrader':
                yield name
    
    security.declarePrivate('event_data')
    def event_data(self, data):
        "unindex this object if the data is different then what we already have"
        if self.data != data:
            self.unindex_object()
    
    security.declarePrivate('getSelectedItems')
    def getSelectedItems(self):
        "get the currently selected items"
        return self

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.updateCatalogConfig()

    security.declarePrivate('getCatalogs')
    def getCatalogs(self, doc):
        "get the catalog objects"
        if self.catalogScriptPath:
            return self.getCatalogsScript(doc)
        cdoc = self.getCompoundDoc()
        
        catalogs = (getattr(cdoc, name, None) for name in self if name)
        return [catalog for catalog in catalogs if catalog is not None]

    security.declarePrivate('getCatalogsScript')
    def getCatalogsScript(self, doc):
        "get the catalogs from the script"
        path = self.catalogScriptPath
        if path:
            script = self.getCompoundDocContainer().restrictedTraverse(path, None)
            if script is not None:
                return script(doc)
        return []

    security.declarePrivate('updateCatalogConfig')
    def updateCatalogConfig(self):
        "take the info we need from CatalogConfig objects and then remove them"
        for item in self.objectValues('CatalogConfig'):
            name = item.useCatalog
            if name and name not in self:
                self.append(name)
        self.delObjects(self.objectIds('CatalogConfig'))     
    updateCatalogConfig = utility.upgradeLimit(updateCatalogConfig, 141)
                          
Globals.InitializeClass(CatalogManager)
import register
register.registerClass(CatalogManager)