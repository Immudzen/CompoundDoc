# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import nestedlisturl as NestedListURL
import utility

class BaseTab(Base):
    "Basic item to make multi tabbed interfaces"

    meta_type = "BaseTab"
    security = ClassSecurityInfo()
    overwrite=1
    displayType = 'edit'
    tabMapping = None
    tabOrder = None
    renderer = 'Horizontal'
    columns = 0
    configScript = ''
    active = 1

    classConfig = {}
    classConfig['renderer'] = {'name':'Rendering Output', 'type':'list', 'values': NestedListURL.lookup.keys()}
    classConfig['configScript'] = {'name':'Path to script configuration for tabs', 'type':'path'}
    classConfig['active'] = {'name':'Activate the tab manager?', 'type': 'radio'}

    configurable = ('configScript', 'active', 'renderer', 'tabOrder', 'tabMapping')

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

    security.declarePrivate('getTabMapping')
    def getTabMapping(self, name):
        "get the tabMapping from this name"
        if self.tabMapping is not None:
            return self.tabMapping.get(name, name)
        return name

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        typeformat = '<div>Id: %s Display:%s</div>'
        cdoc = self.getCompoundDoc()
        displays = ['']
        if cdoc.DisplayManager is not None:
            displays.extend(cdoc.DisplayManager.displayUsage(self.displayType))
        if cdoc.displayMap is not None:
            displays.extend(cdoc.displayMap.keys())
        
        tabOrder = self.tabOrder
        if tabOrder is None:
            tabOrder = []
        
        neededEntries = len(tabOrder) + 1
        temp.append(self.editSingleConfig('renderer'))
        temp.append(NestedListURL.editRenderer(self.renderer, self))
        
        tabMapping = self.tabMapping
        if tabMapping is None:
            tabMapping = {}
        
        for index in xrange(neededEntries):
            try:
                nameValue = tabOrder[index]
                displayValue = tabMapping[nameValue]
            except (IndexError,KeyError):
                nameValue = ''
                displayValue = ''

            temp.append(typeformat % (self.input_text('name', nameValue, containers=('tabMapping', str(index))),
            self.option_select(displays, 'display', [displayValue],  containers=('tabMapping', str(index)))))
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        tabMapping = dict.pop('tabMapping', None)
        if tabMapping is not None:
            temp = {}
            for i, j in tabMapping.items():
                temp[int(i)] = j
            temp = ((dictionary['name'].strip(), dictionary['display'].strip()) for index, dictionary in sorted(temp.iteritems()))
            cleaned = [(name, display) for name, display in temp if name and display]
            if len(cleaned):
                tabOrder = [name for name, value in cleaned]
                self.setObject('tabOrder', tabOrder)
                temp = {}
                for name, display in cleaned:
                    temp[name] = display
                self.setObject('tabMapping', temp)
            else:
                self.delObjects(('tabOrder', 'tabMapping'))

    security.declarePrivate('getTabOrder')
    def getTabOrder(self, doc=None, tabScript=None):
        "get the tabOrder list structure"
        doc = doc or self.getCompoundDoc()
        query = utility.getQueryDict(self.REQUEST.environ.get('QUERY_STRING', ''))
        configScript = tabScript or self.getConfigScript()
        if configScript is not None:
            return self.correctScriptTabOrder(configScript(doc), query)
        
        tabOrder = self.getConfig('tabOrder')
        if tabOrder is not None:
            return [(name,name, '', {}, query) for name in tabOrder]
        
        return []

    security.declarePrivate('correctScriptTabOrder')
    def correctScriptTabOrder(self, seq, query):
        "correct the script tabOrder to account for the dictionary that can be used to pass in vars"
        temp = []
        for item in seq:
            try:
                url,link,cssClasses = item
                queryDict = {}
            except ValueError:
                url,link,cssClasses,queryDict = item
            temp.append([url,link,cssClasses,queryDict, query])
        return temp

    security.declarePrivate('getConfigScript')
    def getConfigScript(self):
        "return the config script object"
        configScript = self.getConfig('configScript')
        script = None
        if configScript:
            script = self.getCompoundDocContainer().restrictedTraverse(configScript, None)
        return script

    security.declarePrivate('getTabActive')
    def getTabActive(self):
        "return True only if we are set as active and we have data"
        return self.getConfig('active') and (self.getConfig('tabMapping') is not None or self.getConfig('configScript'))

    security.declarePrivate('beforeProfileLoad')
    def beforeProfileLoad(self):
        "run this action before loading the object with profile information"
        self.performUpdate()

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.fixTabOrder()

    security.declarePrivate('fixTabOrder')
    def fixTabOrder(self):
        "fix the tabOrder object"
        if not self.hasObject('tabOrder'):
            if self.tabMapping is not None:
                keys = sorted(self.tabMapping.keys())
            else:
                keys = None
            self.setObject('tabOrder', keys)
    fixTabOrder = utility.upgradeLimit(fixTabOrder, 141)
            

Globals.InitializeClass(BaseTab)
