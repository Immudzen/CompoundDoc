###########################################################################
#    Copyright (C) 2005 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from Acquisition import aq_base

from base import Base

class CouldNotAddPathError(Exception): pass

class LinkManager(Base):
    "link an object in this document to the same db location as another object"

    security = ClassSecurityInfo()
    meta_type = "LinkManager"
    lookup = None
    names = None
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append(self.create_button('resync', 'Resync', containers=['resync']))
        temp.append(self.create_button('create_link', 'Create Link', containers=['create']))
        temp.append(self.input_text(name='path', containers=['create']))
        cdoc = self.getCompoundDoc()
        cdocContainer = self.getCompoundDocContainer()
        table = [['Delete', 'Name','Path','Status', 'Meta Type']]
        for path in self.getLookup():
            name = path.split('/')[-1]
            status = 'BAD'
            itemLocal = getattr(cdoc, name, None)
            localType = 'no data'
            if itemLocal is not None:
                localType = itemLocal.meta_type
            itemRemote = cdocContainer.restrictedTraverse(path, None)
            if aq_base(itemLocal) is aq_base(itemRemote):
                status = "OK"
            delete = self.check_box('ids', path, containers = ('delete',), formType = 'list')
            table.append([delete, name, path, status, localType])
        temp.append(self.createTable(table))
        temp.append(self.create_button('delete', 'Delete Selected Items', containers=['delete']))
        return ''.join(temp)

    security.declarePrivate('customLoadData')
    def customLoadData(self, newLink):
        "newLink is the new LinkManager that will be used to populate this one"
        newLookup = set(newLink.getLookup())
        lookup = set(self.getLookup())
        itemsToAdd = newLookup - lookup
        for path in itemsToAdd:
            self.addPath(path)    
        itemsToRemove = lookup - newLookup
        self.removeLinks(itemsToRemove)
        self.resync()

    security.declarePrivate('eventProfileLast')
    def eventProfileLast(self):
        "run this event as the last thing the object will do before the profile is returned"
        self.resync()

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        create = dict.pop('create', None)
        if create is not None:
            createLink = create.get('create_link')
            path = create.get('path')
            if createLink and path:
                self.addPath(path)
                
        resync = dict.pop('resync', None)
        if resync is not None:
            if 'resync' in resync:
                self.resync()
        
        delete = dict.pop('delete', None)
        if delete is not None:
            if 'delete' in delete and 'ids' in delete:
                self.removeLinks(dict['delete']['ids'])

    def removeLinks(self, paths):
        "remove links that have been selected"
        lookup = self.getLookup()
        names = self.getNames()
        forDeletion = []
        for path in paths:
            name = path.split('/')[-1]
            forDeletion.append(name)
            if name in names:
                names.remove(name)
            if path in lookup:
                lookup.remove(path)
        if forDeletion:
            self.getCompoundDoc().delObjects(forDeletion)
            self.names = names
            self.lookup = lookup
            
    def addPath(self, path):
        "is it okay to add this path?"
        "it is okay to add this path as long as we can get to it without violating security"
        lookup = self.getLookup()
        cdoc = self.getCompoundDoc()
        item = self.getCompoundDocContainer().restrictedTraverse(path, None)
        names = self.getNames()
        if item is not None and hasattr(aq_base(item), 'meta_type'):
            name = item.getId()
            if name not in names and not hasattr(aq_base(cdoc), name):
                names.add(name)
                self.names = names
                cdoc.setObject(name, aq_base(item))
                lookup.append(path)
                self.lookup = sorted(lookup)

    def resync(self):
        "resync our list of paths to link with the internal cdoc state"
        lookup = self.getLookup()
        cdoc = self.getCompoundDoc()
        names = self.getNames()
        for path in lookup:
            item = self.getCompoundDocContainer().restrictedTraverse(path, None)
            if item is not None and hasattr(aq_base(item), 'meta_type'):
                name = item.getId()
                if name not in names:
                    names.add(name)
                if not hasattr(aq_base(cdoc), name) or item.meta_type == getattr(cdoc, name).meta_type:
                    cdoc.setObject(name, aq_base(item))
        self.names = names
            

    security.declarePrivate('getLookup')
    def getLookup(self):
        "get the current lookup variable"
        if self.lookup is not None:
            return self.lookup
        return []

    security.declarePrivate('getLookup')
    def getNames(self):
        "get the current lookup variable"
        if self.names is not None:
            return self.names
        return set()

Globals.InitializeClass(LinkManager)
import register
register.registerClass(LinkManager)