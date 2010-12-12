###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
 #For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class MixObjectManager:
    "this is a mixin class to creat the forms and form processing needed to handle adding and removing objects"

    meta_type = "MixObjectManager"
    security = ClassSecurityInfo()

    security.declarePrivate('add_delete_objects_edit')
    def addDeleteObjectsEdit(self):
        "This is the form elements for adding and deleting objects without the form wrapper"
        return '%s %s' % (self.addObjectsEdit(), self.deleteObjectsEdit())

    security.declarePrivate('deleteObjectsEdit')
    def deleteObjectsEdit(self, allowableTypes=None):
        "This is the form elements for deleting objects"
        if allowableTypes is None:
            allowableTypes = self.restrictedUserObject()
        idsFound = self.getDeletionNames(allowableTypes)
        if not idsFound:
            return ''
        if hasattr(self, "noremove"):
            noremove = self.noremove()
            idsRemove = [i for i in idsFound if i not in noremove]
        idsRemove.sort()
        idsRemove.insert(0, '')
        buttonName = self.getDeleteButtonName(allowableTypes)
        return self.create_button('Del', buttonName) + self.option_select(idsRemove, 'removeme')

    security.declarePrivate('getDeleteButtonName')
    def getDeleteButtonName(self, allowableTypes):
        "get the text for the delete button"
        buttonName = 'Delete'
        if len(allowableTypes) == 1:
            buttonName = 'Delete %s' % allowableTypes[0]
        return buttonName

    security.declarePrivate('getAddButtonName')
    def getAddButtonName(self, allowableTypes):
        "get the text for the add button"
        buttonName = 'Add'
        if len(allowableTypes) == 1:
            buttonName = 'Add %s' % allowableTypes[0]
        return buttonName

    security.declarePrivate('getDeletionNames')
    def getDeletionNames(self, allowableTypes):
        "return the names are should be used for deletion"
        return self.objectIds(allowableTypes)

    security.declarePrivate('addObjectsEdit')
    def addObjectsEdit(self, allowableTypes=None, autoId=None, autoType=None):
        "This is the form elements for adding objects"
        if allowableTypes is None:
            allowableTypes = self.restrictedUserObject()
        buttonName = self.getAddButtonName(allowableTypes)
        selection = ''
        if autoType is None:
            if len(allowableTypes) == 1:
                selection = self.input_hidden('add_me_type', allowableTypes[0])
            else:
                selection = self.option_select(allowableTypes, 'add_me_type')
        inputText = ''
        if autoId is None:
            inputText = self.input_text('add_me_name', '')
        return self.create_button('Add', buttonName) + selection +inputText

    security.declarePrivate('add_delete_objects')
    def add_delete_objects(self, form):
        "Add new objects to the existing object"
        if form.get('removeme', "") != "":
            self.deleteRegisteredObject(form['removeme'], self.noremove())
        if form.get('removemeSeq', "") != "":
            for name in form.get('removemeSeq'):
                noremove = self.noremove()
                self.deleteRegisteredObject(name, noremove)
        if form.get('add_me_name',"") != "":
            self.updateRegisteredObject(form['add_me_name'], form['add_me_type'])

Globals.InitializeClass(MixObjectManager)
