# -*- coding: utf-8 -*-
import base

#for type checking with isinstance
import types
import nestedlisturl as NestedListURL
from Acquisition import aq_base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from AccessControl import Unauthorized
import itertools

import utility

class ContainerTraverse(base.Base):
    "traversal capabilities for a catalog transparently and with dynamic menu and output support"

    meta_type = "ContainerTraverse"
    security = ClassSecurityInfo()
    data = ''
    baseURL = ''
    depth = 1
    showCompoundDocs = 0
    sortOn = ''
    folderSortOn = ''
    selected = None
    restrictedMode = 1
    renderScriptPath = ''
    renderer = 'Vertical'
    mergeScriptName = ''
    docsAsNodes = 0
    columns = 0
    folderTypes = set(('Folder', 'BTreeFolder2', 'BTreeFolder'))

    classConfig = {}
    classConfig['renderer'] = {'name':'Rendering Output', 'type':'list',
      'values': NestedListURL.lookup.keys()}
    classConfig['baseURL'] = {'name':'URL to Container:', 'type':'string'}
    classConfig['depth'] = {'name':'Max Depth:', 'type':'int'}
    classConfig['sortOn'] = {'name':'Document Item to sort on:', 'type':'string'}
    classConfig['folderSortOn'] = {'name':'Folder Item to sort on:', 'type':'string'}
    classConfig['showCompoundDocs'] = {'name':'Show CompoundDocs in menu:', 'type':'radio'}
    classConfig['restrictedMode'] = {'name':'Restricted Mode:', 'type':'radio'}
    classConfig['renderScriptPath'] = {'name':'Render Output using this script:', 'type':'string'}
    classConfig['mergeScriptName'] = {'name':'Name of Script to use for merging items in:', 'type':'string'}
    classConfig['docsAsNodes'] = {'name':'Treat Documents as nodes:', 'type':'radio'}
      
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the cart actions and update the session data to the new information"
        clear = form.pop('clear', None)
        if clear is not None:
            self.setObject('selected', None)
            if 'selected' in form:
                del form['selected']

        selected = form.pop('selected', None)
        if selected is not None:
            if not len(selected):
                selected = None
            self.setObject('selected', selected)

    security.declarePrivate('getSelected')
    def getSelected(self):
        "get the preload list structure"
        if self.selected is not None:
            return self.selected
        return []

    security.declareProtected("Access contents information", 'getContainer')
    def getContainer(self):
        "return the continer we are using as an origin"
        return self.restrictedTraverse(self.baseURL)

    security.declareProtected('View', 'view')
    def view(self, cssClassVar=None, menuFunc=None, openContainers=None, baseContainer=None, depth=None, docBase=None, sortFunc=None, renderer=None, openAll=False, columns=None):
        "Inline draw view"
        openContainers = openContainers or []
        container = baseContainer or self.getContainer()
        
        if depth is None:
            depth = self.depth
        
        if columns is None:
            columns = self.columns
        
        docBase = docBase or self
        renderer = renderer or self.renderer

        if openAll:
            nodes = None
            leafs = ()
            path = None
        else:
            nodes = []
            for node in itertools.chain(self.REQUEST.PARENTS, docBase.aq_chain, [container], openContainers):
                try:
                    if node.meta_type in self.folderTypes:
                        nodes.append(node)
                except AttributeError:
                    pass
 
            leafs = set(self.getCurrentLeafNodes(nodes))
            path = set([aq_base(node) for node in nodes])
        temp = self.traverseContainer(level=depth, container=container, path=path, leafs=leafs, sortFunc=sortFunc, openAll=openAll)

        if self.renderScriptPath:
            self.log(self.absolute_url_path())

        temp = self.resolveObjects(temp, menuFunc)
        return NestedListURL.listRenderer(renderer,temp, columns)

    security.declarePrivate('getCurrentLeafNodes')
    def getCurrentLeafNodes(self, nodes):
        "return the current leaf nodes"
        temp = {}
        for node in nodes:
            path = '/'.join(node.getPhysicalPath())
            if path not in temp:
                temp[path] = node
        leafs = []
        nodes = temp.items()
        nodes.sort(reverse=True)
        current = nodes[0][0]
        leafs.append(nodes[0][1])
        for path,node in nodes:
            if not current.startswith(path):
                current = path
                leafs.append(node)
        return [aq_base(leaf) for leaf in leafs]

    security.declarePrivate('resolveObjects')
    def resolveObjects(self,seq, menuFunc=None):
        "resolve all the objects in this list"
        temp = []

        for object in seq:
            cssClasses = ''
            queryDict = None
            otherAttributes = ''
            if isinstance(object, types.ListType):
                temp.append(self.resolveObjects(object, menuFunc))
            else:
                sort,object,selected = object

                try:
                    sort,text = sort
                except (TypeError, ValueError):
                    text = sort
                try:
                    path = object.absolute_url_path()
                except AttributeError:
                    path = object

                if  menuFunc is not None:
                    path, text, selected, cssClasses, queryDict, otherAttributes = menuFunc(object, path, text, selected, queryDict)

                temp.append((path, text,selected, cssClasses, queryDict, otherAttributes))
        return temp

    security.declarePrivate('traverseContainer')
    def traverseContainer(self, location=0, level=1, container=None, path=None, leafs=None, sortFunc=None, openAll=False):
        "return the items at this index recursively"
        temp = []

        folders = self.getContainers(container, sortFunc)

        cdoclist = self.getDocuments(container, leafs, sortFunc)
        scriptdata = self.getScriptData(container)
        seq = folders + cdoclist + scriptdata
        seq.sort()
        
        for sortvalue,object in seq:
            objects = []
            
            if openAll:
                selected = 0
            else:
                selected = aq_base(object) in path
            
            if getattr(object, 'meta_type', None) in self.folderTypes and location < level and (selected or openAll):
                results = self.traverseContainer(location+1, level, object, path, leafs, sortFunc, openAll)
                if results:
                    objects.extend(results)
            temp.append((sortvalue, object,selected))
            if objects:
                temp.append(objects)
        if not temp:
            temp = cdoclist
        return temp

    security.declarePrivate('getContainers')
    def getContainers(self, container, sortFunc=None):
        "return the containers for our current level"
        sorting = 0
        if sortFunc is not None or self.folderSortOn:
            sorting = 1
        sortFunc = sortFunc or self.getFolderSortValue
        
        if sorting:
            folders = []
            for folder in container.objectValues(self.folderTypes):
                try:
                    sort = sortFunc(folder)
                except Unauthorized:
                    sort = 0
                if sort:
                    folders.append(((sort, folder.title_or_id()), folder))
        else:
            folders = [(object.title_or_id(), object) for object in container.objectValues(self.folderTypes)]
        return folders

    security.declarePrivate('getScriptData')
    def getScriptData(self, container):
        "return any rendered script information for the current level"
        temp = []
        mergeScriptName = self.mergeScriptName
        if mergeScriptName and container.hasObject(mergeScriptName):
            script = container.restrictedTraverse(mergeScriptName, None)
            if script is not None:
                temp = list(script())
        return temp

    security.declarePrivate('getDocuments')
    def getDocuments(self, container, leafs, sortFunc=None):
        "get the documents for this level"
        #This test is trying to figure out if we are at a leaf node
        okayToShow = self.docsAsNodes or aq_base(container) in leafs
        if okayToShow and self.showCompoundDocs:
            return self.drawCompoundDocs(container, sortFunc=sortFunc)
        return []

    security.declarePrivate('drawCompoundDocs')
    def drawCompoundDocs(self, container, sortFunc=None):
        "Draw the compounddocs in this container"
        selected = set(self.getSelected())
                
        sorting = 0
        if sortFunc is not None or self.sortOn:
            sorting = 1

        sortFunc = sortFunc or self.getDocSortValue

        cdocs = container.objectValues(['CompoundDoc'])
        if selected:
            cdocs = (cdoc for cdoc in cdocs if cdoc.profile in selected)
        if sorting:
            temp = []
            for cdoc in cdocs:
                try:
                    sort = sortFunc(cdoc)
                except Unauthorized:
                    sort = 0
                if sort:
                    temp.append(((sort, cdoc.title_or_id()), cdoc))
        else:
            temp = [(cdoc.title_or_id(), cdoc) for cdoc in cdocs]
        return temp

    security.declarePrivate('getSortValue')
    def getSortValue(self, object, path):
        "Return the sort value for this object and None if nothing else can be found"
        if self.restrictedMode:
            sort = object.restrictedTraverse(path, None)
        else:
            sort = object.unrestrictedTraverse(path, None)
        if callable(sort):
            try:
                return sort(mode='view')
            except TypeError: #this covers the case where the sortable is a method or something that does not take mode
                return sort()
        return sort

    security.declarePrivate('getFolderSortValue')
    def getFolderSortValue(self, object):
        "Return the sort value for this object and None if nothing else can be found"
        return self.getSortValue(object, self.folderSortOn)

    security.declarePrivate('getDocSortValue')
    def getDocSortValue(self, object):
        "Return the sort value for this object and None if nothing else can be found"
        return self.getSortValue(object, self.sortOn)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append(self.editSingleConfig('renderer'))
        temp.append(NestedListURL.editRenderer(self.renderer, self))
        temp.append(self.editSingleConfig('baseURL'))
        temp.append(self.editSingleConfig('depth'))
        temp.append(self.editSingleConfig('sortOn'))
        temp.append(self.editSingleConfig('folderSortOn'))
        temp.append(self.editSingleConfig('showCompoundDocs'))
        temp.append(self.editSingleConfig('restrictedMode'))
        temp.append(self.editSingleConfig('renderScriptPath'))
        temp.append(self.editSingleConfig('mergeScriptName'))
        temp.append(self.editSingleConfig('docsAsNodes'))
        profiles = ['']
        profiles.extend(utility.getStoredProfileNames())
        selected = self.getSelected()
        temp.append('<p>%s</p>' % self.create_button('clear', 'Clear Selected Profile'))
        temp.append('<p>Profiles that are allowed:%s</p>' % self.multiselect('selected', profiles, selected, size=10))
        return ''.join(temp)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

Globals.InitializeClass(ContainerTraverse)
import register
register.registerClass(ContainerTraverse)