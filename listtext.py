# -*- coding: utf-8 -*-
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from Acquisition import aq_base
import time
import operator
import utility

class ListText(base.Base):
    "ListText is a list of text objects"

    meta_type = "ListText"
    security = ClassSecurityInfo()
    updateAlways = 1
    data = ''
    sortedList = None
    listBegin = '<ul>'
    listEnd = '</ul>'
    addType = 'InputText'
    deleteButtonText = 'Delete List Entry'
    addButtonText = 'Add List Entry'
    scriptChangePath = ''
    
    
    allowedListTypes = ('InputText', 'TextArea', 'InputFloat', 
        'Date', 'File', 'InputInt', 'Money', 'Picture')

    classConfig = {}
    classConfig['addType'] = {'name':'Type of Objects in List', 'type':'list', 'values': allowedListTypes}
    classConfig['listBegin'] = {'name':'listBegin', 'type':'string'}
    classConfig['listEnd'] = {'name':'listEnd', 'type':'string'}
    classConfig['scriptChangePath'] = {'name':'Path to change notification script', 'type': 'path'}
    
    updateReplaceList = ('listBegin', 'listEnd', 'addType', 'deleteButtonText', 'addButtonText', )
    
    configurable = ('listBegin', 'listEnd', 'addType',)
    
    security.declarePrivate('add_delete_objects')
    def add_delete_objects(self, form):
        "Add new objects to the existing object"
        if form.get('removeme', "") != "":
            self.delListItem(form['removeme'])
        if 'Add' in form:
            self.addListItem()

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        temp = []
        if self.sortedList:
            for i in self:
                temp.append(i.PrincipiaSearchSource())
        return ' '.join(temp)            
            
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        temp = []
        listBegin = self.getConfig('listBegin')
        listEnd = self.getConfig('listEnd')
        if self.sortedList:
            temp.append(listBegin)
            for i in self:
                text = i.view()
                if text:
                    temp.append('<li>%s</li>' % text)
            temp.append(listEnd)
        return ''.join(temp)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div class="outline">']
        temp.append(self.addDeleteObjectsEdit())
        if self.sortedList:
            format = '<div class="outline">%s</div>'
            for i in self:
                temp.append(format % i.edit())
        temp.append("</div>")
        return ''.join(temp)

    security.declarePrivate('getDeletionNames')
    def getDeletionNames(self,allowableTypes):
        "return the names are should be used for deletion"
        if self.sortedList:
            #do the count from 1 instead of 0
            return [""] + range(1,len(self)+1)
        return ()

    security.declarePrivate('getDeleteButtonName')
    def getDeleteButtonName(self,allowableTypes):
        "get the text for the delete button"
        return self.deleteButtonText

    security.declarePrivate('getAddButtonName')
    def getAddButtonName(self,allowableTypes):
        "get the text for the add button"
        return self.addButtonText

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        return [self.getConfig('addType')]

    security.declarePrivate('add_delete_objects_edit')
    def addDeleteObjectsEdit(self):
        "This is the form elements for adding and deleting objects without the form wrapper"
        return '%s %s' % (self.addObjectsEdit(autoId=1,autoType=1), self.deleteObjectsEdit())

    security.declarePrivate("getAvailableListsContents")
    def getAvailableListsContents(self):
        "Return a list of all available list items"
        if self.sortedList:
            return  [object.data for object in self]
        return []
    
    #List behavior stuff
    
    security.declareProtected("Access contents information", "__getitem__")
    def __getitem__(self, i):
        if self.sortedList is not None:
            return self.sortedList[i].__of__(self)
        raise IndexError
    
    security.declareProtected("Access contents information", "__getslice__")
    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        for i in self.sortedList[i:j]:
            yield i.__of__(self)
    
    security.declareProtected("Access contents information", "__iter__")
    def __iter__(self):
        if self.sortedList:
            for i in self.sortedList:
                yield i.__of__(self)

    security.declareProtected("Access contents information", "__len__")
    def __len__(self):
        if self.sortedList:
            return len(self.sortedList)
        return 0 
    
    security.declareProtected('Change CompoundDoc', '__setitem__', '__guarded_setitem__')
    def __setitem__(self, i, item): 
        if self.sortedList:
            self.sortedList[i].__of__(self).populatorLoader(item)
        self._p_changed = 1
    __guarded_setitem__ = __setitem__
        
    security.declareProtected('Change CompoundDoc', '__delitem__', '__guarded_delitem__')
    def __delitem__(self, i):
        if self.sortedList: 
            objectId = self.sortedList[i].getId()
            self.deleteRegisteredObject(objectId, [])
            del self.sortedList[i]
            if not len(self.sortedList):
                self.sortedList=None
            self._p_changed = 1
    __guarded_delitem__ = __delitem__
    
    #For some reason through the web code can't call this method so disabling it
    #security.declareProtected('Change CompoundDoc', '__setslice__')
    #def __setslice__(self, i, j, other):
    #    i = max(i, 0); j = max(j, 0)
    #    if self.sortedList:
    #        for index in range(i,j):
    #            self.sortedList[index] = other[index]
    
    #For some reason through the web code can't call this method so disabling it
    #security.declareProtected('Change CompoundDoc', '__delslice__')
    #def __delslice__(self, i, j):
    #    i = max(i, 0); j = max(j, 0)
    #    if self.sortedList:
    #        items = self.sortedList[i:j]
    #        del self.sortedList[i:j]
    #        for i in items:
    #            self.deleteRegisteredObject(i.getId(), [])    
    #        if not len(self.sortedList):
    #            self.sortedList=None
    #        self._p_changed = 1
    
    security.declareProtected('Change CompoundDoc', 'append')
    def append(self, item):
        if not self.sortedList:
            self.sortedList = []
        obj = self.createNextItem()
        obj.populatorLoader(item)    
        self.sortedList.append(obj)
        self._p_changed = 1
    
    security.declareProtected('Change CompoundDoc', 'insert')
    def insert(self, i, item):
        if not self.sortedList:
            self.sortedList = []
        obj = self.createNextItem()
        obj.populatorLoader(item)
        self.sortedList.insert(i, obj)
        self._p_changed = 1 
    
    security.declareProtected('Change CompoundDoc', 'pop')
    def pop(self, i=-1): 
        if self.sortedList:
            item = self[i]
            del self[i]
            return item
    
    security.declareProtected('Change CompoundDoc', 'reverse')
    def reverse(self): 
        if self.sortedList:
            self.sortedList.reverse()
            self._p_changed = 1    
    
    #End list behavior stuff
    
    security.declarePrivate('createNextItem')
    def createNextItem(self):
        'create the next object we can use'
        name = utility.cleanRegisteredId(repr(time.time()).replace('.', '_'))
        self.updateRegisteredObject(name, self.getConfig('addType'))
        return aq_base(getattr(self,name))
    
    security.declarePrivate('addListItem')
    def addListItem(self):
        "add a new list item"
        obj = self.createNextItem()
        if not self.sortedList:
            self.sortedList = []
        self.sortedList.append(obj)
        self._p_changed=1

    security.declarePrivate('delListItem')
    def delListItem(self, name):
        "delete a list item"
        try:
            position = int(name)-1
            del self[position]
        except ValueError:
            pass

    security.declarePrivate("removeUnNeeded")
    def removeUnNeeded(self, list, typekeep):
        "Remove the UnNeeded items based on this list"
        pass

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeListIndex()
        self.cleanupNames()
        self.repairSortedList()

    security.declarePrivate("removeListIndex")
    def removeListIndex(self):
        "remove the listIndex"
        if self.hasObject('listIndex'):
            self.delObjects(['listIndex'])
    removeListIndex = utility.upgradeLimit(removeListIndex, 141)
            
    security.declarePrivate("cleanupNames")
    def cleanupNames(self):
        "clean up the names in this listtext object"
        addType = self.getConfig('addType')
        if not reduce(operator.add,[name.count('_') for name in self.objectIds(addType)],0):
            oldobjects = []
            objectItems = self.objectItems(addType)
            objectItems.sort()
            for name,inputtext in objectItems:
                self.addListItem()
                #the last element i the list is what we want
                self.sortedList[-1].data = inputtext.data
                oldobjects.append(name)
            self.delObjects(oldobjects)
    cleanupNames = utility.upgradeLimit(cleanupNames, 141)
            
    security.declarePrivate("repairSortedList")
    def repairSortedList(self):
        "repair the sortedList object"
        if self.sortedList and len(self.sortedList) != len(self.objectIds(self.addType)):
            "sortedList is broken because it does not match the objects that should be in it regenerate it"
            addType = self.getConfig('addType')
            self.sortedList = [aq_base(inputtext) for inputtext in self.objectValues(addType)]
    repairSortedList = utility.upgradeLimit(repairSortedList, 141)
    
    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        if self.sortedList:
            return ' /-\ '.join([item.data.replace('\n','\\n') for item in self.sortedList])
        return ''

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        items = string.split(' /-\ ')
        total = 0
        if self.sortedList:
            total = len(self.sortedList)
        if len(items) < total:
            numberToDelete = total - len(items)
            self.delObjects([item.getId() for item in self.sortedList[-numberToDelete:]])
            self.sortedList = self.sortedList[0:-numberToDelete]
        elif len(items) > total:
            for i in xrange(len(items)-total):
                self.addListItem()
        for i in xrange(total):
            self.sortedList[i].__of__(self).setObject('data',items[i].replace('\\n','\n'))

Globals.InitializeClass(ListText)
import register
register.registerClass(ListText)