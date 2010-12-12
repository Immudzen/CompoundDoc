from objectcompoundcontroller import ObjectCompoundController

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ObjectsCompoundController(ObjectCompoundController):
    "uses a container to give access to a view of many compounddocs"

    meta_type = "ObjectsCompoundController"
    security = ClassSecurityInfo()

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []

        mymode = self.editMode
        view = self.editName
        path = self.editObjectPath
        profile = self.editProfile
        drawid = self.editId

        try:
            object = self.getCompoundDoc().restrictedTraverse(self.editFullPath)
        except KeyError:
            temp.append('<p>No object can be found at %s location.</p>' % self.editFullPath)
            object = None
        if object is not None:
            getUseObjects = getattr(object, 'getUseObjects', None)
            if getUseObjects is not None:
                for i in getUseObjects():
                    temp.append(self.embedRemoteObject(i, path, mymode, view, profile, drawid))

        return ''.join(temp)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''           
            
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        temp = []

        mymode = self.viewMode
        view = self.viewName
        path = self.viewObjectPath
        profile = self.viewProfile
        drawid = self.viewId

        try:
            object = self.getCompoundDoc().restrictedTraverse(self.viewFullPath)
        except KeyError:
            temp.append('<p>No object can be found at %s location.</p>' % self.viewFullPath)
            object = None

        if object is not None:
            getUseObjects = getattr(object, 'getUseObjects', None)
            if getUseObjects is not None:
                for i in getUseObjects():
                    temp.append(self.embedRemoteObject(i, path, mymode, view, profile, drawid))
        return ''.join(temp)

Globals.InitializeClass(ObjectsCompoundController)
import register
register.registerClass(ObjectsCompoundController)