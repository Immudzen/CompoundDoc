# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlCatalogManager(ControlBase):
    "Input text class"

    meta_type = "ControlCatalogManager"
    security = ClassSecurityInfo()
    control_title = 'Catalog'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div class="">']
        catalogManager = self.getCompoundDoc().CatalogManager
        if catalogManager is not None:
            temp.append('<div>')
            temp.append(self.submitChanges())
            temp.append('</div>')
            temp.append(catalogManager.edit())
        else:
            temp.append(self.create_button('addCatalogManager', 'Create CatalogManager'))
        temp.append('</div>')
        return ''.join(temp)
        
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        addCatalogManager = form.get('addCatalogManager', None)
        if addCatalogManager is not None:
            self.getCompoundDoc().addRegisteredObject('CatalogManager', 'CatalogManager')

Globals.InitializeClass(ControlCatalogManager)
