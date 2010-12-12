import basecatalog
import baseremoteembed
import zExceptions

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CatalogCompoundController(basecatalog.BaseCatalog, baseremoteembed.BaseRemoteEmbed):
    "Uses the Catalogs to give access to a view of many compounddocs"

    meta_type = "CatalogCompoundController"
    security = ClassSecurityInfo()

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        available = self.option_select(self.getAvailableCatalogs(), 'useCatalog', [self.useCatalog])
        format = "<div>Available Catalogs : %s</div>%s"
        temp = [
          ['', 'Edit', 'View'],
          ['Mode', self.drawEditMode(), self.drawViewMode()],
          ['Path', self.drawEditObjectPath(), self.drawViewObjectPath()],
          ['Name', self.drawEditName(), self.drawViewName()],
          ['Profile', self.drawEditProfile(), self.drawViewProfile()],
          ['Show Id', self.drawEditId(), self.drawViewId()]]
        return format % (available, self.createTable(temp))

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        mymode = self.editMode
        view = self.editName
        path = self.editObjectPath
        profile = self.editProfile
        drawid = self.editId

        #Fast abort so we don't dispatch to a bunch of other methods for something that can't draw
        if mymode not in self.modes:
            return ''

        temp = []
        for i in getattr(self, self.useCatalog)(meta_type='CompoundDoc'):
            try:
                object = i.getObject()
                if object is not None:
                    temp.append(self.embedRemoteObject(object, path, mymode, view, profile, drawid))
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                pass
        return ''.join(temp)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''            
            
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        mymode = self.viewMode
        view = self.viewName
        path = self.viewObjectPath
        profile = self.viewProfile
        drawid = self.viewId

        #Fast abort so we don't dispatch to a bunch of other methods for something that can't draw
        if mymode not in self.modes:
            return ''

        temp = []
        for i in getattr(self, self.useCatalog)(meta_type='CompoundDoc'):
            try:
                object = i.getObject()
                if object is not None:
                    temp.append(self.embedRemoteObject(object, path, mymode, view, profile, drawid))
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                pass
        return ''.join(temp)


Globals.InitializeClass(CatalogCompoundController)
import register
register.registerClass(CatalogCompoundController)