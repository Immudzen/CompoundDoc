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

Globals.InitializeClass(ObjectCompoundController)
import register
register.registerClass(ObjectCompoundController)
