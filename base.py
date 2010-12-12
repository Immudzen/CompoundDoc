# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from getset import GetSet
from widgets import Widgets
import baseobject
import utility
import mixobjectloadstore
import mixconfigobject
import mixupgrader
import mixobserver
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from mixaddregistered import MixAddRegistered
from mixobjectmanager import MixObjectManager
from AccessControl import getSecurityManager
from AccessControl import Unauthorized

from Acquisition import aq_base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import manageEditForm
import urllib

import os.path

class Base(baseobject.BaseObject,
  GetSet,
  Widgets,
  mixupgrader.MixUpgrader,
  mixobjectloadstore.MixObjectLoadStore,
  mixconfigobject.MixConfigObject,
  mixobserver.MixObserver,
  MixAddRegistered,
  MixObjectManager,
  SimpleItem):
    "Abstract Base"

    classVersion = 163  #run upgrader scripts 160
    classUpdateVersion = 122  #add attributes
    overwrite = 0
    updateAlways = 0

    meta_type = "Base"
    security = ClassSecurityInfo()
    
    drawDict = {'view':'view', 'edit':'edit', 'config':'config', 'debug':'debugObject'}
    
    manage = manage_main = manage_edit_form = manage_workspace = manageEditForm.ManageEditForm('manage_edit_form')
    attr_notified = None
    
    manage_options = (
      {'label': 'Edit', 'action': 'manage_workspace'},
      {'label': 'View', 'action': 'index_html'},
      {'label': 'Inline', 'action': 'inlineView'},)+ SimpleItem.manage_options

    security.declareProtected("Access contents information", 'objectItems')
    objectItems = ObjectManager.objectItems

    security.declareProtected("Access contents information", 'objectValues')
    objectValues = ObjectManager.objectValues

    security.declareProtected("Access contents information", 'objectIds')
    objectIds = ObjectManager.objectIds
    _getOb = ObjectManager._getOb

    security.declareProtected("Access contents information", 'objectIdsWithMetaType')
    def objectIdsWithMetaType(self, spec=None):
        # Returns a list of subobject ids of the current object.
        # If 'spec' is specified, returns objects whose meta_type
        # matches 'spec'.
        if spec is not None:
            if type(spec)==type('s'):
                spec=[spec]
            set = ((obj['id'], obj['meta_type']) for obj in self._objects)
            return [(name, meta_type) for name,meta_type in set if meta_type in spec]
        return [(obj['id'], obj['meta_type'])  for obj in self._objects]

    security.declareProtected('Change permissions', 'manage_access')
    security.declareProtected('Take ownership', 'manage_takeOwnership','manage_changeOwnershipType')
    security.declareProtected('View management screens', 'manage_owner',
        'manage_UndoForm', 'manage_page_style_css', 'manage_page_header',
        'manage_page_footer', 'manage', 'manage_edit_form', 'manage_main','manage_workspace')

    security.declarePrivate('atomicSubmit')
    def atomicSubmit(self):
        "this is used in editing of subparts"
        return self.submitChanges()

    security.declareProtected('CompoundDoc: Manage Config', 'manage_config')
    def manage_config(self):
        "draw the config panel"
        return ''.join([self.begin_manage(), self.submitChanges(), self.config(), self.manage_page_footer()])
    
    security.declareProtected('View', "__str__")
    def __str__(self):
        "str rep of object"
        return str(self.view())
    
    def manage_tabs(self):
        "return the tabbed interface for editing this object"
        format = '<div class="mainMenu">%s</div><div class="pathMenu">%s at  %s</div>'
        return format % (self.manage_absolute_urls(), self.meta_type, self.tabs_path_default())

    def tabs_path_default(self, unquote=urllib.unquote):
        "Custom tabs_path_default for creating the white on black interface"
        #All forms items that compounddoc has to process consists of absolute urls to the db
        #so if there are no / in the form keys then there is nothing to process
        if self.REQUEST.form and not 'CompoundDocProcessed' in self.REQUEST.other and utility.any(key.startswith('/') for key in self.REQUEST.form):
            self.manage_edit()
            url = self.REQUEST.other.get('redirectTo', None)
            if url is not None:
                return self.REQUEST.RESPONSE.redirect(url)
            
        linkpat = '<a href="%s/manage_main">%s</a>\n'
        temp = ''
        out = [linkpat % ('', '/')]
        for i in self.absolute_url(1).split('/'):
            temp = temp + '/' + i
            out.append(linkpat % (temp, i))
            out.append('/')
        return ''.join(out)

    def manage_absolute_urls(self, REQUEST={}):
        "create an absolute url sequence for management"
        url = self.absolute_url_path()
        format = '<a href="%s%s" %s>%s</a>\n'
        
        queryString = self.REQUEST.environ.get('QUERY_STRING', '')
        if queryString:
            queryString = '?' + queryString
        
        manageTab = self.REQUEST.URLPATH0.replace('%s/' % url, '').split('/')[0]
        temp = []
        append = temp.append
        for i in self.filtered_manage_options():
            if i['action'] == manageTab:
                append(format % (os.path.join(url, i['action']), queryString, 'class="highLight"', i['label']))
            else:
                append(format % (os.path.join(url, i['action']), queryString, '', i['label']))
        return ''.join(temp)
    
    security.declareProtected('View', "__call__")
    def __call__(self, client=None, REQUEST={}, RESPONSE=None, name=None, mode=None, **kw):
        "call rep of object"
        if mode is None:
            mode = self.getDrawMode()
        obj = self.draw(mode, **kw)
        if mode == 'view':
            return self.gen_html(obj)
        return obj

    security.declareProtected('View', 'inlineView')
    def inlineView(self):
        "Inline view of document"
        return '%s%s%s' % (self.begin_manage(), self.gen_html(self.view()), self.manage_page_footer())

    security.declarePrivate('eventProfileLoad')
    def eventProfileLoad(self, id, content):
        "Handle an ProfileLoad event"
        if self.overwrite or (hasattr(aq_base(self), id) and not getattr(self, id) and content):
            self.setObject(id, content)
        else:
            self.updateObject(id, content)

    security.declarePrivate("removeUnNeeded")
    def removeUnNeeded(self, keeplist, typekeeplist):
        "Remove the UnNeeded items based on this list"
        idsKeep = self.objectIds(typekeeplist) + keeplist
        self.delObjects([id for id in self.objectIds() if id not in idsKeep])

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "before editing"
        pass

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "before editing"
        pass

    security.declareProtected('Change CompoundDoc','manage_edit')
    def manage_edit(self, dict=None):
        "Process edits."
        self.before_manage_edit(dict)
        self.objectSpecificEdit(dict)
        self.after_manage_edit(dict)
        self.notifyObserversSyncDB()
        self.add_delete_objects(dict)

    security.declarePrivate('alternate_manage_edit')
    def alternate_manage_edit(self, dict=None):
        "Process edits."
        alt = getattr(self, 'alternate_security_edit', None)
        if alt is not None:
            try:
                if getSecurityManager().validate(None, self, 'alternate_security_edit', alt):
                    alt(dict)
            except Unauthorized:
                pass
        for key, value in dict.iteritems():
            if hasattr(aq_base(self), key):
                object = getattr(self, key)
                if hasattr(aq_base(object), 'alternate_manage_edit'):
                    object.alternate_manage_edit(dict = value)

    security.declarePrivate('objectSpecificEdit')
    def objectSpecificEdit(self, dict):
        "This is the object specific edit stuff"
        for i, j in dict.items():
            if hasattr(aq_base(self), i):
                object = getattr(self, i)
                if hasattr(aq_base(object), 'manage_edit'):
                    object.manage_edit(dict = dict[i])
                else:
                    self.setObject(i, j)

    security.declarePrivate('notifyObserversSyncDB')
    def notifyObserversSyncDB(self):
        "notify all observers and set the object as changed"
        if self.hasBeenModified():
            self.updateBoboBaseModificationTime()
            self.observerNotify()
            if self.meta_type != 'CompoundDoc':
                self.runChangeNotificationScript()

    security.declarePrivate('runChangeNotificationScript')
    def runChangeNotificationScript(self):
        "run the script if we have one to notify of changes"
        scriptPath = self.getConfig('scriptChangePath')
        if scriptPath and self.REQUEST.other.get('okayToRunNotification',  1):
            script = self.restrictedTraverse(scriptPath, None)
            if script is not None:
                script(self)

    security.declarePrivate('hasBeenModified')
    def hasBeenModified(self):
        "check if this item has been modified in the current transaction"
        return hasattr(self, 'REQUEST') and aq_base(self) in self.REQUEST.other.get('modifiedPaths', [])

    security.declarePrivate('performUpdate')
    def performUpdate(self):
        "Update object to newest version"
        self.gen_vars()
        self.delayed_gen_vars()
        for item in self.__dict__.values():
            if hasattr(aq_base(item), 'performUpdate'):
                item.__of__(self).performUpdate()

    security.declarePrivate('performUpgrade')
    def performUpgrade(self):
        "perform the upgrade on this object and its children"
        self.upgrader()
        for key in self.__dict__.keys():
            item = getattr(self,key)
            if hasattr(aq_base(item), 'performUpgrade'):
                item.performUpgrade()

    security.declareProtected('View', "index_html")
    def index_html(self, mode='view'):
        "Basic View Alone"
        return self(mode=mode)

    security.declarePrivate('gen_vars')
    def gen_vars(self):
        "Generate variables also used in update."
        if hasattr(aq_base(self), 'instance'):
            for name, value in self.instance:
                if name not in self.__dict__:
                    self.updateObject(name, value)

    security.declarePrivate('delayed_gen_vars')
    def delayed_gen_vars(self):
        "These are vars that can not be generated until after the first update pulse goes through"
        if hasattr(aq_base(self), 'delayedInstance'):
            for name, value in self.delayedInstance:
                if name not in self.__dict__:
                    self.updateObject(name, value)           
        for i in self.aq_parent.objectValues(['CreationAssistant', 'CreationAssistantString', 'CreationAssistantDTML']):
            if self.meta_type == i.metaType:
                i.setupObject(self)

    security.declarePrivate('gen_html')
    def gen_html(self, data):
        "Interpret DTML and convert to HTML"
        if callable(data):
            data = data.__of__(self)()
        try:
            if 'dtml' in data:
                return Globals.HTML(data, globals())(self, self.REQUEST)
        except TypeError:
            pass
        return data

    security.declareProtected('View', 'getSecurityMode')
    def getSecurityMode(self):
        "select which mode we should be using between edit and view based on security"
        if getSecurityManager().checkPermission('Change CompoundDoc', self):
            return 'edit'
        return 'view'

    security.declarePublic('draw')
    def draw(self, renderType='view', **kw):
        "rendering dispatcher"
        try:
            renderName = self.drawDict[renderType]
        except KeyError:
            renderName = None
        if renderName is not None:
            render = self.restrictedTraverse(renderName, None)
            if render is not None:
                return render(**kw)
        return ''

    security.declarePrivate("getDictName")
    def getDictName(self):
        "Return the names of these items in a list but formatted for the form output filter"
        #remove the path to this compounddoc from the path to the object in it
        cdocPath = self.getCompoundDoc().getPhysicalPath()
        myPath = list(self.getPhysicalPath()[len(cdocPath):])
        return [cdocPath, myPath]

    security.declareProtected('View management screens', 'debugObject')
    def debugObject(self, **kw):
        "Get the info for this object and stick it on this list"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % self.getEncoding())
        temp = []
        temp.append('<p>I am: %s</p>' % self.getId())
        if hasattr(self, 'profile') and self.meta_type == 'CompoundDoc':
            temp.append('<p>My profile is: %s</p>' % self.profile)
        temp.append('<p>My type is: %s</p>' % self.meta_type)
        #Security reasons not sure what to do with this entirely yet but I think it is mostly obsolete
        temp.append('<div>%s</div>' % self.convert(str(self.__dict__)))
        return ''.join(temp)

    security.declarePrivate('getRemoteObject')
    def getRemoteObject(self, path, meta_type = ''):
        "Get the remote image"
        if path:
            item = self.restrictedTraverse(path, default=None)
            if not item:
                item = self.getCompoundDoc().restrictedTraverse(path, default=None)
            if not item:
                item = self.getCompoundDocContainer().restrictedTraverse(path, default=None)
            if item and item.meta_type == meta_type:
                return item

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        available =[''] + self.availableObjects()
        noremove = self.noremove()
        return [i for i in available if i not in noremove]

    security.declarePrivate('updateBoboBaseModificationTime')
    def updateBoboBaseModificationTime(self):
        """Update the bobobase_modification_time of all parents up to the main compounddoc
        of a change if we are newer then our parent"""
        for i in self.aq_chain:
            if self._p_mtime > i._p_mtime:
                i._p_changed=1
            if getattr(aq_base(i), 'meta_type', None) == 'CompoundDoc':
                break

    security.declarePrivate('noCacheHeader')
    def noCacheHeader(self):
        "set the headers so this item will not be cached needed becuase the same url can map to multiple objects"
        #self.REQUEST.RESPONSE.setHeader('Expires', '-1')
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')
        self.REQUEST.RESPONSE.setHeader('Pragma', 'no-cache')
        #self.REQUEST.RESPONSE.setHeader('Cache-Disposition', 'private')

    security.declarePrivate('issueEventProfileLast')
    def issueEventProfileLast(self):
        "call the eventProfileLast on every sub object"
        temp = [object for object in self.objectValues() if hasattr(aq_base(object), 'eventProfileLast')]
        for i in temp:
            i.eventProfileLast()
        for i in temp:
            i.issueEventProfileLast()

    security.declarePrivate('eventProfileLast')
    def eventProfileLast(self):
        "run this event as the last thing the object will do before the profile is returned"
        self.observerNotify()

    security.declarePublic('getUniqueMetaTypes')
    def getUniqueMetaTypes(self):
        "return all the unique meta_types found in this object"
        meta_types = set([self.meta_type])
        for obj in self.objectValues():
            if obj.hasObject('getUniqueMetaTypes'):
                meta_types.add(obj.getUniqueMetaTypes())
        return meta_types

    security.declarePrivate('setSelectedDocument')            
    def setSelectedDocument(self, selected):
        "set the selected document to redirect to"
        baseURL = self.REQUEST.other['URL']
        queryString = self.REQUEST.environ.get('QUERY_STRING', '')
        if selected:
            url = baseURL + '?' + utility.updateQueryString(queryString, {'selectedDocument': selected})
        else:
            url = baseURL + '?' + queryString
        urlFrom = self.REQUEST.other.get('HTTP_REFERRER', '')
        if urlFrom != url:
            self.REQUEST.other['redirectTo'] = url

Globals.InitializeClass(Base)
