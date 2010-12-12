from objectcompoundcontroller import ObjectCompoundController

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ObjectsCustomController(ObjectCompoundController):
    "uses a container to give access to a view of many compounddocs"

    meta_type = "ObjectsCustomController"
    security = ClassSecurityInfo()
    viewDTMLHeader = ''
    viewDTMLFooter = ''
    editDTMLHeader = ''
    editDTMLFooter = ''
    
    classConfig = {}
    classConfig['viewDTMLHeader'] = {'name':'DTML View Header:', 'type':'text'}
    classConfig['viewDTMLFooter'] = {'name':'DTML View Footer:', 'type':'text'}
    classConfig['editDTMLHeader'] = {'name':'DTML Edit Header:', 'type':'text'}
    classConfig['editDTMLFooter'] = {'name':'DTML Edit Footer:', 'type':'text'}
    
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []

        mymode = self.editMode
        view = self.editName
        path = self.editObjectPath
        profile = self.editProfile
        drawid = self.editId
        cdoc = self.getCompoundDoc()
        editHeader = self.editDTMLHeader
        editFooter = self.editDTMLFooter


        try:
            object = self.getCompoundDoc().restrictedTraverse(self.editFullPath)
        except KeyError:
            temp.append('<p>No object can be found at %s location.</p>' % self.editFullPath)
            object = None
        if object and hasattr(object, 'getUseObjects'):
            for i in object.getUseObjects():
                if i is not cdoc:
                    temp.append(self.gen_html(editHeader))
                    temp.append(self.embedRemoteObject(i, path, mymode, view, profile, drawid))
                    temp.append(self.gen_html(editFooter))
        return ''.join(temp)

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
        viewHeader = self.viewDTMLHeader
        viewFooter = self.viewDTMLFooter

        try:
            object = self.getCompoundDoc().restrictedTraverse(self.viewFullPath)
        except KeyError:
            temp.append('<p>No object can be found at %s location.</p>' % self.viewFullPath)
            object = None

        if object and hasattr(object, 'getUseObjects'):
            for i in object.getUseObjects():
                if i is not cdoc:
                    temp.append(viewHeader)
                    temp.append(self.embedRemoteObject(i, path, mymode, view, profile, drawid))
                    temp.append(viewFooter)
        return ''.join(temp)


Globals.InitializeClass(ObjectsCustomController)
import register
register.registerClass(ObjectsCustomController)