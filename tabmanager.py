# -*- coding: utf-8 -*-
from basetab import BaseTab

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import nestedlisturl as NestedListURL
import utility

class TabManager(BaseTab):
    "TabManager manages multiple tabs in the edit interface"

    meta_type = "TabManager"
    security = ClassSecurityInfo()
    overwrite=1
    displayType = 'edit'
    active = 0
    
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''    

    security.declareProtected('View', 'view')
    def view(self, doc=None, renderer=None, tabScript=None):
        "Inline draw view"
        if doc is None:
            doc = self.getCompoundDoc()
        renderer = renderer or self.getConfig('renderer')
        if self.getTabActive():
            editname = self.getDisplayName()
            menu = []
            url = doc.absolute_url_path()
            for name,clickableName,cssClass,queryDict, query in self.getTabOrder(doc=doc, tabScript=tabScript):
                selected = 0
                if self.getTabMapping(name) == editname and utility.dictInQuery(queryDict, query):
                    selected = 1
                query = query.copy()
                query.update(queryDict)
                menu.append(('%s/manage_workspace/%s' % (url,name),clickableName,selected, cssClass, query, ''))
            cssClass = ' class="tabControl"' if renderer != 'Themeroller Tabs' else ''
            return '<div%s>%s</div>' % (cssClass, NestedListURL.listRenderer(renderer,menu, self.columns))
        return ""

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        format = '<div class="outline"><p>%s</p>%s</div>'
        return format  % (self.editSingleConfig('active'), BaseTab.edit(self))

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        BaseTab.classUpgrader(self)
        self.fixupTabOrder()
        self.fixupTabMapping()
        
    security.declarePrivate('fixupTabOrder')        
    def fixupTabOrder(self):
        "fixup the tabOrder attribute"
        if not self.tabOrder:
            self.setObject('tabOrder', None)
    fixupTabOrder = utility.upgradeLimit(fixupTabOrder, 141)
            
    security.declarePrivate('fixupTabMapping')        
    def fixupTabMapping(self):
        "fixup the tabMapping attribute"
        if not self.tabMapping:
            self.setObject('tabMapping', None)
    fixupTabMapping = utility.upgradeLimit(fixupTabMapping, 141)
    
Globals.InitializeClass(TabManager)
import register
register.registerClass(TabManager)