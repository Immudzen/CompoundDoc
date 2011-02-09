###########################################################################
#    Copyright (C) 2007 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from DateTime import DateTime

class ControlDefaultManager(ControlBase):
    "Manage the default objects for compounddoc to make them easier to add and remove"

    meta_type = "ControlDefaultManager"
    security = ClassSecurityInfo()
    control_title = 'Defaults'
    
    allowed = ('addCatalogManager','delCatalogManager','addTabManager','delTabManager','addDisplayManager', 'delDisplayManager',
            'addLinkManager', 'delLinkManager', 'addEventManager', 'delEventManager', 
            'adduserModificationTimeStamp', 'deluserModificationTimeStamp')
    
    defaults =(('CatalogManager', "Manages Catalogs"), 
            ('TabManager','Manages Tabs'),
            ('DisplayManager', 'Manages Displays'),
            ('LinkManager', 'Manages Linked Objects'),
            ('EventManager', "Manages The event system(don't think it works)"),
            ('userModificationTimeStamp', "Keeps the time a user last modified this document"),)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = ['<div class="">']
        creators = []
        cdoc = self.getCompoundDoc()
        for name,description in self.defaults:
            if getattr(cdoc, name) is None:
                creators.append([self.create_button('add%s' % name, 'Create %s' % name), description])
            else:
                creators.append([self.create_button('del%s' % name, 'Delete %s' % name), description])
        
        temp.append(self.createTable(creators))
        temp.append('</div>')
        return ''.join(temp)
        
        
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        for formName in self.allowed:
            addRemove = form.pop(formName, None)
            if addRemove is not None:
                getattr(self, formName)()
            
    def addCatalogManager(self):
        self.getCompoundDoc().addRegisteredObject('CatalogManager', 'CatalogManager')
        
    def delCatalogManager(self):
        self.getCompoundDoc().delObjects(['CatalogManager'])
        
    def addTabManager(self):
        self.getCompoundDoc().addRegisteredObject('TabManager', 'TabManager')
        
    def delTabManager(self):
        self.getCompoundDoc().delObjects(['TabManager'])
        
    def addDisplayManager(self):
        self.getCompoundDoc().addRegisteredObject('DisplayManager', 'DisplayManager')
        
    def delDisplayManager(self):
        self.getCompoundDoc().delObjects(['DisplayManager'])
        
    def addLinkManager(self):
        self.getCompoundDoc().addRegisteredObject('LinkManager', 'LinkManager')
        
    def delLinkManager(self):
        self.getCompoundDoc().delObjects(['LinkManager'])
   
    def addEventManager(self):
        self.getCompoundDoc().addRegisteredObject('EventManager', 'EventManager')
        
    def delEventManager(self):
        self.getCompoundDoc().delObjects(['EventManager'])
        
    def adduserModificationTimeStamp(self):
        self.getCompoundDoc().userModificationTimeStamp = DateTime()
        
    def deluserModificationTimeStamp(self):
        self.getCompoundDoc().delObjects(['userModificationTimeStamp'])        

Globals.InitializeClass(ControlDefaultManager)