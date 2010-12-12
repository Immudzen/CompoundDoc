#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from userobject import UserObject

from BTrees.OOBTree import OOTreeSet
import types
import utility

import os.path

class SimpleList(UserObject):
    "SimpleList object"

    security = ClassSecurityInfo()
    meta_type = "SimpleList"
    radioOptions = ( ('append', 'Add'), ('remove', 'Remove') , ('replace', 'Replace') )

    entry = None

    security.declareProtected('CompoundDoc: Modify SimpleList', 'addEntries')
    def addEntries(self,items):
        "add these items to our current list of items"
        if self.entry is None:
            self.replaceEntries(items)
        for item in items:
            if not self.entry.has_key(item):
                self.entry.insert(item)
    
    security.declareProtected('CompoundDoc: Modify SimpleList', 'removeEntries')
    def removeEntries(self,items):
        "removes these items from the current set of entries"
        if self.entry is not None:
            for item in items:
                if self.entry.has_key(item):
                    self.entry.remove(item)
    
    security.declareProtected('CompoundDoc: Modify SimpleList', 'replaceEntries')
    def replaceEntries(self,items):
        "replace all the entries with these ones"
        self.entry = OOTreeSet()
        for item in items:
            self.entry.insert(item)    
    
    security.declareProtected('CompoundDoc: View SimpleList', 'drawViewWindows')
    def drawViewWindows(self):
        "draw the list of addresses in windows format"
        return '\r\n'.join(self.getEntries()) 
        
    security.declareProtected('CompoundDoc: View SimpleList', 'drawViewMac')
    def drawViewMac(self):
        "draw the list of addresses in mac format"
        return '\r'.join(self.getEntries())
        
    security.declareProtected('CompoundDoc: View SimpleList', 'drawViewUnix')
    def drawViewUnix(self):
        "draw the list of addresses in unix format"
        return '\n'.join(self.getEntries())        
            
            
    radioLookup = {'append' : addEntries, 'remove' : removeEntries , 'replace' : replaceEntries }
    
    security.declareProtected('CompoundDoc: Add List Item', 'addEntry')
    def addEntry(self, item):
        "Add an entry to the list"
        if self.entry is None:
            self.entry = OOTreeSet()
        self.entry.insert(item)

    security.declareProtected('CompoundDoc: Del List Item', 'delEntry')
    def delEntry(self, item):
        "Remove an entry form the list"
        if self.entry.has_key(item):
            self.entry.remove(item)
            if not len(self.entry):
                self.entry = None

    security.declareProtected('CompoundDoc: Has List Item', 'hasEntry')
    def hasEntry(self,item):
        "Do we have this item"
        if self.entry is not None:
            return self.entry.has_key(item)

    security.declareProtected('CompoundDoc: Get List Items', 'getEntries')
    def getEntries(self):
        "Return all the entries as a list"
        if self.entry is not None:
            return self.entry.keys()
        return OOTreeSet()

    security.declareProtected('CompoundDoc: Get List Items', 'getTree')
    def getTree(self):
        "Return all the entries as the native format"
        if self.entry is not None:
            return self.entry
        return OOTreeSet()

    security.declareProtected('CompoundDoc: Clear List Items', 'clearEntries')
    def clearEntries(self):
        "Remove all the entries from the object"
        self.entry = None

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "process the edits"
        if 'editAdd' in dict and 'editAddName' in dict:
            self.addEntries(dict['editAddName'])
        if 'editDel' in dict and 'editDelName' in dict:
            self.removeEntries(dict['editDelName'])
        if 'editClear' in dict:
            self.clearEntries()
            
        data = dict.pop('data', None)
        if data is not None:
            temp = data.read().split()
            self.radioLookup[dict['fileSettings']](self,temp)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        append = temp.append
        append(self.text_area('editAddName', '', formType="tokens"))
        append('<p>%s</p>' % self.create_button("editAdd", "Add Entries"))
        append(self.text_area('editDelName', '', formType="tokens"))
        append('<p>%s</p>' % self.create_button("editDel", "Delete Entries"))
        
        append('<p>Upload File:')
        append(self.input_file('data'))
        temp.extend(self.radio_list('fileSettings', self.radioOptions, selected='append'))
        append('</p>')
        
        append(self.create_button("editClear", "Clear All Entries"))
        
        append('<p>View Email Addresses:')
        path = self.absolute_url_path()
        format = ' <a href="%s">%s</a> '
        append(format % (os.path.join(path, 'drawViewWindows'), 'Windows'))
        append(format % (os.path.join(path, 'drawViewUnix'), 'Unix'))
        append(format % (os.path.join(path, 'drawViewMac'), 'Mac'))
        append('</p>')
        
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.unorderedList(self.getEntries())

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ' '.join(self.getEntries())
    
    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.convertListToOOTreeSet()
        
    security.declarePrivate('convertListToOOTreeSet')
    def convertListToOOTreeSet(self):
        "conver the list object to an OOTreeSet"
        if len(self.entry) and isinstance(self.entry, types.ListType):
            temp = OOTreeSet()
            for i in self.entry:
                temp.insert(i)
            self.setObject('entry', temp)
    convertListToOOTreeSet = utility.upgradeLimit(convertListToOOTreeSet, 141)
        
Globals.InitializeClass(SimpleList)
import register
register.registerClass(SimpleList)