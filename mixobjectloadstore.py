# -*- coding: utf-8 -*-

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from baseobject import BaseObject
import copy
from Acquisition import aq_base
import utility

class MixObjectLoadStore(BaseObject):
    '''This is a mixin to give load and store to a file capability
    for an object. It is implemented via pickling'''

    meta_type = "MixObjectLoadStore"
    security = ClassSecurityInfo()

    security.declarePrivate('objectLoadCDoc')
    def objectLoadCDoc(self, cdoc):
        "load another compounddoc into this compounddoc and treat it as a template"
        replaceList = ['DisplayManager', 'EventManager', 'TabManager', 'CatalogManager', 'MethodManager', 'profileTypeKeep', 'objectConfig', 'masterLocation', 'displayMap', 'defaultDisplay']
        
        replaceList.extend(self.updateReplaceList)
        
        noreplace = ['manage_workspace', 'manage_main', 'manage', 'manage_edit_form', 'ControlPanel', 'submitChanges']
        objectIds = [i for i in cdoc.objectIds() if i not in noreplace]

        if hasattr(cdoc, 'masterLocation'):
            if cdoc.masterLocation != self.getPath():
                master = self.unrestrictedTraverse(cdoc.masterLocation, None)
                if master is not None and master.meta_type == 'CompoundDoc' and master.DisplayManager is not None:
                    self.setObject('DisplayManager', aq_base(master.DisplayManager))
            replaceList.remove('DisplayManager')
            noreplace.append('DisplayManager')
        #do replacemants
        for i in replaceList:
            if i in cdoc.__dict__:
                temp = aq_base(getattr(cdoc, i))
                self.delObjects([i])
                self.setObject(i, temp)
                if i in objectIds:
                    objectIds.remove(i)
            else: #if the item is a replacement item and that item is not in the profile doc remove that attribute
                self.delObjects([i])
                if i in objectIds:
                    objectIds.remove(i)
        
        #add items that we don't have
        for i in copy.copy(objectIds):
            if not i in self.__dict__:
                self.delObjects([i])
                self.setObject(i, aq_base(getattr(cdoc, i)))
                objectIds.remove(i)

        #replace other items that we do have
        for i in copy.copy(objectIds):
            if i in self.__dict__:
                temp = aq_base(getattr(cdoc, i))
                local = getattr(self, i)
                if temp.meta_type != local.meta_type:
                    self.delObjects([i])
                    self.setObject(i, temp)
                elif local.meta_type == 'CompoundDoc':
                    #if the item is a CompoundDoc it must be treated differently
                    local.objectLoadCDoc(temp)
                elif utility.isinstance(local, BaseObject):
                    #only use loadData on items derived from BaseObject
                    local.loadData(temp)
                objectIds.remove(i)

        typeKeepList = self.getProfileTypeKeep()
        keeplist = cdoc.__dict__.keys()

        assistants = self.aq_parent.objectValues(['CreationAssistant', 'CreationAssistantString', 'CreationAssistantDTML'])
        if assistants:
            for i in assistants:
                if i.idTypeMapping is not None:
                    keeplist.extend(i.idTypeMapping.keys())
        available = cdoc.availableObjects()
        temp = [(name, getattr(cdoc, 'meta_type', None)) for name, cdoc in self.objectItems()]
        self.delObjects([name for name, meta_type in temp if meta_type in available and name not in keeplist and meta_type not in typeKeepList])

        if assistants:
            for i in assistants:
                i.setupObject(self)
       
    security.declarePrivate('loadData')
    def loadData(self, attribute):
        """load data from attribute into myself I will only get this if I am the
        same type attribute it is and the default is for me to keep all of my data
        but for it to overwrite my config"""
        replaceList = ['observing', 'observed']
        replaceList.extend(self.updateReplaceList)
        noreplace = ['userModificationTimeStamp', 'manage_workspace', 'manage_main', 'manage',
          'manage_edit_form','ControlPanel', 'submitChanges', '_objects']
        overwrite = self.overwrite
        updateAlways = self.updateAlways
        if hasattr(aq_base(self), 'configLoader') and hasattr(aq_base(attribute), 'objectConfig'):
            self.configLoader(attribute.objectConfig)
            noreplace.append('objectConfig')
        else:
            replaceList.append('objectConfig')
        if hasattr(aq_base(self), 'customLoadData'):
            self.customLoadData(attribute)
        for i in attribute.__dict__:
            if updateAlways:
                self.updateObject(i, aq_base(getattr(attribute, i)))
            elif i in replaceList or not i in self.__dict__ or overwrite:
                self.delObjects([i])
                self.setObject(i, aq_base(getattr(attribute, i)))
            elif getattr(attribute,i) and not getattr(self,i):
                self.delObjects([i])
                self.setObject(i, aq_base(getattr(attribute, i)))
            elif i in noreplace or (hasattr(aq_base(self), i) and getattr(self,i)):
                pass
            
        #anything that we are supposed to replace that the attribute does not we need to delete
        self.delObjects([i for i in replaceList if (i not in attribute.__dict__ and i in self.__dict__)])

        self.createMetaMapping()

        assistants = [i for i in self.aq_parent.objectValues(['CreationAssistant', 'CreationAssistantString', 'CreationAssistantDTML'])]
        for i in assistants:
            i.setupObject(self)


    security.declarePrivate('objectLoadCDocDisplayOnly')
    def objectLoadCDocDisplayOnly(self, cdoc):
        "load another compounddoc rendering system into this compounddoc"
        replaceList = ['DisplayManager', 'displayMap', 'defaultDisplay']

        if cdoc.masterLocation is not None:
            if cdoc.masterLocation != self.getPath():
                master = self.unrestrictedTraverse(cdoc.masterLocation, None)
                if master is not None and master.meta_type == 'CompoundDoc' and master.DisplayManager is not None:
                    self.setObject('DisplayManager', aq_base(master.DisplayManager))
            replaceList.remove('DisplayManager')
        #do replacemants
        for i in replaceList:
            temp = aq_base(getattr(cdoc, i))
            self.delObjects([i])
            self.setObject(i, temp)
        
Globals.InitializeClass(MixObjectLoadStore)
