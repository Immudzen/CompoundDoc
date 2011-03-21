# -*- coding: utf-8 -*-
from objectcompoundcontroller import ObjectCompoundController

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility
import BTrees.OOBTree
from OFS.SimpleItem import SimpleItem

def dummyFunc(container, doc):
    "this is just a dummy function to have the same interface for the add/delete events"
    return None

class DummyClass(SimpleItem):
    
    security = ClassSecurityInfo()
    meta_type = "DummyClass"
    
    def __init__(self, name):
        self.id = name


class ObjectsController(ObjectCompoundController):
    "uses a container to give access to a view of many compounddocs"

    meta_type = "ObjectsController"
    security = ClassSecurityInfo()
    prepend = ''
    randomId = 0
    allowAddRemove = 1
    autoNumber = 1
    drawControls = 1
    objectStore = None
    typeStored = None
    scriptAdd = ''
    scriptDelete = ''

    allowedListTypes = ('InputText', 'TextArea', 'InputFloat', 
        'Date', 'File', 'InputInt', 'Money', 'Picture')

    classConfig = {}
    classConfig['autoNumber'] = {'name':'Number the items on the page?', 'type': 'radio'}
    classConfig['allowAddRemove'] = {'name':'Allow Documents to be added and removed?:', 'type': 'radio'}
    classConfig['prepend'] = {'name':'Prepend Name:', 'type':'string'}
    classConfig['drawControls'] = {'name':'Draw the individual document controls?:', 'type': 'radio'}
    classConfig['typeStored'] = {'name':'Type of Objects', 'type':'list', 'values': allowedListTypes}
    classConfig['scriptAdd'] = {'name':'Post addition script', 'type': 'path'}
    classConfig['scriptDelete'] = {'name':'Pre deletion script', 'type': 'path'}
        
    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        if name:
            if name == 'objectStore':
                name = self.REQUEST.TraversalRequestNameStack.pop()
                obj = self.objectStore.get(name,  None)
                if obj is not None:
                    dummy = DummyClass('objectStore').__of__(self)
                    return obj.__of__(dummy)
            else:
                obj = getattr(self, name, None)
                if obj is not None:
                    return obj        
        
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        return ''

    security.declarePrivate('getObjectStore')
    def getObjectStore(self):
        "get the object store for this object"
        if self.objectStore is None:
            self.setObject('objectStore', BTrees.OOBTree.OOBTree())
        return self.objectStore

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "handle the copy support before we do other stuff"
        if 'jump' in form:
            del form['jump']
        if 'selectedDocument' in form:
            selected = form['selectedDocument']
            for i in selected:
                if i:
                    selected = i
                    break
            else:
                selected = ''
            self.setSelectedDocument(selected)
        dummy = DummyClass('objectStore').__of__(self)
        for key, value in form.pop('objectStore',  {}).items():
            self.objectStore[key].__of__(dummy).manage_edit(dict=value)

    security.declarePrivate('getScriptAdd')
    def getScriptAdd(self):
        "get the catalogs from the script"
        return self.getScript(self.scriptAdd)
        
    security.declarePrivate('getScriptDelete')
    def getScriptDelete(self):
        "get the catalogs from the script"
        return self.getScript(self.scriptDelete)

    def getScript(self, path):
        "return the script for this path"
        script = None
        if path:
            script = self.getCompoundDocContainer().restrictedTraverse(path, None)
        if script is None:
            script = dummyFunc
        return script

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        container = self.getObjectStore()
        if container is not None and self.allowAddRemove:

            if 'add' in form:
                name = form.get('addName','')
                if name:
                    doc = self.createRegisteredObject(name, self.typeStored)
                    container[name] = doc
                    self.getScriptAdd()(self, doc.__of__(self))
                    if form.get('singleMode', None) and doc is not None:
                        self.setSelectedDocument(doc.getId())
            if 'del' in form and 'delName' in form and form['delName']:
                doc = container[form['delName']]
                self.getScriptDelete()(self, doc.__of__(self))
                del container[form['delName']]

    security.declareProtected('View management screens', 'edit')
    def edit(self, dropDownScript=None, drawMenu=1, *args, **kw):
        "Inline edit view"
        if self.typeStored is None:
            return ''
        temp = []

        dummy = DummyClass('objectStore').__of__(self)
        storage = self.getObjectStore()
        objects = [(name,doc.__of__(dummy)) for name,doc in storage.items()]
        self.sortObjects(objects, **kw)

        if self.allowAddRemove:
            temp.extend(self.addRemoveDocument(objects))
        temp.extend(self.drawDocuments(objects, dropDownScript, drawMenu, **kw))
        return ''.join(temp)
    
    security.declarePrivate('drawDocuments')
    def drawDocuments(self, objects, dropDownScript=None, drawMenu=1, **kw):
        "draw these documents"
        drawOne = kw.get('selectOne', None)
        if drawOne:
            return self.drawOne(objects, dropDownScript, **kw)
        else:
            return self.drawMany(objects, drawMenu, **kw)

    security.declarePrivate('drawOne')
    def drawOne(self, objects, dropDownScript=None, container=None, profile=None, **kw):
        "draw only one object for editing"
        temp = [self.input_hidden('singleMode', 1)]

        control = '<div>%s %s</div>'
        showName = ''
        selectBox = ''
        selectBoxFormat = '<input type="checkbox" name="ids:list" value="%s" >'

        mymode = kw.get('docMode', None) or self.editMode
        view = kw.get('docRender', None) or self.editName
        path = self.editObjectPath
        profile = profile or self.editProfile
        drawid = self.editId
        drawControls = self.drawControls
        cdoc = self.getCompoundDoc()

        doc = self.getSelectedDocument(container)
        temp.append('<div>%s</div>' % self.getMenu(objects, dropDownScript, **kw))
        if doc is not None and doc is not cdoc:
            name = doc.getId()
            if drawid:
                showName = name
            if drawControls:
                temp.append(control % (selectBox, showName))
            data = self.embedRemoteObject(doc, path, mymode, view, profile, 0)
            if data is not None:
                temp.append(data)
            else:
                temp.append('<p>For some reason the document you selected could not be shown. Please report this problem.</p>')
                
        return temp

    security.declarePrivate('getSelectedDocument')
    def getSelectedDocument(self):
        "get the currently selected document"
        name = self.REQUEST.form.get('selectedDocument', None)
        if name is not None:
            container = self.getObjectStore()
            return getattr(container, name, None)

    security.declarePrivate('drawMany')
    def drawMany(self, objects, drawMenu=1, container=None, profile=None, **kw):
        "draw many of the compounddocs for editing"
        temp = [self.input_hidden('singleMode', 0)]

        control = '<div id="%s">%s %s %s/%s %s</div>'
        controlNoNumber = '<div id="%s">%s %s %s</div>'
        showName = ''
        numberOfDocuments = len(objects)
        if drawMenu:
            jsMenu = self.getJSMenu(objects)
        else:
            jsMenu = ''
        selectBox = ''
        selectBoxFormat = '<input type="checkbox" name="ids:list" value="%s" >'

        drawid = self.editId
        drawControls = self.drawControls
        cdoc = self.getCompoundDoc()
        autoNumber = kw.get('autoNumber', None)
        
        for index,(name,doc) in enumerate(objects):
            if doc is not cdoc:
                if drawid:
                    showName = name
                if drawControls:
                    if autoNumber:
                        temp.append(control % (name, selectBox, showName, index+1, numberOfDocuments, jsMenu))
                    else:
                        temp.append(controlNoNumber % (name, selectBox, showName, jsMenu))
                temp.append(doc(mode='edit'))
        return temp
    
    security.declarePrivate('addRemoveDocument')
    def addRemoveDocument(self, objects):
        "draw the add remove document interface"
        temp = []
        objects = [''] + [name for name,i in objects]

        temp.append(self.create_button('add', 'Add %s' % self.typeStored))
        temp.append(self.input_text('addName', ''))

        doc = self.getSelectedDocument()
        selected = None
        if doc is not None:
            selected = [doc.getId()]
        temp.append(self.option_select(objects, 'delName', selected=selected))
        temp.append(self.create_button('del', 'Delete %s' % self.typeStored))
        return temp
   
    security.declarePrivate('getJSMenu')
    def getJSMenu(self, documents):
        "return the javascript menu for these documents"
        numberOfDocuments = len(documents)
        format = '%s/%s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s'
        seq = [(name, format % (index+1, numberOfDocuments, name)) for index, (name, i) in enumerate(documents)]
        seq.insert(0, ('jump', 'Jump To Document') )
        temp = [self.option_select(seq, 'jump', selected=['jump'], events='onchange="jumpTo(this)"')]
        return ''.join(temp)
        
    security.declarePrivate('sortObjects')         
    def sortObjects(self, objects, **kw):
        "sort these objects based on the sorton attribute"
        sorton = kw.get('sorton', None)
        if sorton:
            objects.sort(key=operator.attrgetter(sorton))
        objects.sort()

Globals.InitializeClass(ObjectsController)
import register
register.registerClass(ObjectsController)
