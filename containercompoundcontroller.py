# -*- coding: utf-8 -*-
from objectcompoundcontroller import ObjectCompoundController

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

from OFS.CopySupport import cookie_path

class ContainerCompoundController(ObjectCompoundController):
    "uses a container to give access to a view of many compounddocs"

    meta_type = "ContainerCompoundController"
    security = ClassSecurityInfo()
    prepend = ''
    randomId = 0
    cdocName = ""
    folderSwap = 0
    allowAddRemove = 1
    autoNumber = 1
    sorton = ''
    cdocIsContainer = 0
    enableCutCopyPaste = 0
    enableShowOne = 0
    alternateDropDownAttributeName = ''
    folderType = 'Folder'
    drawControls = 1
    dropDownPath = ''
    autoType = ''
    cdocAutoAddTypes = ('timestamp', 'counter')


    folderTypes = ( ('Folder', 'Default Folder') , ('BTree', 'BTreeFolder2') )

    classConfig = {}
    classConfig['autoNumber'] = {'name':'Number the items on the page?', 'type': 'radio'}
    classConfig['cdocName'] = {'name':'Name of CompoundDoc if folder Swap is set:', 'type':'string'}
    classConfig['folderSwap'] = {'name':'Swap CompoundDoc name for Folder Name:', 'type': 'radio'}
    classConfig['allowAddRemove'] = {'name':'Allow Documents to be added and removed?:', 'type': 'radio'}
    classConfig['prepend'] = {'name':'Prepend Name:', 'type':'string'}
    classConfig['sorton'] = {'name':'Sort on attribute:', 'type':'string'}
    classConfig['cdocIsContainer'] = {'name':'Make this cdoc the container instead of its containing folder?:', 'type': 'radio'}
    classConfig['enableCutCopyPaste'] = {'name':'Enable Cut/Copy/Paste support?:', 'type': 'radio'}
    classConfig['enableShowOne'] = {'name':'Show only one document at a time:', 'type': 'radio'}
    classConfig['alternateDropDownAttributeName'] = {'name':'Name of an attribute to use for alternate sorting in the drop down:', 'type':'string'}
    classConfig['folderType'] = {'name':'Type of Folder to use', 'type': 'list', 'values': folderTypes}
    classConfig['drawControls'] = {'name':'Draw the individual document controls?:', 'type': 'radio'}
    classConfig['dropDownPath'] = {'name':'Path to the Drop Down Configuration:', 'type':'path'}
    classConfig['autoType'] = {'name':'Auto Cdoc Naming', 'type': 'list', 'values': ('',) + cdocAutoAddTypes}
        
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

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
        copysupport = form.pop('copysupport', None)
        if self.enableCutCopyPaste and copysupport is not None:
            container = self.getCompoundDocContainer().restrictedTraverse(form['tempEditFullPath'], None)
            self.handleCopySupport(copysupport, container)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        tempEditFullPath = form.get('tempEditFullPath', None)
        folder = None
        if tempEditFullPath is not None:
            folder = self.getCompoundDocContainer().restrictedTraverse(tempEditFullPath, None)
        if folder is None:
            folder = self.getEditFolder()
        if folder is not None and self.allowAddRemove:
            profile = self.editProfile
            if not profile and 'profile' in form:
                profile = form['profile']

            if 'add' in form:
                name = form.get('addName','')
                cdocName = folderSwap = None
                if self.folderSwap and self.cdocName:
                    cdocName = self.cdocName
                    folderSwap = 1
                autoType = self.getConfig('autoType')
                if name or autoType:
                    cdoc = folder.manage_addProduct['CompoundDoc'].manage_addCompoundDoc(name, profile=profile,
                      redir=0, prepend=self.prepend, cdocName=cdocName, folderCreate=folderSwap, returnObject=1, autoType=autoType)
                    
                    if (form.get('singleMode', None) or self.enableShowOne) and cdoc is not None:
                        self.setSelectedDocument(cdoc.getId())
            if 'del' in form and 'delName' in form and form['delName']:
                folder.manage_delObjects([form['delName'],])

    def handleCopySupport(self, form, container):
        "handle the copy and paste stuff"
        if form.pop('cut',None) and 'ids' in form and self.allowAddRemove:
            cp = container.manage_cutObjects(form['ids'])
            resp=self.REQUEST.RESPONSE
            resp.setCookie('__cp', cp, path='%s' % cookie_path(self.REQUEST))
            self.REQUEST['__cp'] = cp
        
        if form.pop('copy',None) and 'ids' in form:
            cp = container.manage_copyObjects(form['ids'])
            resp=self.REQUEST.RESPONSE
            resp.setCookie('__cp', cp, path='%s' % cookie_path(self.REQUEST))
            self.REQUEST['__cp'] = cp
        
        if form.pop('paste',None) and self.allowAddRemove and self.cb_dataValid(): #part of CopySupport
            container.manage_pasteObjects(self.REQUEST['__cp'])
    
    security.declareProtected("Access contents information", 'getEditFolder')
    def getEditFolder(self):
        "get the folder this object is using for editing"
        return self.getFolder('editFullPath')

    security.declareProtected("Access contents information", 'getViewFolder')
    def getViewFolder(self):
        "get the folder this object is using for viewing"
        return self.getFolder('viewFullPath')

    security.declarePrivate('getFolder')
    def getFolder(self,pathName):
        "get the folder we are supposed to be using and create it if it does not exist"
        path = getattr(self,pathName)
        cdocContainer = self.getContainer()
        folder = cdocContainer.restrictedTraverse(path,None)
        if folder is None:
            pathList = path.split('/')
            self.setObject(pathName, '/'.join(utility.drawFolderPath(pathList, cdocContainer, self.folderType)))
            folder = cdocContainer.restrictedTraverse(path,None)
        return folder

    security.declarePrivate('getContainer')
    def getContainer(self):
        "return the continer we are using as an origin"
        if self.cdocIsContainer:
            return self.getCompoundDoc()
        return self.getCompoundDocContainer()

    security.declareProtected('View management screens', 'edit')
    def edit(self, dropDownScript=None, loadFolder=1, drawMenu=1, container=None, profile=None, *args, **kw):
        "Inline edit view"
        temp = []

        folder = container or self.getFolder('editFullPath')
        if folder is not None:
            if loadFolder:
                objects = self.getObjectsToWorkWith(folder, profile)
                if dropDownScript or not self.dropDownPath:
                    self.sortObjects(objects, **kw)
            else:
                objects = tuple()
            
            if self.allowAddRemove:
                temp.extend(self.addRemoveDocument(folder, objects, profile))
            if self.enableCutCopyPaste:
                temp.extend(self.addCutCopyPasteControls())
            temp.extend(self.drawDocuments(objects, dropDownScript, drawMenu, folder, profile, **kw))
        return ''.join(temp)
    
    def addCutCopyPasteControls(self):
        "add the cut/copy/paste controls"
        temp = []
        if self.allowAddRemove:
            temp.append(self.create_button('cut', 'Cut', containers= ('copysupport',)))
        temp.append(self.create_button('copy', 'Copy', containers= ('copysupport',)))
        if self.cb_dataValid(): #part of CopySupport
            temp.append(self.create_button('paste', 'Paste', containers= ('copysupport',)))
        return temp
    
    security.declarePrivate('drawDocuments')
    def drawDocuments(self, objects, dropDownScript=None, drawMenu=1, container=None, profile=None, **kw):
        "draw these documents"
        drawOne = kw.get('selectOne', None)
        if drawOne is None:
            drawOne = self.enableShowOne
        if drawOne:
            return self.drawOne(objects, dropDownScript, container, profile, **kw)
        else:
            return self.drawMany(objects, drawMenu, container, profile, **kw)

    security.declarePrivate('drawOne')
    def drawOne(self, objects, dropDownScript=None, container=None, profile=None, **kw):
        "draw only one object for editing"
        temp = [self.input_hidden('tempEditFullPath', '/'.join(container.getPhysicalPath())), self.input_hidden('singleMode', 1)]

        control = '<div>%s %s</div>'
        showName = ''
        selectBox = ''

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
            if self.enableCutCopyPaste:
                selectBox = self.check_box('ids', name, containers = ('copysupport',), formType = 'list')
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
    def getSelectedDocument(self, container=None):
        "get the currently selected document"
        name = self.REQUEST.form.get('selectedDocument', None)
        if name is not None:
            container = container or self.getEditFolder()
            return getattr(container, name, None)

    security.declarePrivate('drawMany')
    def drawMany(self, objects, drawMenu=1, container=None, profile=None, **kw):
        "draw many of the compounddocs for editing"
        temp = [self.input_hidden('tempEditFullPath', '/'.join(container.getPhysicalPath())), self.input_hidden('singleMode', 0)]

        control = '<div id="%s">%s %s %s/%s %s</div>'
        controlNoNumber = '<div id="%s">%s %s %s</div>'
        showName = ''
        numberOfDocuments = len(objects)
        if drawMenu:
            jsMenu = self.getJSMenu(objects)
        else:
            jsMenu = ''
        selectBox = ''

        mymode = kw.get('docMode', None) or self.editMode
        view = kw.get('docRender', None) or self.editName
        path = self.editObjectPath
        profile = profile or self.editProfile
        drawid = self.editId
        drawControls = self.drawControls
        cdoc = self.getCompoundDoc()
        autoNumber = kw.get('autoNumber', None) or self.autoNumber
        
        for index,(name,doc) in enumerate(objects):
            if doc is not cdoc:
                if self.enableCutCopyPaste:
                    selectBox = self.check_box('ids', name, containers = ('copysupport',), formType = 'list')
                if drawid:
                    showName = name
                if drawControls:
                    if autoNumber:
                        temp.append(control % (name, selectBox, showName, index+1, numberOfDocuments, jsMenu))
                    else:
                        temp.append(controlNoNumber % (name, selectBox, showName, jsMenu))
                temp.append(self.embedRemoteObject(doc, path, mymode, view, profile, 0))
        return temp
    
    security.declarePrivate('addRemoveDocument')
    def addRemoveDocument(self, folder, objects, profile=None):
        "draw the add remove document interface"
        temp = []
        profile = profile or self.editProfile
        objects = [''] + [name for name,i in objects]
        
        temp.append(self.create_button('add', 'Add Document'))
        if not self.getConfig('autoType'):
            temp.append(self.input_text('addName', ''))
        
        if not profile:
            temp.append(self.option_select(utility.getStoredProfileNames(), 'profile', ['Default']))
        else:
            temp.append(self.input_hidden('profile', profile))
        doc = self.getSelectedDocument(folder)
        selected = None
        if doc is not None:
            selected = [doc.getId()]
        temp.append(self.option_select(objects, 'delName', selected=selected))
        temp.append(self.create_button('del', 'Delete Document'))
        return temp
                            
    security.declarePrivate('getMenu')
    def getMenu(self, documents, dropDownScript=None, **kw):
        "return the menu for these documents this is used in selectOne mode"
        temp = []
        selected = self.REQUEST.form.get('selectedDocument', None)
        if selected is not None:
            temp.append('<input type="hidden" name="selectedDocument:default" value="%s" >' % selected)
        
        dropDownPath, loadText, enableLoadButton = self.drawDropDownPathControls(documents, dropDownScript, **kw)
        if dropDownPath:
            temp.append(dropDownPath)
        else:
            temp.append(self.drawPrimaryDropDown(documents))
            temp.append(self.drawAlternateDropDown(documents))
 
        if loadText is None:
            loadText = 'Load Document'
        if enableLoadButton:
            temp.append(self.submitChanges(loadText))
        return ''.join(temp)

    security.declarePrivate('drawPrimaryDropDown')
    def drawPrimaryDropDown(self, docs):
        "draw the primary drop down"
        js = 'onchange="submit()"'
        seq = [(name, name) for (name, i) in docs]
        seq.insert(0, ('', 'Load Document') )
        return self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty', events=js)

    security.declarePrivate('drawAlternateDropDown')
    def drawAlternateDropDown(self, docs):
        "draw the alternate drop down"
        js = 'onchange="submit()"'
        alternate = self.alternateDropDownAttributeName
        if alternate:
            seq = ((getattr(i, alternate, ''), name) for (name, i) in docs)
            seq = ((method, name) for method, name in seq if callable(method))
            seq = ((method(mode='view'), name) for method, name in seq)
            seq = sorted(seq)
            seq = ((name, method) for method,name in seq)
            seq = list(seq)
            if seq:
                seq.insert(0, ('', 'Load Document') )
                return self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty',  events=js)
        return ''

    security.declarePrivate('drawDropDownPathControls')
    def drawDropDownPathControls(self, docs, dropDownScript=None, **kw):
        "draw the drop down path controls"
        dropDownPath = self.dropDownPath
        loadButtonText = None
        enableLoadButton = 1
        if dropDownPath or dropDownScript is not None:
            script = dropDownScript or self.getCompoundDoc().restrictedTraverse(dropDownPath, None)
            temp = []
            renderMenu = None
            if script is not None:
                dropDownSetup = script()
                dropDownSetup = iter(dropDownSetup)
                loadButtonText = dropDownSetup.next()
                renderMenu = dropDownSetup.next()
                for loadString, sortScript, renderScript, okScript, catalogScript in dropDownSetup:
                    temp.append(self.drawDropDown(docs, loadString, sortScript, renderScript, okScript, catalogScript, **kw))
            if renderMenu is not None:
                output = renderMenu(self.getCompoundDoc(), temp, loadButtonText)
                enableLoadButton = 0
            else:
                output = ''.join(temp)
            return output, loadButtonText, enableLoadButton
        return '', loadButtonText, enableLoadButton

    security.declarePrivate('drawDropDown')
    def drawDropDown(self, docs, loadString, sortScript, renderScript, okScript, catalogScript, **kw):
        "draw a drop down control for these docs sorted by sortPath and rendered with renderPath"
        js = 'onchange="submit()"'
        
        if catalogScript is not None:
            seq = utility.callOptional(catalogScript, self.getCompoundDoc(), kw.get('scriptArg', None))
        else:
            if okScript is not None:
                docs = utility.callOptional(okScript, docs, kw.get('scriptArg', None))
            seq = utility.callOptional(sortScript, docs, kw.get('scriptArg', None))
            seq.sort()
            seq = [(name, doc) for sort, name,doc in seq]
            seq = utility.callOptional(renderScript, seq, kw.get('scriptArg', None))
            seq = [(name, render) for render,name,doc in seq]
        loadString = loadString or 'Load Document'
        seq.insert(0, ('', loadString) )
        return self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty',  events=js)    
        
    security.declarePrivate('getJSMenu')
    def getJSMenu(self, documents):
        "return the javascript menu for these documents"
        numberOfDocuments = len(documents)
        format = '%s/%s&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%s'
        seq = [(name, format % (index+1, numberOfDocuments, name)) for index, (name, i) in enumerate(documents)]
        seq.insert(0, ('jump', 'Jump To Document') )
        temp = [self.option_select(seq, 'jump', selected=['jump'], events='onchange="jumpTo(this)"')]

        alternate = self.alternateDropDownAttributeName
        if alternate:
            seq = ((getattr(i, alternate, ''), name) for (name, i) in documents)
            seq = ((method, name) for method, name in seq if callable(method))
            seq = sorted((method(mode='view'), name) for method, name in seq)
            seq = [(name, method) for method,name in seq]
            if seq:
                seq.insert(0, ('jump', 'Jump To Document') )
                temp.append(self.option_select(seq, 'jump', selected=['jump'], events='onchange="jumpTo(this)"'))

        return ''.join(temp)
                        
    security.declarePrivate('getObjectsToWorkWith')
    def getObjectsToWorkWith(self, folder, profile=None):
        "get the objects we should work with from this folder"
        objects = folder.objectItems('CompoundDoc')
        profile = profile or self.editProfile
        
        if profile:
            objects = [(name,i) for name,i in objects if i.profile == profile]
        
        return list(objects)
             
    security.declarePrivate('sortObjects')         
    def sortObjects(self, objects, **kw):
        "sort these objects based on the sorton attribute"
        sorton = kw.get('sorton', None) or self.sorton
        sort = lambda o: None
        if sorton:
            def sort(o):
                cdoc = o[1]
                obj = getattr(cdoc, sorton, None)
                if obj is not None:
                    return obj(mode='view')
                  
        objects.sort(key=sort)
                    
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        temp = []

        mymode = self.viewMode
        view = self.viewName
        path = self.viewObjectPath
        profile = self.viewProfile
        drawid = self.viewId
        cdoc = self.getCompoundDoc()

        folder = self.getFolder('viewFullPath')
        if folder is not None:
            for i in folder.objectValues('CompoundDoc'):
                if i is not cdoc:
                    temp.append(self.embedRemoteObject(i, path, mymode, view, profile, drawid))
        return ''.join(temp)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeRandomId()
    
    security.declarePrivate('makeDataASequence')
    def removeRandomId(self):
        "remove the randomId and stick timestamp in autotype if randomId is set"
        if self.randomId:
            self.setObject('autoType', 'timestamp')
            self.delObjects(['randomId',])
    removeRandomId = utility.upgradeLimit(removeRandomId, 160)

Globals.InitializeClass(ContainerCompoundController)
import register
register.registerClass(ContainerCompoundController)