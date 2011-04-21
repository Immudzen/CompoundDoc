# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2009 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase
from AccessControl import ClassSecurityInfo
import Globals
from Acquisition import aq_base
import utility

picFormatScript = """traverse = pic.getCompoundDoc().restrictedTraverse
for imageFilter in %s:
    traverse(imageFilter).regenImages(pic)"""

imageFilterFormatScript = """pic = imageFilter.getCompoundDoc().restrictedTraverse('%s')
imageFilter.regenImages(pic)"""

def pathDifference(folder,  script):
    "find the path difference between these scripts"
    folderPath = '.'.join(folder.getPhysicalPath())
    scriptPath = '.'.join(script.getPhysicalPath())
    return scriptPath.replace(folderPath,  '')

class ControlConverter(ControlBase):
    "control panel for conversion items"

    meta_type = "ControlConverter"
    security = ClassSecurityInfo()
    control_title = 'Convert'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        cdoc = self.getCompoundDoc()
        temp = []
        temp.append('<div class="">')
        format = '<p>%s:%s</p>'
        temp.append(format % (self.input_text('scriptPath', ''), 'Path to Scripts Folder'))
        if cdoc.DisplayManager is not None:
            temp.append(format % (self.check_box('convertdisplay', ''), 'Convert Displays to Render'))

        if cdoc.CatalogManager is not None and not cdoc.CatalogManager.catalogScriptPath:
            temp.append(format % (self.check_box('convertcatalog', ''), 'Convert CatalogManager to use a script'))

        if cdoc.TabManager is not None and cdoc.TabManager.tabMapping is not None:
            temp.append(format % (self.check_box('converttabmanager', ''), 'Convert TabManager to use a script'))

        if cdoc.objectIds('TabView'):
            temp.append(format % (self.check_box('converttabview', ''), 'Convert TabViews to use a script'))

        if cdoc.objectIds('Picture'):
            temp.append(format % (self.check_box('convertPicNotifyToScript', ''), 'Have Pictures use scripts for notification'))

        if cdoc.EventManager is not None or cdoc.LinkManager is not None:
            temp.append(format % (self.check_box('convertLinkEventManager', ''), 'Remove empty Link and Event Managers'))

        if not cdoc.configDocPath:
            temp.append(format % (self.check_box('convertconfig', ''),'Create and setup a Config doc') )

        if self.getConfig('changeContextRenders') == 0 and self.displayMap is not None and not self.renderScriptLookupPath:
            temp.append(format % (self.check_box('convertRenderToScript', ''),'Convert renders to a render script') )

        temp.append(format % (self.check_box('removeConfigLocal', ''), 'Remove attributes that can be configured'))
        temp.append("<p>%s</p>" % self.submitChanges())
        if self.REQUEST.other.get('results', ''):
            temp += ["<p>%s</p>" % i for i in self.REQUEST.other['results']]
        temp.append('</div>')
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form=None):
        "This item is in charge of the profile/layout manager object"
        results = []
        if not self.profile and not self.isConfigDoc:
            self.REQUEST.other['results'] = ['Document must have a profile to be converted']
            return
        
        scriptPath = form.pop('scriptPath', '')
        if self.profile:
            folder = self.getProfileFolder(scriptPath)
        elif not self.profile and self.isConfigDoc:
            folder = self.getCompoundDocContainer().unrestrictedTraverse(scriptPath,  None)

        if form.pop('convertdisplay', None) is not None:
            results.extend(self.convertdisplays(folder))

        if form.pop('convertcatalog', None) is not None:
            results.extend(self.convertCatalog(folder))

        if form.pop('converttabmanager', None) is not None:
            results.extend(self.convertTabManager(folder))

        if form.pop('converttabview', None) is not None:
            results.extend(self.convertTabViews(folder))

        if form.pop('convertPicNotifyToScript', None) is not None:
            results.extend(self.convertPicNotifyToScript(folder))

        if form.pop('convertLinkEventManager', None) is not None:
            results.extend(self.convertLinkEventManager())

        if form.pop('convertconfig', None) is not None:
            results.extend(self.convertConfig(folder))

        if form.pop('removeConfigLocal', None) is not None:
            results.extend(self.removeConfigLocal())
            
        if form.pop('convertRenderToScript', None) is not None:
            results.extend(self.convertRenderToScript(folder))
        
        self.REQUEST.other['results'] = results

    security.declarePrivate('convertConfig')
    def convertConfig(self, folder):
        "convert this document to a config doc"
        temp = []
        cdoc = self.getCompoundDoc()
        folder = self.getCompoundDocContainer()
        name = cdoc.profile + 'C'
        configDoc = folder.manage_addProduct['CompoundDoc'].manage_addCompoundDoc(name, redir=0, returnObject=1)
        configDoc.changeProfile(doc=cdoc)
        configDoc.profile = ''
        configDoc.delObjects(['masterLocation'])
        cdoc.configDocPath = configDoc.absolute_url_path()
        cdoc.delObjects(['TabManager', 'displayMap', 'defaultDisplay', 'CatalogManager'])
        temp.append('Created a Config doc and set it up to be used')
        return temp

    security.declarePrivate('convertLinkEventManager')
    def convertLinkEventManager(self):
        "remove the LinkManager and EventManager if they are empty"
        temp = []
        cdoc = self.getCompoundDoc()
        if cdoc.EventManager is not None:
            cdoc.delObjects(['EventManager'])
            temp.append('Removed EventManager')
        if cdoc.LinkManager is not None and cdoc.LinkManager.lookup is None:
            cdoc.delObjects(['LinkManager'])
            temp.append('Removed LinkManager')
        return temp

    security.declarePrivate('removeConfigLocal')
    def removeConfigLocal(self):
        "convert this document to a config doc"
        temp = []
        cdoc = self.getCompoundDoc()
        meta_types = ('File', 'TextArea', 'SectionText', 'Selection', "EComControl", 'ActionRadio',
            'ListText', 'Picture', 'ImageFilter', 'Date', 'TabView','CalculatedValue')
        for obj in cdoc.objectValues(meta_types):
            obj.delObjects(obj.configurable)
        return temp

    security.declarePrivate('getProfileFolder')
    def getProfileFolder(self, scriptPath):
        "get profiles folder"
        scripts = self.getCompoundDocContainer().restrictedTraverse(scriptPath, None)
        if scripts is not None:
            try:
                profiles = scripts.profiles
            except AttributeError:
                scripts.manage_addProduct['OFSP'].manage_addFolder('profiles')
                profiles = scripts.profiles
            profileFolder = getattr(profiles, self.profile, None)
            
            if profileFolder is None:
                profiles.manage_addProduct['OFSP'].manage_addFolder(self.profile)
                profileFolder = getattr(profiles, self.profile)
            return profileFolder
            
    security.declarePrivate('convertCatalog')
    def convertCatalog(self, folder):
        "convert this document to a config doc"
        temp = []
        cdoc = self.getCompoundDoc()
        cm = cdoc.CatalogManager

        if cm.data is not None:
            scriptContents = ["return ["]
            for name in cm.data:
                scriptContents.append('doc.%s,' % name)
            scriptContents.append("]")
            scriptContents = '\n'.join(scriptContents)

            params = "doc"

            scriptname = 'catalogConfig'
            folder.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
            script = getattr(folder, scriptname)
            script.ZPythonScript_edit(params, scriptContents)
            
            cm.delObjects(['data'])
            cm.catalogScriptPath = script.absolute_url_path()


        temp.append('Convert CatalogManager to use a script')
        return temp

    security.declarePrivate('convertTabManager')
    def convertTabManager(self, folder):
        "convert this document to a config doc"
        temp = []
        cdoc = self.getCompoundDoc()
        tm = cdoc.TabManager

        if tm.tabMapping is not None:
            self.convertTab(folder, '', tm)
            
        temp.append('Convert CatalogManager to use a script')
        return temp

    security.declarePrivate('convertTabViews')
    def convertTabViews(self, folder):
        "convert this document to a config doc"
        temp = []
        cdoc = self.getCompoundDoc()
        
        for name, tab in cdoc.objectItems('TabView'):
            self.convertTab(folder, name, tab)
            
        temp.append('Convert TabViews to use a script')
        return temp

    security.declarePrivate('converTab')
    def convertTab(self, folder, name, tab):
        "convert this tab to a script"
        mapping = tab.tabMapping
        scriptContents = ["return ["]
        for tabName in tab.tabOrder:
            scriptContents.append('("%s","%s","",{}),' % (mapping[tabName],tabName))
        scriptContents.append("]")
        scriptContents = '\n'.join(scriptContents)

        params = "doc"

        scriptname = 'tabConfig%s' % name
        folder.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
        script = getattr(folder, scriptname)
        script.ZPythonScript_edit(params, scriptContents)
        
        tab.delObjects(['tabMapping', 'tabOrder'])
        tab.configScript = script.absolute_url_path()

    security.declarePrivate('convertPicNotifyToScript')
    def convertPicNotifyToScript(self, folder):
        "convert Pictures to use scripts"
        try:
            notify = folder.notify
        except AttributeError:
            folder.manage_addProduct['OFSP'].manage_addFolder('notify')
            notify = folder.notify
        cdoc = self.getCompoundDoc()

        temp = [repr(notify)]
        for pic in cdoc.objectValues(('Picture',)):
            temp.append(repr(pic))
            if 'observing' in pic.__dict__:
                scriptname = '%schangeNotification' % pic.getId()
                notify.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
                script = getattr(notify, scriptname)
                script.ZPythonScript_edit('pic', picFormatScript % repr(pic.observing))
                pic.scriptChangePath = script.absolute_url_path()

                for path in pic.observing:
                    imageFilter = cdoc.restrictedTraverse(path)
                    scriptname = '%schangeNotification' % imageFilter.getId()
                    notify.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
                    script = getattr(notify, scriptname)
                    script.ZPythonScript_edit('imageFilter', imageFilterFormatScript % imageFilter.location)
                    imageFilter.scriptChangePath = script.absolute_url_path()
                    imageFilter.delObjects(['location'])
                pic.delObjects(['observing'])
        temp.append('Updated all Pictures')
        return temp

    security.declarePrivate('convertdisplays')
    def convertdisplays(self, folder):
        "convert displays to renders"
        temp = []
        cdoc = self.getCompoundDoc()
        if not cdoc.profile:
            temp.append('Documents must have a profile to be converted')
            
        dm = self.getCompoundDoc().DisplayManager
        if folder is None:
            temp.append('No folder could be found at this path, make sure you point to the scripts folder for displays')
        if dm is not None:
            for displayName,display in dm.objectItems('Display'):
                filters = display.objectItems()
                if len(filters) == 1:
                    output = self.createRenderFromFilter(folder, displayName, display, filters[0])
                    temp.extend(output)
                else:
                    temp.append('Could not convert %s to a render because it has more then one filter' % displayName)
            if not dm.objectIds('Display'):
                cdoc.delObjects(['DisplayManager', 'masterLocation'])
                temp.append('No Displays left so we are deleting the DisplayManager')
        return temp

    def convertRenderToScript(self,  folder):
        "convert the renders to a script"
        cdoc = self.getCompoundDoc()
        if self.displayMap is not None and self.getConfig('changeContextRenders') == 0 and not self.renderScriptLookupPath:
            scriptname = 'renderScriptLookup'
            folder.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
            script = getattr(folder, scriptname)
            
            scriptContents = []
            conditional = 'if'
            defaultEdit= self.defaultDisplay.get('edit', None)
            defaultView= self.defaultDisplay.get('view', None)
            for renderName,  (header, body, footer) in self.displayMap.items():
                if renderName == defaultEdit:
                    orConditional = ' or display =="defaultEdit"'
                elif renderName == defaultView:
                    orConditional = ' or display == "defaultView"'
                else:
                    orConditional = ''
                condition = "%s display == '%s'%s:" % (conditional,  renderName,  orConditional)
                if header:
                    headerScriptPath = 'container%s' % pathDifference(folder,  folder.unrestrictedTraverse(header))
                else:
                    headerScriptPath = 'None'
                if body:
                    bodyScriptPath = 'container%s' % pathDifference(folder,  folder.unrestrictedTraverse(body))
                else:
                    bodyScriptPath = 'None'
                if footer:
                    footerScriptPath = 'container%s' % pathDifference(folder,  folder.unrestrictedTraverse(footer))
                else:
                    footerScriptPath = 'None'
                renders = '    return (%s, %s, %s)' % (headerScriptPath,  bodyScriptPath,  footerScriptPath)
                scriptContents.append(condition)
                scriptContents.append(renders)
                conditional = 'elif'
            scriptContents = '\n'.join(scriptContents)
            
            script.ZPythonScript_edit('doc, display', scriptContents)
            cdoc.renderScriptLookupPath = script.absolute_url_path()
            cdoc.displayMap = None
            cdoc.defaultDisplay = None
            return ["Converted Renders to a control script"]
        return ['Could not convert renders']

    def createRenderFromFilter(self, folder, displayName, display, displayFilter):
        "create a render from a filter"
        temp = []
        cdoc = self.getCompoundDoc()
        dm = cdoc.DisplayManager
        profile = cdoc.profile
        filterName, filterObj = displayFilter
        try:
            renders = folder.renders
        except AttributeError:
            folder.manage_addProduct['OFSP'].manage_addFolder('renders')
            renders = folder.renders
            
        temp.append('Working with folder %s' % renders.absolute_url_path())
        
        wrapper = lambda x: x
        if filterObj.codetype == 'DTML':
            wrapper = utility.dtmlToScript
        
        headerData = filterObj.wrapperHeader
        if headerData in ('return context.standard_html_header()', '<dtml-var standard_html_footer>'):
            headerPath = "standard_html_header"
        elif headerData == '':
            headerPath = ''
        else:
            scriptname = '%s_%s' % (displayName, 'header')
            renders.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
            script = getattr(renders, scriptname)
            script.ZPythonScript_edit('', wrapper(headerData))
            headerPath = script.absolute_url_path()
        
        bodyData = filterObj.code
        scriptname = displayName
        renders.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
        script = getattr(renders, scriptname)
        script.ZPythonScript_edit('', wrapper(bodyData))
        bodyPath = script.absolute_url_path()
        
        footerData = filterObj.wrapperFooter
        if footerData in ('return context.standard_html_footer()', '<dtml-var standard_html_footer>'):
            footerPath = "standard_html_footer"
        elif footerData == '':
            footerPath = ''
        else:
            scriptname = '%s_%s' % (displayName, 'footer')
            renders.manage_addProduct['PythonScripts'].manage_addPythonScript(scriptname)
            script = getattr(renders, scriptname)
            script.ZPythonScript_edit('', wrapper(footerData))
            footerPath = script.absolute_url_path()
        
        utility.addRender(cdoc, displayName, headerPath, bodyPath, footerPath)
        
        if display.usage == 'view' and displayName == dm.defaultView:
            utility.setDefaultView(cdoc, displayName)
            dm.delObjects(['defaultView'])
        elif display.usage == 'edit' and displayName == dm.defaultEdit:
            utility.setDefaultEdit(cdoc, displayName)
            dm.delObjects(['defaultEdit'])
        
        
        cdoc.DisplayManager.delObjects([displayName])
        temp.append('Converted %s to a render' % displayName)
        return temp

Globals.InitializeClass(ControlConverter)
