# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import Persistence
import Acquisition

from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser
from AccessControl import getSecurityManager

import utility

class ManageEditForm(Persistence.Persistent,Acquisition.Implicit):
    "Base for all container items abstract"

    meta_type = "ManageEditForm"
    security = ClassSecurityInfo()

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        if name:
            cdoc = self.getCompoundDoc()
            tab = cdoc.TabManager

            if tab is not None and tab.tabMapping is not None and tab.getTabActive():
                if name in tab.tabMapping:
                    displayName = tab.tabMapping[name]
                    self.REQUEST.other['editlayout'] = displayName
                    if self.displayMap is not None and self.displayMap.has_key(name):
                        mapping = self.displayMap[displayName]
                        self.setRenderREQUEST(displayName, mapping[0], mapping[2])
                    self.REQUEST.other['editname'] = name
                    return self

            configDoc = cdoc.getConfigDoc()
            configTab = None
            if configDoc is not None:
                configTab = configDoc.TabManager
            
            if configDoc is not None and configTab is not None and configTab.tabMapping is not None and configTab.getTabActive():
                if name in configTab.tabMapping:
                    displayName = configTab.tabMapping[name]
                    self.REQUEST.other['editlayout'] = displayName
                    if configDoc.displayMap is not None and configDoc.displayMap.has_key(name):
                        mapping = configDoc.displayMap[displayName]
                        self.setRenderREQUEST(displayName, mapping[0], mapping[2])
                    self.REQUEST.other['editname'] = name
                    return self

            lookup = self.getRenderScriptLookup()
            if lookup is not None:
                current_user = getSecurityManager().getUser()
                newSecurityManager(None, UnrestrictedUser('manager', '', ['Manager'], []))
                header, body, footer = lookup(self, name)
                newSecurityManager(None, current_user)
                if body is not None:
                    self.setRenderREQUESTScript(name, body, header, footer)
                    return self

            if self.displayMap is not None and self.displayMap.has_key(name):
                mapping = self.displayMap[name]
                self.setRenderREQUEST(name, mapping[0], mapping[2])
                return self
            
            if configDoc is not None and configDoc.displayMap is not None and configDoc.displayMap.has_key(name):
                mapping = configDoc.displayMap[name]
                self.setRenderREQUEST(name, mapping[0], mapping[2])
                return self
            
            if self.hasCompoundDisplayView(name):
                self.REQUEST.other['editlayout'] = name
                return self
            
            if hasattr(self, name):
                return getattr(self, name)
            else:
                return self

    def __call__(self, REQUEST, RESPONSE, **kw):
        "this is needed for deleting and other stuff need to make it work better"
        return self.index_html()

    security.declareProtected('View management screens', "index_html")
    def index_html(self):
        "Custom Object for Editing Objects to allow url rewriting"
        cdoc = self.getCompoundDoc()
        
        if self.REQUEST.form and not 'CompoundDocProcessed' in self.REQUEST.other and any(key.startswith('/') for key in self.REQUEST.form):
            cdoc.manage_edit()
            url = self.REQUEST.other.get('redirectTo', None)
            if url is not None:
                return self.REQUEST.RESPONSE.redirect(url)
        
        #must be called first so that vars can be set before we do tabs and other stuff
        bodyScript = self.REQUEST.other.get('renderScript', None)
        if bodyScript is not None:
            self.setDrawMode('edit')
            body = bodyScript(cdoc)
        else:
            body = self.edit(display=self.getDisplayName())
        
        temp = []
        temp.append(self.manage_page_header())
        temp.append(self.manage_tabs())
        
        tab = cdoc.TabManager
        if tab is not None:
            temp.append(tab.view())
        else:
            configDoc = cdoc.getConfigDoc()
            if configDoc is not None:
                tab = configDoc.TabManager
                if tab is not None:
                    temp.append(tab.view(doc=cdoc))
        
        temp.append(cdoc.begin_form())
        temp.append(cdoc.atomicSubmit())
        temp.append('<div>')
        temp.append(body)
        temp.append(self.manage_page_footer())
        #This is to catch changes that happen during the rendering of the page
        cdoc.processChanges()
        return self.gen_html(''.join(temp))

Globals.InitializeClass(ManageEditForm)
import register
register.registerClass(ManageEditForm)