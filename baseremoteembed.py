#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject
import mixremoteembed
import utility

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class BaseRemoteEmbed(UserObject, mixremoteembed.MixRemoteEmbed):
    "Base for all objects that embed remote objects"

    meta_type = "BaseRemoteEmbed"
    security = ClassSecurityInfo()
    overwrite=1

    viewMode = ''
    viewObjectPath = ''
    viewName = ''
    viewProfile = ''
    editMode = ''
    editObjectPath = ''
    editName = ''
    editProfile = ''
    viewId = 0
    editId = 0

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

    security.declarePrivate('drawEditProfile')
    def drawEditProfile(self):
        "draw the edit interface for editProfile and append it to the list"
        temp = [''] + utility.getStoredProfileNames()
        return self.option_select(temp, 'editProfile', [self.editProfile])

    security.declarePrivate('drawEditName')
    def drawEditName(self):
        "draw the edit interface for editName and append it to the list"
        return self.input_text('editName',  self.editName)

    security.declarePrivate('drawEditObjectPath')
    def drawEditObjectPath(self):
        "draw the edit interface for editObjectPath and append it to the list"
        return self.input_text('editObjectPath',  self.editObjectPath)

    security.declarePrivate('drawEditMode')
    def drawEditMode(self):
        "draw the edit interface for EditMode and append it to the list"
        temp = [''] + list(self.modes)
        return self.option_select(temp, 'editMode', [self.editMode])

    security.declarePrivate('drawViewProfile')
    def drawViewProfile(self):
        "draw the edit interface for viewProfile and append it to the list"
        temp = [''] + utility.getStoredProfileNames()
        return self.option_select(temp, 'viewProfile', [self.viewProfile])

    security.declarePrivate('drawViewName')
    def drawViewName(self):
        "draw the edit interface for viewName and append it to the list"
        return self.input_text('viewName',  self.viewName)

    security.declarePrivate('drawViewObjectPath')
    def drawViewObjectPath(self):
        "draw the edit interface for viewObjectPath and append it to the list"
        return self.input_text('viewObjectPath',  self.viewObjectPath)

    security.declarePrivate('drawViewMode')
    def drawViewMode(self):
        "draw the edit interface for viewMode and append it to the list"
        temp = [''] + list(self.modes)
        return self.option_select(temp, 'viewMode', [self.viewMode])

    security.declarePrivate('drawEditId')
    def drawEditId(self):
        "draw the edit interface for editId"
        return self.true_false('editId', self.editId, 0)

    security.declarePrivate('drawViewId')
    def drawViewId(self):
        "draw the edit interface for viewId"
        return self.true_false('viewId', self.viewId, 0)

Globals.InitializeClass(BaseRemoteEmbed)
