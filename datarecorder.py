# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
import base
import copy

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from BTrees.OOBTree import OOTreeSet
from BTrees.OOBTree import difference

import BTrees.OOBTree
import time
import types
import utility
import DateTime
import itertools
from OFS.SimpleItem import SimpleItem

from htmldatafilter import HTMLDataFilter
from csvdatafilter import CSVDataFilter
from seperatordatafilter import SeperatorDataFilter

class Record(SimpleItem):
    
    security = ClassSecurityInfo()
    meta_type = "DataRecorder Record"
    
    def __init__(self, name, data, script, parent):
        if script is not None:
            data = script(self, data, parent)
        self.__dict__.update(data)
        self.id = float(name)
        self.recordDate = DateTime.DateTime(float(name))
        
    security.declarePublic('index_html')
    def index_html(self, name='index_html'):
        "draw this document"
        obj = self.getRender(name)
        if obj is not None:
            return obj(self)
        
        format = '<div>%s: %s</div>'
        
        temp = []
        temp.append(format % ('ID', repr(self.id))) 
        for key, value in self.__dict__.iteritems():
            if key != "id":
                temp.append(format % (key, repr(value)))
        return ''.join(temp)
            
Globals.InitializeClass(Record)

class DataRecorder(base.Base):
    "DataRecorder class"

    meta_type = "DataRecorder"
    security = ClassSecurityInfo()
    fieldList = None
    records = None
    archive = None
    allowArchive = 1
    allowClear = 1
    startTime = None
    stopTime = None
    orderHeaderPath = ''
    catalogPath = ''
    catalogArchivePath = ''
    recordScriptPath = ''
    recordRenderScriptPath = ''
    
    fieldOrder = None #just to make it easier to remove from instances
    
    HTMLDataFilter = HTMLDataFilter('HTMLDataFilter')
    CSVDataFilter = CSVDataFilter('CSVDataFilter')
    SeperatorDataFilter = SeperatorDataFilter('SeperatorDataFilter')

    classConfig = {}
    classConfig['allowArchive'] = {'name':'Allow Archiving?:', 'type':'radio'}
    classConfig['allowClear'] = {'name':'Allow Clearing?:', 'type':'radio'}
    classConfig['orderHeaderPath'] = {'name':'Path to Default Config Script', 'type':'path'}
    classConfig['catalogPath'] = {'name':'Path to Catalog', 'type':'path'}
    classConfig['catalogArchivePath'] = {'name':'Path to Archive Catalog', 'type':'path'}
    classConfig['recordScriptPath'] = {'name':'Path to record modifier script', 'type':'path'}
    classConfig['recordRenderScriptPath'] = {'name':'Path to record rendering script', 'type':'path'}
    
    drawDict = base.Base.drawDict.copy()
    drawDict['showRecords'] = 'showRecords'
    drawDict['showArchive'] = 'showArchive'
    drawDict['showFieldList'] = 'showFieldList'
    
    updateReplaceList = ('catalogPath', 'catalogArchivePath', 'orderHeaderPath', 'allowArchive', 'allowClear')
    
    security.declarePrivate('getCatalog')
    def getCatalog(self, archive=None):
        "get the current catalog if there is one"
        if archive is not None:
            path = self.getConfig('catalogArchivePath')
        else:
            path = self.getConfig('catalogPath')
        if path:
            obj = self.getCompoundDoc().restrictedTraverse(path, None)
            if obj is not None and obj.meta_type == 'ZCatalog':
                return obj
    
    security.declarePrivate('getRecordScript')
    def getRecordScript(self):
        "get the record modifier script"
        recordScriptPath = self.recordScriptPath
        if recordScriptPath:
            return self.restrictedTraverse(recordScriptPath, None)
            
    def getRender(self, name):
        "get the default recordRendering script"
        if self.recordRenderScriptPath:
            script = self.getCompoundDocContainer().restrictedTraverse(self.recordRenderScriptPath, None)
            if script is not None:
                return script(name)
    
    security.declareProtected('View management screens', 'showRecords')
    def showRecords(self):
        "show the records"
        return self.showRecordsCommon(archive=0)
        
    security.declareProtected('View management screens', 'showFieldList')    
    def showFieldList(self):
        "show the fieldList as a view"
        return self.unorderedList(self.fieldList or [])
    
    security.declareProtected('View management screens', 'showArchive')
    def showArchive(self):
        "show the records"
        return self.showRecordsCommon(archive=1)

    security.declarePrivate('showRecordsCommon')
    def showRecordsCommon(self, archive):
        "common function for showing records/archives"
        path = '_'.join(self.getPhysicalPath())
        format = '''<div>%s<span id="%s_loadMenu_%s"></span></div>
        <div id="%s_showDocument_%s"></div>
        '''
        return format % (self.getPrimaryMenu(archive=archive), path, archive, path, archive)

    security.declareProtected('View management screens', 'loadRecord')
    def loadRecord(self, archive, selectedDocument):
        "load this record and return it for AJAX"
        name, data = self.getSelectedDocument(archive=archive, selectedDocument=selectedDocument)
        doc = 'Can Not Load Document'
        if name is not None and data is not None:
            doc = Record(name=name, data=data, script=self.getRecordScript(), parent=self).__of__(self).index_html()
        return doc

    security.declarePrivate('getMenu')
    def getPrimaryMenu(self, archive=0):
        "return the menu for these documents this is used in selectOne mode"
        if archive:
            records = self.archive
        else:
            records = self.records
            
        if records is None:
            return ''
            
        temp = []
        
        path = '_'.join(self.getPhysicalPath())
        js = '''onchange="loadRecord(this, '#%s_loadMenu_%s','%s/getSecondaryMenu?archive:int=%s&start:int=')"''' % (path, archive, self.absolute_url(), archive)
        seq = [(idx*100, DateTime.DateTime(i)) for idx,i in enumerate(itertools.islice(records.keys(), None, None, 100))]
        seq.insert(0, ('', 'Load Document') )
        temp.append(self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty', events=js))
        return ''.join(temp)

    security.declareProtected('View management screens', 'getSecondaryMenu')
    def getSecondaryMenu(self, start=0, archive=0):
        "return the menu for these documents this is used in selectOne mode"
        if archive:
            records = self.archive
        else:
            records = self.records
            
        if records is None:
            return ''
            
        temp = []

        path = '_'.join(self.getPhysicalPath())
        js = '''onchange="loadRecord(this, '#%s_showDocument_%s','%s/loadRecord?archive:int=%s&selectedDocument=')"''' % (path, archive, self.absolute_url(), archive)
        seq = [(repr(i), DateTime.DateTime(i)) for i in itertools.islice(records.keys(), start, start+100)]
        seq.insert(0, ('', 'Load Document') )
        temp.append(self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty', events=js))
        return ''.join(temp)

    security.declarePrivate('getSelectedDocument')
    def getSelectedDocument(self, archive=0, selectedDocument=None):
        "get the currently selected document"
        if archive:
            records = self.archive
        else:
            records = self.records
            
        if selectedDocument is not None:
            selectedDocument = float(selectedDocument)
            try:
                return selectedDocument, records[selectedDocument]
            except KeyError:
                pass
        return None, None

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "getattr method"
        try:
            recordName = float(name)
        except ValueError:
            recordName = None
        if self.records is not None and self.records.has_key(recordName):
            "object has an object with name return that"
            doc = Record(name=name, data=self.records[recordName], script=self.getRecordScript(), parent=self).__of__(self)
            return doc
        if self.archive is not None and self.archive.has_key(recordName):
            "object has an object with name return that"
            doc = Record(name=name, data=self.archive[recordName], script=self.getRecordScript(), parent=self).__of__(self)
            return doc
        guard = object()
        item = getattr(self, name, guard)
        if item is not guard:
            return item

    security.declareProtected('View management screens', "edit")
    def edit(self, dateFormat='dropDownDate', *args, **kw):
        "Inline edit short object"
        format = """<p>Currently there are %s records and %s in archive</p>
        <div>%s%s%s</div><p>Search Start Time:%s</p><p>Search Stop Time:%s</p>
        <p>%s</p>"""
        lenArchive = 0
        if self.archive is not None:
            lenArchive = len(self.archive)
            
        lenRecords = 0
        if self.records is not None:
            lenRecords = len(self.records)

        clear = ''
        archive = ''
        archiveClear = ''
        if self.getConfig('allowClear'):
            clear = self.create_button('clear', "Clear")
        
        if self.getConfig('allowArchive'):
            archive = self.create_button('archive', "Archive")
            archiveClear = self.create_button('archiveClear', "Archive & Clear")
        if self.startTime is None:
            self.addRegisteredObject('startTime', 'Date')
            self.startTime.clearDateTime()
        if self.stopTime is None:
            self.addRegisteredObject('stopTime', 'Date')
            self.stopTime.clearDateTime()
        return format % (lenRecords, lenArchive, archiveClear,
          archive, clear, self.startTime(mode='edit', format=dateFormat), self.stopTime(mode='edit', format=dateFormat), self.submitChanges())

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        add = self.create_button('addRecords', "Add All Records To Catalog")
        addArchive = self.create_button('addRecordsArchive', "Add All Archive Records To Catalog")
        return '<p>%s</p><p>%s</p>' % (add, addArchive)

    security.declarePrivate('processRecorderChanges')
    def processRecorderChanges(self, form):
        "process the recorder changes"
        if self.getConfig('allowClear') and form.pop('clear',None):
            self.clearRecords()
        
        if form.pop('addRecords',None):
            self.addRecordsToCatalog()
        
        if form.pop('addRecordsArchive',None):
            self.addRecordsToCatalogArchive()
        elif  self.getConfig('allowArchive') and form.pop('archive',None):
            if self.records is not None:
                self.addMainRecordsToCatalogArchive()

                if self.archive is None:
                    self.setObject('archive', BTrees.OOBTree.OOBTree())
                self.archive.update(self.records)
        elif  self.getConfig('allowArchive') and form.pop('archiveClear',None):
            self.addMainRecordsToCatalogArchive()
            if self.records is not None:
                if self.archive is None:
                    self.setObject('archive', BTrees.OOBTree.OOBTree())

                self.archive.update(self.records)
                self.clearRecords()

    security.declarePrivate('clearRecords')
    def clearRecords(self):
        "clear the current records object and the catalog entries for it"
        if self.records is not None:
            catalog = self.getCatalog()
            if catalog is not None:
                uncatalog_object = catalog.uncatalog_object
                docPath = self.getPath()
                for key in self.records.keys():
                    path = '/'.join([docPath, repr(key)])
                    uncatalog_object(path)
            self.setObject('records', None)
            
    security.declarePrivate('addRecordsToCatalog')
    def addRecordsToCatalog(self):
        "add the current records to the catalog"
        self.addRecordsToCatalogShared(records=self.records)            
            
    security.declarePrivate('addRecordsToCatalogArchive')
    def addRecordsToCatalogArchive(self):
        "add the current records to the catalog"
        self.addRecordsToCatalogShared(archive=1, records=self.archive) 

    security.declarePrivate('addMainRecordsToCatalogArchive')
    def addMainRecordsToCatalogArchive(self):
        "add the current records to the catalog"
        self.addRecordsToCatalogShared(archive=1, records=self.records) 

    security.declarePrivate('addRecordsToCatalogShared')
    def addRecordsToCatalogShared(self, archive=None, records=None):
        "add the current records to the catalog"
        catalog = self.getCatalog(archive)
        
        if catalog is not None and records is not None:
            catalog_object = catalog.catalog_object
            docPath = self.getPath()
            for key, value in records.items():
                doc = Record(name=repr(key), data=copy.deepcopy(value), script=self.getRecordScript(), parent=self).__of__(self)
                path = '/'.join([docPath, repr(key)])
                catalog_object(doc, uid=path)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        self.processRecorderChanges(form)

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return self.HTMLDataFilter.view()

    security.declarePrivate("getDataFilters")
    def getDataFilters(self):
        "Return a list of all available filters"
        return (self.HTMLDataFilter, self.CSVDataFilter, self.SeperatorDataFilter)

    #security.declarePrivate('instance')
    #instance = (('HTMLDataFilter', ('create', 'HTMLDataFilter')),
    #    ('CSVDataFilter', ('create', 'CSVDataFilter')),
    #    ('SeperatorDataFilter', ('create', 'SeperatorDataFilter')))

    security.declareProtected('Python Record Addition', 'addDictObject')
    def addDictObject(self, dict):
        "Add a dict like object and copy its contents into the records list update fileldMap also"
        if hasattr(dict, 'items'):
            temp = copy.deepcopy(dict)
            
            fieldList = self.fieldList
            if fieldList is None:
                fieldList = []
            
            for key in dict:
                if key not in fieldList:
                    fieldList.append(key)
            if fieldList:
                self.setObject('fieldList', fieldList)
            if temp:
                entryTime = time.time()
                if self.records is None:
                    self.setObject('records' ,BTrees.OOBTree.OOBTree())

                self.records[entryTime] = temp
                catalog = self.getCatalog()
                if catalog is not None:
                    doc = Record(name=repr(entryTime), data=temp, script=self.getRecordScript(), parent=self).__of__(self)
                    path = '/'.join([self.getPath(), repr(entryTime)])
                    catalog.catalog_object(doc, uid=path)


    security.declareProtected('Python Record Access', 'getListDict')
    def getListDict(self, start=None, stop=None, query=None, archive=None):
        "Return the list that has all the dicts in it for python script use only"
        allowed = self.getAllowedRecords(query)
        
        if archive is not None:
            records = self.archive
        else:
            records = self.records

        if records is not None:
            if allowed is None:
                return records.values(start, stop)
            else:
                return [records[key] for key in self.allowedKeys(records, start, stop, allowed)]
        return []

    security.declareProtected('Python Record Modification', 'addDataToRecords')
    def addDataToRecords(self, script, start=None, stop=None, query=None, archive=None):
        "Return the list that has all the dicts in it for python script use only"
        allowed = self.getAllowedRecords(query)
        
        if archive is not None:
            records = self.archive
        else:
            records = self.records

        if records is not None:
            if allowed is None:
                for key,value in utility.subTrans(records.items(start, stop),  100):
                    newData = script(value)
                    newData.update(value)
                    records[key] = newData
            else:
                for key in utility.subTrans(self.allowedKeys(records, start, stop, allowed),  100):
                    data = records[key]
                    newData = script(data)
                    newData.update(data)
                    records[key] = newData
        return []

    security.declarePrivate("getAllowedRecords")
    def getAllowedRecords(self, query):
        "get the allowed records based on this query"
        if query is not None:
            catalog = self.getCatalog()
            if catalog is not None:
                return BTrees.OOBTree.OOTreeSet(record.id for record in catalog(query))

    security.declarePrivate("allowedKeys")
    def allowedKeys(self, records, start, stop, allowed):
        "return the allowed keys"
        if start is not None or stop is not None:
            keyRange = BTrees.OOBTree.OOTreeSet(records.keys(min=start, max=stop))
            return BTrees.OOBTree.intersection(keyRange, allowed)
        else:
            return BTrees.OOBTree.intersection(records, allowed)

    security.declareProtected('Python Record Access', 'getFieldList')
    def getFieldList(self):
        "Return the field list for python script use only"
        if self.fieldList is not None:
            return copy.copy(self.fieldList)
        return []

    security.declarePrivate("PrincipiaSearchSource")
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.changeListDictDataRecorder()
        self.changeListDictDataRecorderArchive()
        self.removeNotUsed()
        self.removeNotNeededFilters()

    security.declarePrivate('changeListDictDataRecorder')
    def changeListDictDataRecorder(self):
        "Change the list to a dict in the DataRecorder"
        if isinstance(self.records, types.ListType):
            temp = BTrees.OOBTree.OOBTree()
            for i in self.records:
                temp[time.time()] = i
            self.setObject('records', temp)
    changeListDictDataRecorder = utility.upgradeLimit(changeListDictDataRecorder, 141)
    
    security.declarePrivate('changeListDictDataRecorderArchive')
    def changeListDictDataRecorderArchive(self):
        "Change the list to a dict in the DataRecorder archive item"
        if isinstance(self.archive, types.ListType):
            temp = BTrees.OOBTree.OOBTree()
            for i in self.archive:
                temp[time.time()] = i
            self.setObject('archive', temp)
    changeListDictDataRecorderArchive = utility.upgradeLimit(changeListDictDataRecorderArchive, 141)
        
    security.declarePrivate('removeNotUsed')
    def removeNotUsed(self):
        "remove fieldOrder and archive,fieldList,records if not being used"
        toRemove = ['fieldOrder', 'fileNameBase']

        if not self.fieldList:
            toRemove.append('fieldList')
        if self.archive is not None and not self.archive:
            toRemove.append('archive')
        if self.records is not None and not self.records:
            toRemove.append('records')
        self.delObjects(toRemove)
    removeNotUsed = utility.upgradeLimit(removeNotUsed, 157)

    security.declarePrivate('removeNotNeededFilters')
    def removeNotNeededFilters(self):
        "remove Filters that are not being used"
        toRemove = []

        if getattr(self.CSVDataFilter, 'visible', None) is None:
            toRemove.append('CSVDataFilter')
        if getattr(self.HTMLDataFilter, 'visible', None) is None:
            toRemove.append('HTMLDataFilter')
        if getattr(self.SeperatorDataFilter,'visible', None) is None:
            toRemove.append('SeperatorDataFilter')
        self.delObjects(toRemove)
    removeNotNeededFilters = utility.upgradeLimit(removeNotNeededFilters, 163)

Globals.InitializeClass(DataRecorder)
import register
register.registerClass(DataRecorder)
