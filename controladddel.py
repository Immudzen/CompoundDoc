#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlAddDel(ControlBase):
    "control panel for addition/deletion in the control panel"

    meta_type = "ControlAddDel"
    security = ClassSecurityInfo()
    control_title = 'AddDel'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        format = '<div class="configDataArea"><div>%s</div><div style="position:absolute; left:20em; top:0">%s</div></div>'
        return format % (self.addObjectsEdit(), self.deleteObjectsEdit())
          
    security.declarePrivate('deleteObjectsEdit')
    def deleteObjectsEdit(self, allowableTypes=None):
        "This is the form elements for deleting objects"
        cdoc = self.getCompoundDoc()
        if allowableTypes is None:
            allowableTypes = cdoc.restrictedUserObject()
        idsFound = cdoc.objectIdsWithMetaType(allowableTypes)
        if not idsFound:
            return ''
        if cdoc.hasObject("noremove"):
            noremove = cdoc.noremove()
            idsRemove = [(name, '%s (%s)' % (name, meta_type)) for name,meta_type in idsFound if name not in noremove]
        idsRemove.sort()
        idsRemove.insert(0, '')
        buttonName = cdoc.getDeleteButtonName(allowableTypes)
        selection = cdoc.option_select(idsRemove, 'removemeSeq', multiple=1, size=25, dataType='list')
        return '<p>%s</p><p>%s</p>' % (cdoc.create_button('Del', buttonName), selection)
        
    security.declarePrivate('addObjectsEdit')
    def addObjectsEdit(self, allowableTypes=None, autoId=None, autoType=None):
        "This is the form elements for adding objects"
        cdoc = self.getCompoundDoc()
        if allowableTypes is None:
            allowableTypes = cdoc.restrictedUserObject()
        buttonName = cdoc.getAddButtonName(allowableTypes)
        selection = ''
        if autoType is None:
            if len(allowableTypes) == 1:
                selection = cdoc.input_hidden('add_me_type', allowableTypes[0])
            else:
                selection = cdoc.option_select(allowableTypes, 'add_me_type', size=25)
        inputText = ''
        if autoId is None:
            inputText = cdoc.input_text('add_me_name', '')
        return '<p>%s</p><p>%s</p><p>%s</p>' % (cdoc.create_button('Add', buttonName), inputText, selection)

Globals.InitializeClass(ControlAddDel)
