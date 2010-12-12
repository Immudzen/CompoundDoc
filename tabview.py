# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from basetab import BaseTab

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import nestedlisturl as NestedListURL
import utility
import os.path

class TabView(BaseTab):
    "TabView can make multi tabbed view interfaces"

    meta_type = "TabView"
    security = ClassSecurityInfo()
    overwrite=0
    displayType = 'view'

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''
    
    security.declareProtected('View', 'view')
    def view(self, doc=None, tabScript=None, columns=None):
        "Inline draw view"
        if columns is None:
            columns = self.columns
        
        displayName = self.getDisplayName()
        menu = []
        doc = doc or self.getCompoundDoc()
        url = doc.absolute_url_path()
        
        tabOrder = self.getTabOrder(doc=doc, tabScript=tabScript)
        tabMapping = self.getConfig('tabMapping')
        if tabMapping is not None:
            tabOrder = [(tabMapping[name], clickableName, cssClass, queryDict, query) for name, clickableName, cssClass, queryDict, query in tabOrder]
        
        for name,clickableName,cssClass, queryDict, query in tabOrder:
            selected = 0
            if name == displayName and utility.dictInQuery(queryDict, query):
                selected = 1
            query = query.copy()
            query.update(queryDict)
            menu.append((os.path.join(url,name),clickableName,selected, cssClass, query, ''))
        return NestedListURL.listRenderer(self.getConfig('renderer'),menu, columns)

Globals.InitializeClass(TabView)
import register
register.registerClass(TabView)
