#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from baseobject import BaseObject
from Acquisition import aq_base
import utility

class MixUpgrader(BaseObject):
    "this is a mixin class to give objects a auto upgrade capability"

    meta_type = "MixUpgrader"
    security = ClassSecurityInfo()

    security.declarePrivate('upgrader')
    def upgrader(self):
        "performUpgrades to the objet"
        self.fixObjectIdAndName()
        self.fixConfigId()
        self.removeAttributeConfig()
        self.fixupCacheSystem()
        self.removeObjectAndStateAttributes()
        self.upgraderRepairAttributes()
        self.createMetaMapping()
        self.upgraderRemoveParentMCP()
        self.fixupObserverSystem()
        self.removeDataAttribute()
        self.upgradeObjectConfigOrRemoveIt()
        self.undoMasterSharing()
        self.doClassSpecificUpgrades()
        self.resetCreateConfigDefault()
        self.removeItemsSpecificToCompoundDoc()
        self.resetTextAreaCaches()
        self.updateFilePictureMetaInformation()
        self.removeEditCache()
        self.removeNestedListURLObjects()
        self.removeManageEditFormInstances()
        self.removeItemsThatAreDefault()
        self.mergeObjectConfigIntoObject()
        self.removeOwnerFromAttributes()

    security.declarePrivate('removeItemsThatAreDefault')
    def removeItemsThatAreDefault(self):
        "remove the items in this object that are the same as the class default items"
        for name, value in self.__dict__.items():
            if hasattr(self.__class__, name) and getattr(self.__class__, name) == value:
                delattr(self, name)
    removeItemsThatAreDefault = utility.upgradeLimit(removeItemsThatAreDefault, 141)                
                
    security.declarePrivate('mergeObjectConfigIntoObject')
    def mergeObjectConfigIntoObject(self):
        "remove objectConfig and merge its information into its parents object"
        if 'objectConfig' in self.__dict__:
            for name, value in self.objectConfig.items():
                if name in self.classConfig:
                    self.setObject(name, value)
            self.delObjects(['objectConfig'])
    mergeObjectConfigIntoObject = utility.upgradeLimit(mergeObjectConfigIntoObject, 141) 
            
    security.declarePrivate('removeManageEditFormInstances')
    def removeManageEditFormInstances(self):
        "remove the mamange edit form objects from stuff that is not a CompoundDoc object"
        if self.meta_type != 'CompoundDoc':
            self.delObjects(self.objectIds('ManageEditForm'))
    removeManageEditFormInstances = utility.upgradeLimit(removeManageEditFormInstances, 141) 
    
    security.declarePrivate('fixObjectIdAndName')
    def fixObjectIdAndName(self):
        "fix the id and __name__ attributes of an object"
        sdict = self.__dict__
        if not 'id' in sdict and '__name__' in sdict:
            self.id = self.__name__
            del self.__name__
        if '__name__' in sdict:
            del self.__name__
    fixObjectIdAndName = utility.upgradeLimit(fixObjectIdAndName, 141)
    
    security.declarePrivate('removeAttributeConfig')
    def removeAttributeConfig(self):
        "remove the config attribute if we have one"
        if 'config' in self.__dict__:
            del self.__dict__['config']
    removeAttributeConfig = utility.upgradeLimit(removeAttributeConfig, 141)
            
    security.declarePrivate('removeNestedListURLObjects')
    def removeNestedListURLObjects(self):
        "remove the config attribute if we have one"
        self.delObjects(self.objectIds('NestedListURL'))
    removeNestedListURLObjects = utility.upgradeLimit(removeNestedListURLObjects, 141)
        
    security.declarePrivate('fixupCacheSystem')
    def fixupCacheSystem(self):
        "fixed the editCache object if it is not the right type"
        self.delObjects(['cacheNameEdit'])
    fixupCacheSystem = utility.upgradeLimit(fixupCacheSystem, 141)
    
    security.declarePrivate('fixupObserverSystem')
    def fixupObserverSystem(self):
        "fix the observer system by"
        sdict = self.__dict__
        if 'observing' in sdict and not self.observing:
            self.delObjects(['observing'])
        if 'observed' in sdict:
            self.delObjects(['observed'])
        if 'observing' in sdict:
            self.upgraderRemoveDuplicateObservingEntries()
            self.upgraderChangeObservationPath()
    fixupObserverSystem = utility.upgradeLimit(fixupObserverSystem, 141)
    
    security.declarePrivate('removeDataAttribute')
    def removeDataAttribute(self):
        "removed the data attribute from all objects that should not have it"
        if self.meta_type in ['ControlPanel',
          'ControlProfileManager', 'ControlCatalogManager', 'ControlDebugObject',
          'ControlEditManager', 'ControlEventManager', 'ControlViewManager',
          'ControlConfigManger', 'ControlAddDel', 'ControlRequest', 'ControlDisplayManager',
          'ControlLicense', 'ControlLog', 'ControlTabManager', 'Display', 'DisplayFilter',
          'DisplayManager', 'DisplayUserAgent']:
            self.delObjects(['data'])
    removeDataAttribute = utility.upgradeLimit(removeDataAttribute, 141)
    
    security.declarePrivate('doClassSpecificUpgrades')
    def doClassSpecificUpgrades(self):
        "do the upgrades specific to a class"
        if hasattr(aq_base(self), 'classUpgrader'):
            self.classUpgrader()
    
    security.declarePrivate('upgradeObjectConfigOrRemoveIt')
    def upgradeObjectConfigOrRemoveIt(self):
        "upgrade the objectConfig object where appropriate and remove it otherwise"
        if 'objectConfig' in self.__dict__ and self.meta_type not in ['Config', 'Entry']:
            if hasattr(aq_base(self), 'classConfig'):
                if hasattr(aq_base(self.objectConfig), 'classUpgrader'):
                    self.objectConfig.classUpgrader()
            else:
                self.delObjects(['objectConfig'])
    upgradeObjectConfigOrRemoveIt = utility.upgradeLimit(upgradeObjectConfigOrRemoveIt, 141)
    
    security.declarePrivate('undoMasterSharing')
    def undoMasterSharing(self):
        "copy the remove shared objects locally since we are not a master document"
        if self.meta_type == 'CompoundDoc':
            if self.masterLocation is not None:
                if self.masterLocation != self.getPath():
                    master = self.unrestrictedTraverse(self.masterLocation, None)
                    if master is not None and master.meta_type == 'CompoundDoc':
                        self.setObject('CatalogManager', aq_base(master.CatalogManager)._getCopy(master))
                        self.setObject('TabManager', aq_base(master.TabManager)._getCopy(master))
                        self.setObject('EventManager', aq_base(master.EventManager)._getCopy(master))
    undoMasterSharing = utility.upgradeLimit(undoMasterSharing, 141)
    
    security.declarePrivate('resetCreateConfigDefault')
    def resetCreateConfigDefault(self):
        "reset the var called createConfigDefault if it is not correct or should not exist"
        if 'createConfigDefault' in self.__dict__:
            self.delObjects(['createConfigDefault'])
    resetCreateConfigDefault = utility.upgradeLimit(resetCreateConfigDefault, 141)
    
    security.declarePrivate('removeItemsSpecificToCompoundDoc')
    def removeItemsSpecificToCompoundDoc(self):
        "remove items from various objects that only compounddoc objects should have"
        sdict = self.__dict__
        if self.meta_type != 'CompoundDoc':
            if self.objectIds('ManageEditForm'):
                self.upgraderRemoveManage()
            if 'objectVersion' in sdict:
                self.delObjects(['objectVersion'])
            if 'updateVersion' in sdict:
                self.delObjects(['updateVersion'])
            if 'userModificationTimeStamp' in sdict:
                self.delObjects(['userModificationTimeStamp'])
    removeItemsSpecificToCompoundDoc = utility.upgradeLimit(removeItemsSpecificToCompoundDoc, 141)
    
    security.declarePrivate('resetTextAreaCaches')
    def resetTextAreaCaches(self):
        "reset the caches of text areas"
        sdict = self.__dict__
        if self.meta_type in ['TextArea', 'SectionText']:
            if 'cachedSTX' in sdict:
                self.delObjects(['cachedSTX'])
            if not 'renderCache' in sdict:
                self.updateCache()
    resetTextAreaCaches = utility.upgradeLimit(resetTextAreaCaches, 141)
    
    security.declarePrivate('updateFilePictureMetaInformation')
    def updateFilePictureMetaInformation(self):
        "update the meta information attached to files and pictures"
        if self.meta_type in ['File', 'Picture']:
            self.setFileSize()
            self.updateFileContentType()
    updateFilePictureMetaInformation = utility.upgradeLimit(updateFilePictureMetaInformation, 141)
   
    security.declarePrivate('removeEditCache')
    def removeEditCache(self):
        "if we have a var called editCache remove it"
        self.delObjects(['editCache'])
    removeEditCache = utility.upgradeLimit(removeEditCache, 141)
    
    security.declarePrivate('fixConfigId')
    def fixConfigId(self):
        "Fix the id of the config object since a bug at one point allowed an entry to be called id"
        config = getattr(self, 'objectConfig', None)
        if config is not None and config == 'Config':
            if not 'id' in self.__dict__:
                config.id = 'objectConfig'
            if hasattr(config.id, 'meta_type') and config.id.meta_type == 'Entry':
                config.setObject('showId', aq_base(config.id))
                config.delObjects(['id'])
                config.id = 'objectConfig'
    fixConfigId = utility.upgradeLimit(fixConfigId, 141)
    
    security.declarePrivate('removeObjectAndStateAttributes')
    def removeObjectAndStateAttributes(self):
        "remove the object and state attributes"
        try:
            del self.object
        except (AttributeError, KeyError):
            pass

        try:
            del self.state
        except (AttributeError,KeyError):
            pass
    removeObjectAndStateAttributes = utility.upgradeLimit(removeObjectAndStateAttributes, 141)
    
    security.declarePrivate('createMetaMapping')
    def createMetaMapping(self):
        "Create a meta_type mapping for each object that has one to speed up lookups by type"
        #Items should be fixing their entires automatically and cleanup should not happen here
        #It screws up the ObjectRecords since they have entries that are in a subobject that
        #uses a getattr to catch those requests and this would remove those entries.
        temp = []
        for name, item in self.__dict__.items():
            if getattr(item, 'meta_type', None):
                temp.append({'id':name, 'meta_type':item.meta_type})
        if self.meta_type == 'ObjectRecorder':
            meta = self.recordType
            if meta is not None:
                for key in self.getRecordKeys():
                    temp.append({'id':key, 'meta_type':meta})

        temp = tuple(sorted(temp))
        if self._objects != temp:
            self.setObject('_objects', temp)
    createMetaMapping = utility.upgradeLimit(createMetaMapping, 141)
    
    security.declarePrivate('upgraderRepairAttributes')
    def upgraderRepairAttributes(self):
        "repair attributes that got created too soon and so caused the upgrader to abort"
        if self.meta_type in ['CompoundDoc', 'Config', 'Entry']:
            return None
        name = self.getId()

        trans = {}
        trans[name+'data'] = 'data'
        trans[name+'title'] = 'title'
        trans[name+'filename'] = 'filename'
        trans[name+'fileSize'] = 'fileSize'
        trans[name+'tags'] = 'tags'
        trans[name+'alt'] = 'alt'
        trans[name+'principiaSearch'] = 'principiaSearch'
        trans[name+'code'] = 'code'
        trans[name+'codetype'] = 'codetype'
        trans[name+'required'] = 'required'
        trans[name+'optional'] = 'optional'
        trans[name+'clients'] = 'clients'
        trans[name+'language'] = 'language'
        trans[name+'structured'] = 'structured'
        trans[name+'cachedSTX'] = 'cachedSTX'
        trans[name+'description'] = 'description'
        trans[name+'alias'] = 'alias'
        trans[name+'usage'] = 'usage'
        trans[name+'registeredFilters'] = 'registeredFilters'
        trans[name+'registered'] = 'registeredFilters'
        trans[name+'defaultFilter'] = 'defaultFilter'
        trans[name+'defaultEdit'] = 'defaultEdit'
        trans[name+'defaultView'] = 'defaultView'
        trans[name] = 'data'
        trans[name+'MCP'] = 'MCP'
        trans[name+'Parents'] = 'Parents'
        trans[name+'mode'] = 'mode'
        trans[name+'objectPath'] = 'objectPath'
        trans[name+'useCatalog'] = 'useCatalog'

        sdict = self.__dict__
        for oldName, newName in trans.items():
            if oldName in sdict:
                oldItem = getattr(self, oldName)
                self.delObjects([oldName])
                newItem = None
                if newName in sdict:
                    newItem = getattr(self, newName)
                if oldItem and newItem is None:
                    self.setObject(newName, oldItem)
    upgraderRepairAttributes = utility.upgradeLimit(upgraderRepairAttributes, 141)
    
    security.declarePrivate('upgraderRemoveParentMCP')
    def upgraderRemoveParentMCP(self):
        "This removes parent facing links and links to the main compounddoc"
        self.delObjects(['MCP', 'Parent'])
    upgraderRemoveParentMCP = utility.upgradeLimit(upgraderRemoveParentMCP, 141)
    
    security.declarePrivate('upgraderRemoveDuplicateObservingEntries')
    def upgraderRemoveDuplicateObservingEntries(self):
        "Remove the multiple entries that the previous observing code could get into"
        if 'observing' in self.__dict__:
            temp = list(set(self.observing))
            if self.observing != temp:
                self.observing = temp
    upgraderRemoveDuplicateObservingEntries = utility.upgradeLimit(upgraderRemoveDuplicateObservingEntries, 141)
    
    security.declarePrivate('upgraderChangeObservationPath')
    def upgraderChangeObservationPath(self):
        "Change the observation path for items in local cdocs to be locally relative"
        cdoc = self.getCompoundDoc()
        if 'observing' in self.__dict__:
            if [1 for i in self.observing if i[0] == '/']:
                temp = [cdoc.unrestrictedTraverse(i, None) for i in self.observing]
                temp = [i.getRelativePath(self) for i in temp if i is not None]
                if self.observing != temp:
                    self.observing = temp
    upgraderChangeObservationPath = utility.upgradeLimit(upgraderChangeObservationPath, 141)
    
    security.declarePrivate('upgraderRemoveManager')
    def upgraderRemoveManage(self):
        "remove the ManageEditForm object from all non compounddocs"
        self.delObjects(self.objectIds('ManageEditForm'))
    upgraderRemoveManage = utility.upgradeLimit(upgraderRemoveManage, 141)
    
    security.declarePrivate('removeOwnerFromAttribute')
    def removeOwnerFromAttributes(self):
        "remove _owner from all the non CompoundDoc attributes"
        if self.meta_type != 'CompoundDoc':
            self.delObjects(['_owner'])
    removeOwnerFromAttributes = utility.upgradeLimit(removeOwnerFromAttributes, 155)
    
Globals.InitializeClass(MixUpgrader)
