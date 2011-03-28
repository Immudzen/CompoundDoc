# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject
import utility
import validators
import itertools

class Selection(UserObject):
    "Input text class"

    security = ClassSecurityInfo()
    meta_type = "Selection"

    data = None
    selection = None
    scriptPath = ""
    multipleSelect = 0
    rowsVisible = 1
    allowClear = 0
    outputFormat = 'list'
    dataType = 'string'
    scriptChangePath = ''

    outputValues = ( ('list', 'Drop Down List'), ('radioinline', 'Radio Box Inline'), ('radioblock', 'Radio Box Block'),
        ('checkinline', 'CheckBox Inline'), ('checkblock', 'CheckBox Block'))
    dateTypes = ('string', 'int', 'float')

    classConfig = {}
    classConfig['scriptPath'] = {'name':'Path to Script', 'type':'path'}
    classConfig['multipleSelect'] = {'name':'Enable Multiple Selection', 'type': 'radio'}
    classConfig['rowsVisible'] = {'name':'Number of Rows Visible for Selection', 'type': 'int'}
    classConfig['allowClear'] = {'name':'Enable the clear button', 'type': 'radio'}
    classConfig['outputFormat'] = {'name':'Output Format', 'type': 'list', 'values': outputValues}
    classConfig['dataType'] = {'name':'Type of Date Stored', 'type': 'list', 'values': dateTypes}
    classConfig['scriptChangePath'] = {'name':'Path to change notification script', 'type': 'path'}
    
    updateReplaceList = ('scriptPath', 'multipleSelect', 'rowsVisible', 'allowClear', 'outputFormat', 'dataType', )
    
    configurable = ('dataType', 'allowClear', 'outputFormat', 'multipleSelect', 'rowsVisible', 'scriptPath',) 
    
    security.declarePrivate('validate_data')
    def validate_data(self, value):
        "validate this value for the new value for the data attribute and then return what is okay"
        if isinstance(value, basestring):
            value = [value,]
        temp = []
        allowed = set(self.getChoiceValues())
        checker = validators.getChecker(self.getConfig('dataType'))
        for i in value:
            i = checker(i)
            if i is not None and i in allowed:
                temp.append(i)
        if temp:
            return temp

    security.declarePrivate('post_process_dataType')    
    def post_process_dataType(self, before, after):
        "if the dataType is changed we need to ensure that all items in data fall in this new data type"
        self.revalidateData()

    security.declarePrivate('revalidateData')
    def revalidateData(self):
        "revalidate this data object"
        data = self.data
        if data is not None:
            self.setObject('data', self.validate_data(data))

    security.declareProtected('View management screens', 'edit')
    def edit(self, outputFormat=None, *args, **kw):
        "Inline edit short object"
        clear = ''
        if self.getConfig('allowClear'):
            clear = self.create_button('clear', 'Clear %s' % self.getId()) + '<br>' 
        return clear + self.getEditControl(outputFormat)

    security.declarePrivate('getEditControl')
    def getEditControl(self, outputFormat=None):
        "get the edit control"
        choices = self.getChoices()
        data = self.data
        if data is None:
            data = []
        outputFormat = outputFormat or self.getConfig('outputFormat')
        if outputFormat == 'list':
            return self.option_select(choices, 'data', data, multiple=self.getConfig('multipleSelect'),
                    size=self.getConfig('rowsVisible'), dataType='list')
        if outputFormat == 'radioinline':
            return self.radio_box_inline(choices, 'data', data)
        if outputFormat == 'radioblock':
            return self.radio_box_block(choices, 'data', data)
        if outputFormat == 'checkinline':
            return self.checkbox_inline(choices, 'data', data)
        if outputFormat == 'checkblock':
            return self.checkbox_block(choices, 'data', data)
        return ''
        

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "process the edits"
        clear = dict.pop('clear', None)
        if clear is not None:
            self.setObject('data', None)
            try:
                del dict['data']
            except KeyError:
                pass

    security.declareProtected("Access contents information", 'getChoices')
    def getChoices(self):
        'get the available choices to select from'
        temp = []
        scriptPath = self.getConfig('scriptPath')
        if scriptPath:
            script = self.getCompoundDocContainer().restrictedTraverse(scriptPath, None)
            if script is not None:
                temp = self.changeCallingContext(script)()
        return temp 
        
    security.declareProtected("Access contents information", 'getChoiceValues')
    def getChoiceValues(self):
        'get the available choices to select from'
        for i in self.getChoices():
            if isinstance(i, basestring):
                yield i
            else:
                try:
                    yield i[0]
                except (TypeError, ValueError):
                    yield i
        
    security.declarePrivate('getSelectedItems')
    def getSelectedItems(self):
        "get the currently selected items"
        data = self.data
        if data is None:
            if self.getConfig('multipleSelect'):
                return []
            else:
                return ''
        if self.getConfig('multipleSelect'):
            return data
        else:
            return data[0]
        
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.getSelectedItems()

