# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2005 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from BTrees.OOBTree import OOBTree

import BTrees.Length

import utility


class LookupTable(base.Base):
    "LookupTable class"

    meta_type = "LookupTable"
    security = ClassSecurityInfo()
    records = None
    recordsLength = None

    drawDict = base.Base.drawDict.copy()
    drawDict['drawTable'] = 'drawTable'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        format = "<p>Currently there are %s records</p><div>%s</div>"
        if self.records is None:
            self.records = OOBTree()
        lenRecords = self.recordsLength() if self.recordsLength is not None else 0
        return format % (lenRecords, self.create_button('clear', "Clear"))

    security.declarePrivate('processRecorderChanges')
    def processRecorderChanges(self, form):
        "process the recorder changes"
        clear = form.pop('clear', None)
        if clear is not None:
            self.clear()

    security.declarePrivate('after_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        self.processRecorderChanges(form)

    security.declareProtected('View management screens', "drawTable")
    def drawTable(self):
        "Render page"
        temp = []
        format = '<p>%s:%s</p>'
        if self.records is not None:
            for key,value in self.records.items():
                temp.append(format % (repr(key), repr(value)))
        return ''.join(temp)

    security.declareProtected('Python Record Modification', 'insert')
    def insert(self, key, value):
        "modify this key and value into the OOBTree"
        if self.records is None:
            self.records = OOBTree()
        if self.recordsLength is None:
            self.setObject('recordsLength' ,BTrees.Length.Length())
        
        if key not in self.records:
            self.recordsLength.change(1)
        self.records.insert(key,value)

    security.declareProtected('Python Record Modification', 'add')
    def add(self, key, value):
        "this this key and value into the OOBTree"
        if self.records is None:
            self.records = OOBTree()
        if self.recordsLength is None:
            self.setObject('recordsLength' ,BTrees.Length.Length())
        
        if key not in self.records:
            self.recordsLength.change(1)
        self.records[key] = value

    security.declareProtected('Python Record Access', 'items')
    def items(self, min=None, max=None):
        "return the items in this OOBTree"
        if self.records is None:
            return []
        return self.records.items(min, max)

    security.declareProtected('Python Record Access', 'values')
    def values(self, min=None, max=None):
        "return the values of this OOBTree"
        if self.records is None:
            return []
        return self.records.values(min, max)

    security.declareProtected('Python Record Modification', 'update')
    def update(self, collection):
        "update our OOBTree with the data in collection"
        if self.records is None:
            self.records = OOBTree()
        if self.recordsLength is None:
            self.setObject('recordsLength' ,BTrees.Length.Length())
        
        records = self.records
        change = self.recordsLength.change
        for key,value in collection.items():
            if key not in records:
                change(1)
            records[key] = value

    security.declareProtected('Python Record Access', 'keys')
    def keys(self, min=None, max=None):
        "return the keys of this OOBTree"
        if self.records is None:
            return []
        return self.records.keys(min,max)

    security.declareProtected('Python Record Modification', '__delitem__')
    def __delitem__(self, key):
        "delete this key from the OOBTree"
        if self.records is not None:
            del self.records[key]
            self.recordsLength.change(-1)

    security.declareProtected('Python Record Modification', 'remove')
    def remove(self, key):
        "delete this key from the OOBTree"
        if self.records is not None:
            del self.records[key]
            self.recordsLength.change(-1)

    security.declareProtected('Python Record Modification', '__setitem__')
    def __setitem__(self, key, value):
        "set this key and value in the OOBTree"
        if self.records is None:
            self.records = OOBTree()
        self.records[key] = value

    security.declareProtected('Python Record Access', '__getitem__')
    def __getitem__(self, index):
        "get this item from the OOBTree"
        if self.records is not None:
            return self.records[index]
        raise KeyError, index

    security.declareProtected('Python Record Access', 'get')
    def get(self, key, default=None):
        "get this item from the OOBTree"
        if self.records is not None:
            return self.records.get(key,default)
        return default

    security.declareProtected('Python Record Access', 'has_key')
    def has_key(self, key):
        "see if we have this key in the OOBTree"
        if self.records is not None:
            return self.records.has_key(key)
        return False

    security.declareProtected('Python Record Modification', 'clear')
    def clear(self):
        "clear the OOBTree"
        self.setObject('records', None)
        self.setObject('recordsLength', None)
        
    security.declarePrivate("PrincipiaSearchSource")
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''
      
    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.createBTreeLength() 
      
    security.declarePrivate('createBTreeLength')
    def createBTreeLength(self):
        "remove Filters that are not being used"
        if self.records is not None:
            length = BTrees.Length.Length()
            length.set(len(self.records))
            self.setObject('recordsLength', length)
    createBTreeLength = utility.upgradeLimit(createBTreeLength, 165)


Globals.InitializeClass(LookupTable)
import register
register.registerClass(LookupTable)
