import baseremoteembed

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ObjectCompoundController(baseremoteembed.BaseRemoteEmbed):
    "Uses the Catalogs to give access to a view of many compounddocs"

    meta_type = "ObjectCompoundController"
    security = ClassSecurityInfo()
    viewFullPath = ''
    editFullPath = ''

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''   
    
    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        temp = [
          ['','Edit','View'],
          ['Path to Object',self.drawEditFullPath(),self.drawViewFullPath()],
          ['Mode',self.drawEditMode(),self.drawViewMode()],
          ['Path',self.drawEditObjectPath(),self.drawViewObjectPath()],
          ['Name',self.drawEditName(),self.drawViewName()],
          ['Profile',self.drawEditProfile(),self.drawViewProfile()],
          ['Show Id',self.drawEditId(),self.drawViewId()]]
        return self.createTable(temp)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        object = None
        try:
            if self.editFullPath:
                object = self.getCompoundDocContainer().restrictedTraverse(self.editFullPath)
            elif self.editObjectPath:
                object = self.getCompoundDoc()
        except KeyError:
            return '<p>No object can be found at %s location.</p>' % self.editFullPath
        if object is not None:
            return self.embedRemoteObject(object, self.editObjectPath, self.editMode,
              self.editName, self.editProfile, self.editId)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        object = None
        try:
            if self.viewFullPath:
                object = self.getCompoundDocContainer().restrictedTraverse(self.viewFullPath)
            elif self.viewObjectPath:
                object = self.getCompoundDoc()
        except KeyError:
            object = None
        if object:
            return self.embedRemoteObject(object, self.viewObjectPath, self.viewMode, self.viewName,
              self.viewProfile, self.viewId)

    security.declarePrivate('drawEditFullPath')
    def drawEditFullPath(self, config=None):
        "draw the edit interface for FullPath"
        return self.input_text('editFullPath', self.editFullPath)

    security.declarePrivate('drawViewFullPath')
    def drawViewFullPath(self, config=None):
        "draw the edit interface for viewFullPath"
        return self.input_text('viewFullPath', self.viewFullPath)

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
        return ''

Globals.InitializeClass(ObjectCompoundController)
import register
register.registerClass(ObjectCompoundController)