#List behavior stuff
    
    security.declareProtected("Access contents information", "__getitem__")
    def __getitem__(self, i):
        if self.data:
            return self.data[i]
        raise IndexError
    
    security.declareProtected("Access contents information", "__getslice__")
    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        for i in self.data[i:j]:
            yield i
    
    security.declareProtected("Access contents information", "__iter__")
    def __iter__(self):
        if self.data:
            for i in self.data:
                yield i

    security.declareProtected("Access contents information", "__len__")
    def __len__(self):
        if self.data:
            return len(self.data)
        return 0 
    
    security.declareProtected('Change CompoundDoc', '__setitem__', '__guarded_setitem__')
    def __setitem__(self, i, item): 
        if self.data:
            self.data[i] = item
        self._p_changed = 1
    __guarded_setitem__ = __setitem__
        
    security.declareProtected('Change CompoundDoc', '__delitem__', '__guarded_delitem__')
    def __delitem__(self, i):
        if self.data: 
            del self.data[i]
            if not len(self.data):
                self.data=None
            self._p_changed = 1
    __guarded_delitem__ = __delitem__
    
    #For some reason through the web code can't call this method so disabling it
    #security.declareProtected('Change CompoundDoc', '__setslice__')
    #def __setslice__(self, i, j, other):
    #    i = max(i, 0); j = max(j, 0)
    #    if self.data:
    #        for index in range(i,j):
    #            self.data[index] = other[index]
    
    #For some reason through the web code can't call this method so disabling it
    #security.declareProtected('Change CompoundDoc', '__delslice__')
    #def __delslice__(self, i, j):
    #    i = max(i, 0); j = max(j, 0)
    #    if self.data:
    #        items = self.data[i:j]
    #        del self.data[i:j]
    #        for i in items:
    #            self.deleteRegisteredObject(i.getId(), [])    
    #        if not len(self.data):
    #            self.data=None
    #        self._p_changed = 1
    
    security.declareProtected('Access contents information', '__contains__')
    def __contains__(self, name):
        if self.data:
            return name in self.data
        return False
    
    security.declareProtected('Change CompoundDoc', 'append')
    def append(self, item):
        if not self.data:
            self.data = []
        self.data.append(item)
        self._p_changed = 1
    
    security.declareProtected('Change CompoundDoc', 'insert')
    def insert(self, i, item):
        if not self.data:
            self.data = []
        self.data.insert(i, item)
        self._p_changed = 1 
    
    security.declareProtected('Change CompoundDoc', 'pop')
    def pop(self, i=-1): 
        if self.data:
            item = self[i]
            del self[i]
            return item
    
    security.declareProtected('Change CompoundDoc', 'reverse')
    def reverse(self): 
        if self.data:
            self.data.reverse()
            self._p_changed = 1    
    
    security.declareProtected('Change CompoundDoc', 'clear')
    def clear(self):
        self.setObject('data', None, runValidation=0)
        
    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, items,  runValidation=1):
        self.setObject('data', items,  runValidation)
        
    #End list behavior stuff               

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.makeDataASequence()
        self.clearSelection()
        self.removeScriptEnabled()
        self.fixupData() 
    
    security.declarePrivate('makeDataASequence')
    def makeDataASequence(self):
        "turn data into a sequence if it is not one already"
        data = self.data
        if data is not None and isinstance(data, basestring):
            self.data = [data]
    makeDataASequence = utility.upgradeLimit(makeDataASequence, 141)
    
    security.declarePrivate('clearSelection')
    def clearSelection(self):
        "clear the selection variable it is no longer used"
        self.setObject('selection', None)       
    clearSelection = utility.upgradeLimit(clearSelection, 141)
    
    security.declarePrivate('removeScriptEnabled')
    def removeScriptEnabled(self):
        "remove the scriptEnabled attribute since it is not needed anymore"
        self.delObjects(['scriptEnabled',])       
    removeScriptEnabled = utility.upgradeLimit(removeScriptEnabled, 144)

    security.declarePrivate('fixupData')
    def fixupData(self):
        "if the data attribute is a string turn it into a list"
        self.setObject('data', self.validate_data(self.data))       
    fixupData = utility.upgradeLimit(fixupData, 146)    

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        if self.data:
            return ' /-\ '.join(itertools.imap(str, self.data))
        return ''

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        string = string.strip()
        if string:
            items = string.split(' /-\ ')
            items = map(str.strip, items)
            if items:
                self.setObject('data', items)

Globals.InitializeClass(Selection)
import register
register.registerClass(Selection)
