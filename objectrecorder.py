# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
import base
import copy

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from DateTime import DateTime

from BTrees.IOBTree import IOBTree

class ObjectRecorder(base.Base):
    """Object Recorder works like a data recorder but instead of storing dictionaries it stores other
    kinds of objects over time."""

    meta_type = "ObjectRecorder"
    security = ClassSecurityInfo()
    recordType = None
    dictMap = "recordMap.%s"
    records = None

    def __getattr__(self, name):
        try:
            name = int(name)
        except ValueError:
            return base.Base.__getattr__(self,name)
        if self.records:
            try:
                return self.records[name]['record'].__of__(self)
            except KeyError:
                pass

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        format = "<p>Currently there are %s records of %s type.</p><div>%s</div>"
        if self.records is None:
            self.records = IOBTree()
        if self.records:
            temp.append(format % (len(self.records), self.recordType, self.create_button('clear', "Clear")))
            temp.append('''<p>Show: <a href="?show:int=2" class="rightSpacer">All</a>
              <a href="?show:int=1" class="rightSpacer">Processed</a>
              <a href="?show:int=0">Unprocessed</a></p>''')
            table = [['Date Posted','Data','Processed']]
            showSetting = self.getShowSetting()
            for name,record in self.objectItems(self.recordType):
                processedState = self.records[int(name)]['processed']

                if showSetting == 0 and processedState == 0:
                    table.append(self.generateTableRow(name,record,processedState))
                elif showSetting == 1 and processedState == 1:
                    table.append(self.generateTableRow(name,record,processedState))
                elif showSetting == 2:
                    table.append(self.generateTableRow(name,record,processedState))
            temp.append(self.createTable(table))
        return ''.join(temp)

    security.declarePrivate('generateTableRow')
    def generateTableRow(self,name, record,processedState):
        "generate the entries needed for a row in the table"
        date = self.records[int(name)]['date'].fCommon()
        data = record(mode='view')
        processed = self.radio_box(self.dictMap % name, processedState)
        return [date, data, processed]

    security.declarePrivate('getShowSetting')
    def getShowSetting(self):
        "Get the selected month and year"
        show = 0
        if self.REQUEST.form:
            show = int(self.REQUEST.form.get('show',0))
            if show > 2 or show < 0:
                show = 0
        return show

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        allowableTypes = self.restrictedUserObject()
        return self.option_select(allowableTypes, 'recordType', (self.recordType,))

    security.declarePrivate('processRecorderChanges')
    def processRecorderChanges(self, form):
        "process the recorder changes"
        if form.pop('clear',None):
            self.records.clear()
            self.delObjects(map(str,self.objectIds(self.recordType)))

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        self.processRecorderChanges(form)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self,form):
        "process the recordMap var for processed items"
        if 'recordMap' in form:
            for key,value in form['recordMap'].items():
                record = self.records[int(key)]
                record['processed'] = value
                self.records[int(key)] = record

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return ''

    security.declareProtected('Python Record Addition', 'addRecord')
    def addRecord(self, record):
        "Add a record object which is of the type that we are currently accepting"
        storageRecord = None
        if self.records is None:
            self.records = IOBTree()
        if self.records:
            nextKey = self.records.maxKey()+1
        else:
            nextKey = 0
        if self.recordType is not None and getattr(record, 'meta_type', None) == self.recordType:
            storageRecord = copy.deepcopy(record)
        elif self.recordType and record:
            storageRecord = self.createRegisteredObject(str(nextKey), self.recordType)
            dataLoader = getattr(storageRecord, 'dataLoader', None)
            if dataLoader is not None:
                storageRecord.__of__(self).gen_vars()
                dataLoader({'data':record, 'title':{'data':'Record'}, 'filename':{'data':'file'}})
            else:
                storageRecord = None

        if storageRecord is not None:
            self.records[nextKey] = {'record':storageRecord, 'date':DateTime(), 'processed':0}
            self._updateMetaMapping(str(nextKey),storageRecord)


    def _getOb(self, id, default=None):
        btree = self.records
        if not btree.has_key(int(id)):
            if default is None:
                raise AttributeError, id
            return default
        else:
            return btree[int(id)]['record'].__of__(self)

    security.declareProtected('Python Record Access', 'getRecords')
    def getRecords(self):
        "Return the list that has all the records in it for python script use only"
        if self.records is None:
            self.records = IOBTree()
        return self.records.values()

    def getRecordObject(self):
        "return the actual BTree object this is for python prduct use only"
        if self.records is None:
            self.records = IOBTree()
        return self.records

    def getRecordKeys(self):
        "return the keys for recorded objects and make them strings"
        if self.records is None:
            self.records = IOBTree()
        return map(str, self.records.keys())

    security.declarePrivate("PrincipiaSearchSource")
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

Globals.InitializeClass(ObjectRecorder)
import register
register.registerClass(ObjectRecorder)
