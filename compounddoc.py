# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from base import Base
from Products.ZCatalog.CatalogPathAwareness import CatalogAware
import OFS.History
from AccessControl import getSecurityManager
import time
import copy
from userobject import UserObject
from DateTime import DateTime
import utility
from useragent import UserAgent

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from Acquisition import aq_base
from forminputfilter import FormInputFilter

import mixregistered #needed to init all the items
import controlpanel


from OFS.ObjectManager import ObjectManager
import register

import basewidget

from BTrees.OOBTree import difference,intersection

import Acquisition

from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import UnrestrictedUser

import AccessControl.Owned

import zExceptions

import nestedlisturl as NestedListURL

from Products.ZCatalog.ZCatalog import ZCatalog

import com.db

def manage_addCompoundDoc(self, id, profile=None, prepend=None, REQUEST=None, RESPONSE=None, redir=1, returnObject=None, folderCreate=None, cdocName=None, autoType=None):
    "Create a compounddoc with this id and profile"
    name = id
    del id
    form = self.REQUEST.form    #can't make a deepcopy but why do I need to clear it before handing on?
    if profile is None:
        profile = form.get('profile', None)
        profile = profile if profile != 'None' else None
    randomAllowed = ('random','long random')
    if name in randomAllowed:
        name = ''
        autoType = 'timestamp'
    if folderCreate is not None:
        if cdocName is not None and cdocName in randomAllowed:
            name = '%s/%s' % (name, '')
            autoType = 'timestamp'
        else:
            name = '%s/%s' % (name, cdocName)

    container = self
    if '/' in name:
        path = name.split('/')
        folders, name = path[:-1], path[-1]
        path = '/'.join(utility.drawFolderPath(folders, self))
        container = self.restrictedTraverse(path)

    if autoType is not None and name == '':
        name = getAutoName(autoType, prepend, container)
    
    if prepend:
        name = prepend + name
    initid = name
    name = utility.cleanRegisteredId(name)
    if (not name or container.hasObject(name)):
        utility.log("we have this object already")
        if REQUEST is not None:
            return self.manage_add_form(profile, initid, 1)
        else: #if we already have an object or no valid name but we have no REQUEST it is being added from a script and None needs to be returned
            return None
    if profile is not None or (utility.isCleanFileName(profile) and utility.allowed_profile(profile)):
        container._setObject(name, CompoundDoc(name, profile))
    else:
        return None
    if returnObject is not None:
        return getattr(self, name)

    if form.get('manage_add', None) == "quick add":
        return self.REQUEST.RESPONSE.redirect(container.absolute_url() + "/manage_workspace")
    elif form.get('manage_add', None) == "add" or redir:
        return self.REQUEST.RESPONSE.redirect(getattr(container, name).absolute_url()+"/manage_edit_form")


def getAutoName(autoType, prepend=None, container=None):
    "run the correct auto namer"
    if autoType == 'timestamp':
        return createNameTimeStamp(prepend, container)
    if autoType == 'counter':
        return createNameCounter(prepend, container)

def createNameTimeStamp(prepend=None, container=None):
    "create a cdoc name from the current time"
    return repr(time.time()).replace('.', '_')

def createNameCounter(prepend=None, container=None):
    "create a cdoc name based by looking in this container for other items that start with this prepend name"
    counter = None
    for docname in container.objectIds():
        if docname.startswith(prepend):
            first,second = docname.split(prepend, 1)
            try:
                localCounter = int(second)
                if localCounter > counter:
                    counter = localCounter
            except ValueError:
                pass
    if counter is None:
        counter = 1
    else:
        counter = counter + 1
    return str(counter)

def manage_add_form(self, profile=None, id='', error=0, folderCreate=None, cdocName=None):
    "Manage add form"
    temp = [self.manage_page_header()]
    temp.append('''
    Please type the name you want this CompoundDoc to have:<br>
    <form name="form" action="manage_addCompoundDoc"><br>''')
    if error:
        temp.append('''<p>The name for this object is not valid
            or is already used. Please
            choose a name that starts with a letter and
            contains only letters, numbers, and _</p>''')
    temp.append('<input type="text" name="id" value="%s" >' % id)
    profiles = utility.getStoredProfileNames()
    if profile is not None and profile in profiles:
        temp.append('<input type="hidden" name="profile:string" value="%s">' % profile)
    else:
        default = getattr(self, 'CompoundDocProfileDefault', 'Default')
        shownProfiles = getattr(self, 'CompoundDocProfilesShown', None)
        if shownProfiles:
            shownProfiles = set(shownProfiles).intersection(set(profiles))
            shownProfiles = list(shownProfiles)
        else:
            shownProfiles = profiles
        shownProfiles.sort()
        if default not in shownProfiles:
            default = shownProfiles[0]
        temp.append(basewidget.option_select(shownProfiles, 'profile', [default]))
    if folderCreate is not None:
        temp.append('<input type="hidden" name="folderCreate:string" value="1">')
    if cdocName is not None:
        temp.append('<input type="hidden" name="cdocName:string" value="%s">' % cdocName)
    temp.append('''<br>
    <p>Note: Only names that start with a letter and the rest of the name contains only letters, numbers and _ are valid.</p>
    <input type="submit" name="manage_add" value="add"><input type="submit" name="manage_add" value="quick add">
    </form>''')
    temp.append(self.manage_page_footer())
    return ''.join(temp)

class CompoundDoc(Base, OFS.History.Historical, CatalogAware, UserObject):
    "Compound Doc class"
    classDict = register.classDict
    


    ControlPanel = controlpanel.ControlPanel('ControlPanel')
    
    meta_type = "CompoundDoc"
    security = ClassSecurityInfo()
    overwrite = 1
    SSLRequired = 0
    configDocPath = ''
    profileTypeKeep = None
    profile = None
    scriptChangePath = ''
    defaultDisplay = None
    displayMap = None
    DisplayManager = None
    EventManager = None
    LinkManager = None
    TabManager = None
    CatalogManager = None
    userModificationTimeStamp = None
    changeContextRenders = 1
    cdocAutoAddTypes = ('timestamp', 'counter')
    renderScriptLookupPath = ''
    isConfigDoc = 0
    masterLocation = None

    classConfig = {}
    classConfig['SSLRequired'] = {'name':'SSLRequired for access', 'type': 'radio'}
    classConfig['scriptChangePath'] = {'name':'Path to change notification script', 'type': 'path'}
    classConfig['configDocPath'] = {'name':'Path to configuration document', 'type': 'path'}
    classConfig['renderScriptLookupPath'] = {'name':'Path to render script', 'type': 'path'}
    classConfig['changeContextRenders'] = {'name':'Change the context of renders?', 'type': 'radio'}
    classConfig['isConfigDoc'] = {'name':'Is this Document a ConfigDoc?', 'type': 'radio'}


    configurable = ('renderScriptLookupPath',)
    updateReplaceList = ('SSLRequired', 'scriptChangePath', 'configDocPath', 'changeContextRenders')

    security.declareProtected('Access contents information', 'OOdifference')
    OOdifference = difference
    
    security.declareProtected('Access contents information', 'OOintersection')
    OOintersection = intersection

    security.declarePrivate('atomicSubmit')
    def atomicSubmit(self):
        "this is used in editing of subparts"
        return ''

    security.declarePrivate('getProfileTypeKeep')
    def getProfileTypeKeep(self):
        "get the profileTypeKeep var if it is not None and a blank list otherwise"
        if self.profileTypeKeep is not None:
            return self.profileTypeKeep
        return []
    
    security.declareProtected('Change permissions', 'manage_access')
    security.declareProtected('Take ownership', 'manage_takeOwnership','manage_changeOwnershipType')
    security.declareProtected('View management screens', 'manage_owner',
        'manage_change_history_page', 'manage_UndoForm', 'manage_page_style_css', 'manage_page_header',
        'manage_page_footer', 'ControlPanel', 'manage', 'manage_edit_form', 'manage_main', 'manage_workspace')
    security.declareProtected('CompoundDoc: Container View', 'manage_container')
    manage_container = ObjectManager.manage_main
    manage_beforeDelete = CatalogAware.manage_beforeDelete

    security.declareProtected('CompoundDoc: Indexing', 'reindex_object')
    reindex_object = CatalogAware.reindex_object

    #Add a new option to manage options
    manage_options = Base.manage_options +\
     OFS.History.Historical.manage_options + (
     {'label': 'Control Panel', 'action': 'ControlPanel'},
     {'label': 'Container View', 'action': 'manage_container'},)

    manage_names = [i['action'] for i in manage_options]

    security.declareProtected('View', "__str__")
    def __str__(self):
        "str rep of object"
        return self.render(mode='view')

    security.declareProtected('View', 'getUserAgent')
    def getUserAgent(self):
        "return a useragent object and stuff it in the request if it is not there already"
        if 'UserAgent' not in self.REQUEST.other:
            self.REQUEST.other['UserAgent'] = UserAgent(self.REQUEST).__of__(self)
        return self.REQUEST.other['UserAgent']
        
    security.declarePublic('parseForm')
    def parseForm(self, dictionary):
        "parse a form into a set of nested dictionaries"
        return FormInputFilter(dictionary)()

    security.declareProtected('CompoundDoc: Change Owner', 'compoundChangeOwnership')
    def compoundChangeOwnership(self, username):
        "change the owner of this object"
        user = self.getUser(username)
        if user is None:
            return None
        #self.changeOwnership(user)
        self._owner = AccessControl.Owned.ownerInfo(user)
        ownerusers = self.users_with_local_role('Owner')
        for user in ownerusers:
            roles = list(self.get_local_roles_for_userid(user))
            roles.remove('Owner')
            if roles:
                self.manage_setLocalRoles(user, roles)
            else:
                self.manage_delLocalRoles([user])
        self.manage_addLocalRoles(username, ['Owner'])

    security.declarePrivate('getUser')
    def getUser(self, username):
        "get this user or return None if you can't find it"
        acl_users = None
        for item in self.aq_chain:
            temp_user = getattr(item, 'acl_users', None)
            if temp_user is not None:
                if temp_user.getUser(username) is not None:
                    acl_users = temp_user
                    break
        if acl_users is not None:
            return acl_users.getUser(username).__of__(acl_users)
        
    security.declarePrivate('__init__')
    def __init__(self, id, profile=None):
        "create a new cdoc"
        if profile is not None:
            self.profile = profile
        self.id = id
        self._init = 1

    security.declarePrivate('setupCompoundDoc')
    def setupCompoundDoc(self):
        "Setup a compounddoc once created"
        self.gen_vars()
        if hasattr(self, '_init'):
            if getattr(self, 'profile', None):
                self.changeProfile(self.profile)
            del self._init

    security.declareProtected('CompoundDoc: Profile Modification', 'changeProfile')
    def changeProfile(self, name=None, doc=None):
        "Change the profile of this object to this name"
        self.unindex_object()
        #self.unindexSubDocs()
        if name == 'None':
            name = None
        if name is not None or doc is not None:
            if doc is not None and doc.meta_type == self.meta_type:
                data = copy.deepcopy(aq_base(doc))
                name = doc.profile
            else:
                data = utility.objectLoadFile(name)
            if data:
                self.updateVersion = getattr(data, 'updateVersion', 0)
                self.objectVersion = getattr(data, 'objectVersion', 0)
                self.objectLoadCDoc(data)
                self.profile = name
                self.upgradeAll()
        else:
            self.setObject('objectVersion', self.classVersion)
            self.setObject('updateVersion', self.classUpdateVersion)
        self.issueEventProfileLast()
        self.indexSubDocs()
        self.index_object()

    security.declareProtected('CompoundDoc: Profile Modification', 'unsetProfile')
    def unsetProfile(self):
        "unset the profile for this CompoundDoc"
        self.profile = ''

    security.declareProtected('CompoundDoc: Sub Transaction', 'subTransFunc')
    def subTransFunc(self, seq, func, count):
        "run this function using subtrasnactions"
        return (func(item) for item in com.db.subTrans(seq, count))
        
    security.declarePrivate('resetMaster')
    def resetMaster(self):
        "copy the remove shared objects locally since we are not a master document"
        masterLocation = self.masterLocation
        if masterLocation is not None:
            cdoc = self.getCompoundDoc()
            if masterLocation != cdoc.getPath():
                master = self.unrestrictedTraverse(masterLocation, None)
                if master is not None and master.meta_type == 'CompoundDoc' and master.DisplayManager is not None:
                    cdoc.setObject('DisplayManager', aq_base(master.DisplayManager)._getCopy(master))
        
    security.declareProtected('CompoundDoc: Profile Modification', 'changeDisplay')
    def changeDisplay(self, name=None, doc=None):
        "Change the displays of this object to what the profile of this name has"
        if doc is not None and doc.meta_type == self.meta_type:
            data = aq_base(doc)
        else:
            data = utility.objectLoadFile(name)
        if data:
            self.objectLoadCDocDisplayOnly(data)
    
    security.declarePrivate('unindex_sub_docs')
    def unindexSubDocs(self):
        "unindex all the sub documents that we have"
        for doc in self.findSubDocs():
            doc.unindex_object()
        
    security.declarePrivate('index_sub_docs')
    def indexSubDocs(self):
        "index all the sub documents that we have"
        for doc in self.findSubDocs():
            doc.index_object()

    security.declarePrivate('findSubDocs')
    def findSubDocs(self):
        "find the subdocuments of this compounddoc and return them"
        return (obj for name, obj in self.ZopeFind(self, obj_metatypes=['CompoundDoc'], search_sub = 1))
    
    security.declareProtected('Access contents information', 'getCompoundDoc')
    def getCompoundDoc(self):
        "This will return the object reference to the first CompounDoc it can find"
        return self

    security.declareProtected('Access contents information', 'getCompoundDocContainer')
    def getCompoundDocContainer(self):
        "This will return the object reference to the first container about a compounddoc it can find"
        return self.aq_inner.aq_parent

    security.declarePublic('getConfigDoc')
    def getConfigDoc(self):
        "get the config document if it exists"
        configDoc = None
        configDocPath = self.configDocPath
        if configDocPath:
            try:
                configDoc = self.REQUEST.other.get('configDocReq', {})[configDocPath]
            except KeyError:
                if configDocPath:
                    doc = self.getCompoundDocContainer().unrestrictedTraverse(configDocPath, None)  #needs to be unrestricted or it does not work during __bobo_traverse__
                    if doc is not None:
                        configDocReq = self.REQUEST.other.get('configDocReq', {})
                        configDocReq[configDocPath] = doc
                        self.REQUEST.other['configDocReq'] = configDocReq
                        configDoc = doc
        return configDoc

    security.declarePublic('getRenderScriptLookup')
    def getRenderScriptLookup(self):
        "get the render script"
        lookup = None
        
        try:
            path = self._v_scriptLookupPath
            lookup = self.getPhysicalRoot().unrestrictedTraverse(path, None)
        except AttributeError:
            renderScriptLookupPath = self.getConfig('renderScriptLookupPath')
            if renderScriptLookupPath:
                script = self.getCompoundDocContainer().unrestrictedTraverse(renderScriptLookupPath, None)  #needs to be unrestricted or it does not work during __bobo_traverse__
                if script is not None:
                    self._v_scriptLookupPath = '/'.join(script.getPhysicalPath())
                    lookup = script
        return lookup

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        #If we have an object with this name return it otherwise try a layout
        try:
            if self.SSLRequired and not self.REQUEST.SERVER_URL.startswith('https'):
                return self.denied
        except AttributeError:  #during an upgrade the REQUEST object does not exist yet so we can ignore this check anyways
            pass
        if name:
            obj = getattr(self, name, None)
            if obj is not None:
                return obj

            obj = self.findRender(name)
            if obj is not None:
                return obj

    security.declarePublic('findRender')
    def findRender(self, name):
        "find the rendering document based on this name"
        if self.displayMap is not None:
            mapping = self.displayMap.get(name, None)
            if mapping is not None:
                self.setRenderREQUEST(name, mapping[0], mapping[2])
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

        if self.hasCompoundDisplayView(name):
            self.REQUEST.other['layout'] = name
            return self

        configDoc = self.getConfigDoc()
        if configDoc is not None:
            if configDoc.displayMap is not None:
                mapping = configDoc.displayMap.get(name, None)
                if mapping is not None:
                    self.setRenderREQUEST(name, mapping[0], mapping[2])
                    return self
        

    security.declareProtected('View', "__call__")
    def __call__(self, client=None, REQUEST=None, RESPONSE=None, name=None, mode=None, **kw):
        "call rep of object"
        if hasattr(self, 'REQUEST'):
            #All forms items that compounddoc has to process consists of absolute urls to the db
            #so if there are no / in the form keys then there is nothing to process
            if self.REQUEST.form and not 'CompoundDocProcessed' in self.REQUEST.other:
                self.manage_edit()
                url = self.REQUEST.other.get('redirectTo', None)
                if url is not None:
                    return self.REQUEST.RESPONSE.redirect(url)
                
            cdoc = self.getCdocFromPublished()
            self.setDrawMode(mode)
            if cdoc is not None and aq_base(cdoc) is aq_base(self):
                return self.index_html()
            else:
                if name is None:
                    name = self.getDisplayName()
                mode = mode or self.getDrawMode()
                return self.draw(mode, display=name)

    security.declareProtected('View', "render")
    def render(self, name=None, mode='view', *args, **kw):
        "just render this document with this name and mode with nothing special"
        return self.draw(mode, display=name, showWrapper=0, *args, **kw)

    security.declareProtected('View', "index_html")
    def index_html(self, REQUEST=None):
        "Basic View Alone"
        #All forms items that compounddoc has to process consists of absolute urls to the db
        #so if there are no / in the form keys then there is nothing to process
        if self.REQUEST.form and not 'CompoundDocProcessed' in self.REQUEST.other:
            self.manage_edit()
            url = self.REQUEST.other.get('redirectTo', None)
            if url is not None:
                return self.REQUEST.RESPONSE.redirect(url)

        #race condition draw MUST be called before trying to get the wrapper
        #display=getattr(self, 'displayName', None)
        bodyScript = self.REQUEST.other.get('renderScript', None)
        if bodyScript is not None:
            body = bodyScript(self)
        else:
            body = self.view(display=self.getDisplayName())

        header, footer = ('','')
        cdoc = self.getCdocFromPublished()
        if cdoc is not None and aq_base(cdoc) is aq_base(self):
            #Controlling document stuff
            self.REQUEST.other['CompoundDoc'] = self
            self.noCacheHeader()
            header, footer = self.getWrapper()
            header, footer = utility.renderNoneAsString(header), utility.renderNoneAsString(footer)
            #This is to catch changes that happen during the rendering of the page
            self.processChanges()
        return '%s%s%s' % (header, body, footer)

    security.declarePrivate('getDocFromPublished')
    def getCdocFromPublished(self):
        "get and return the cdoc in charge of rendering based on the information in PUBLISHED"
        cdocPublished = self.REQUEST.other.get('cdocPublished', None)
        if cdocPublished is not None:
            return cdocPublished
        published = self.REQUEST.other.get('PUBLISHED', None)
        if published is not None:
            try:
                published = published.im_self
            except AttributeError:
                pass
            
            for i in published.aq_chain:
                if getattr(i, 'meta_type', None) == 'CompoundDoc':
                    self.REQUEST.other['cdocPublished'] = i
                    return i

    security.declarePrivate('getWrapper')
    def getWrapper(self):
        "get the header and footer for this page in one request and return it as a list"
        headerScript = self.REQUEST.other.get('headerScript', None)
        footerScript = self.REQUEST.other.get('footerScript', None)
        
        if headerScript is not None and footerScript is not None:
            return (headerScript(self), footerScript(self))
        
        header = self.REQUEST.other.get('header', None)
        footer = self.REQUEST.other.get('footer', None)
        if header is not None and footer is not None:
            return (self.drawCallablePath(header), self.drawCallablePath(footer))
        
        try:
            return self.REQUEST.other['DisplayFilter'].getWrappers()
        except (KeyError, AttributeError):
            return ("","")

    security.declarePublic('hasCompoundDisplayView')
    def hasCompoundDisplayView(self, viewname):
        "return the comparison of having this view in the displaymanager"
        if self.displayMap is not None and self.displayMap.has_key(viewname):
            return True
        configDoc = self.getConfigDoc()
        if configDoc is not None:
            if configDoc.displayMap is not None and configDoc.displayMap.has_key(viewname):
                return True
        if self.DisplayManager is not None and viewname in self.DisplayManager.objectIds('Display'):
            return True

    security.declareProtected('View management screens', 'edit')
    def edit(self, display=None, showWrapper=1, *args, **kw):
        """Inline edit short object
        Use the object defined layout if possible"""
        self.setDrawMode('edit')
        return self.renderPurpose('edit', display, showWrapper, *args, **kw)

    security.declareProtected('View', 'view')
    def view(self, display=None, showWrapper=1, *args, **kw):
        "Inline short draw"
        return self.renderPurpose('view', display, showWrapper, *args, **kw)

    security.declarePrivate('renderPurpose')
    def renderPurpose(self, purpose, display, showWrapper, *args, **kw):
        "render items for a purpose"
        if self.isConfigDoc:
            return ''

        text = self.renderDisplayScript(purpose, display, showWrapper, *args, **kw)
        if text is None:
            text = self.renderDisplay(purpose, display, showWrapper, *args, **kw)
        if text is not None:
            return text
        if text is None and self.DisplayManager is not None:
            text = self.DisplayManager.render(purpose=purpose, display=display)

        if text is None:
            text = '<p>No Display Found</p>'
        return text

    security.declarePrivate('renderDisplay')
    def renderDisplay(self, purpose, display, showWrapper, *args, **kw):
        "Please render an item with this purpose"
        configDoc = None
        if not display: #This is to catch cases where a blank string is passed
            if self.defaultDisplay is not None:
                display = self.defaultDisplay.get(purpose, None)
            
            if not display:  #needs to be not since display can be a blank string
                configDoc = self.getConfigDoc()
                if configDoc is not None and configDoc.defaultDisplay is not None:
                    display = configDoc.defaultDisplay.get(purpose, None)
            
        if display is not None:
            mapping = None
            if self.displayMap is not None:
                mapping = self.displayMap.get(display, None)
            if mapping is None:
                configDoc = configDoc if configDoc is not None else self.getConfigDoc()
                if configDoc is not  None:
                    mapping = configDoc.displayMap.get(display, None)
            if mapping is not None:
                if showWrapper:
                    self.setRenderREQUEST(display, mapping[0], mapping[2])
                return self.drawCallablePath(mapping[1], *args, **kw)
        
        return None

    security.declarePrivate('renderDisplayScript')
    def renderDisplayScript(self, purpose, display, showWrapper, *args, **kw):
        "Please render an item with this purpose using a script for lookup"
        lookup = self.getRenderScriptLookup()
        
        if lookup is None:
            return None
        
        if not display:
            if purpose =='edit':
                display = 'defaultEdit'
            elif purpose == 'view':
                display = 'defaultView'
        
        header, body, footer = lookup(self, display)
        if showWrapper:
            self.setRenderREQUESTScript(display, None, header, footer)
        if body is not None:
            return body(self, *args, **kw)
        return None

    security.declarePrivate('setRenderREQUESTScript')
    def setRenderREQUESTScript(self, name, body, header, footer):
        "set the render request for this mapping"
        if not 'DisplayFilter' in self.REQUEST.other:
            if not 'headerScript' in self.REQUEST.other:
                self.REQUEST.other['headerScript'] = header
                self.REQUEST.other['footerScript'] = footer
        if 'renderName' not in self.REQUEST.other:
            self.REQUEST.other['renderName'] = name
        if 'renderSCript' not in self.REQUEST.other:
            self.REQUEST.other['renderScript'] = body

    security.declarePrivate('setRenderREQUEST')
    def setRenderREQUEST(self, name, header, footer):
        "set the render request for this mapping"
        if not 'DisplayFilter' in self.REQUEST.other:
            if not 'header' in self.REQUEST.other:
                self.REQUEST.other['header'] = header
                self.REQUEST.other['footer'] = footer
        if 'renderName' not in self.REQUEST.other:
            self.REQUEST.other['renderName'] = name

    security.declarePrivate('getDisplayName')
    def getDisplayName(self):
        "get the current displayName from the REQUEST object"
        displayName = self.REQUEST.other.get('renderName', None)
        if displayName is None:
            displayName = self.REQUEST.other.get('layout', None)
        if displayName is None:
            displayName = self.REQUEST.other.get('editlayout', None)
        return displayName

    security.declarePrivate('drawCallablePath')
    def drawCallablePath(self, path, *args, **kw):
        "render this path"
        if path:
            script = self.getCompoundDocContainer().restrictedTraverse(path, None)
            if script is not None:
                if self.getConfig('changeContextRenders'):
                    return self.changeCallingContext(script)(*args, **kw)
                else:
                    return script(self, *args, **kw)
        return None
        
    security.declareProtected('Change CompoundDoc', 'manage_edit')
    def manage_edit(self, RESPONSE=None, dict=None):
        "Process edits"        
        self.REQUEST.other['CompoundDocProcessed'] = 1 #This is done first to prevent recursion
        if any(key.startswith('/') for key in self.REQUEST.form):
            form = self.getCorrectForm(dict)
            #Once one compounddoc is dispatching to others for what needs to be saved no further
            #attempts to do this should be done
            self.REQUEST.form = form
            self.processRemoteEdits(form)
            self.processChanges()

    security.declareProtected('Change CompoundDoc', 'processChanges')
    def processChanges(self):
        "process the changes if there are any"
        modifiedDocs = self.REQUEST.other.get('modifiedDocs', [])
        for obj in copy.copy(modifiedDocs):
            sslState = obj.SSLRequired
            if sslState:
                obj.setObject('SSLRequired', 0)
            
            obj.updateUserModifiedTimeStamp()
            obj.reindex_object()
            obj.runChangeNotificationScript()
            
            #Reset the SSL protection to what it was before we disabled it
            if sslState:
                obj.setObject('SSLRequired', sslState)
            
        if modifiedDocs:
            del self.REQUEST.other['modifiedDocs']
            self.invalidateCaches()

    security.declarePrivate('localProcessing')
    def localProcessing(self, form):
        "do all of the local data processing so that manage_edit is not recursive"
        self.deleteDocProcessor(form)
        self.addDocProcessor(form)
        if utility.hasLocalEdit(form):
            self.processAlternateSecurityEdits(form)
            if getSecurityManager().checkPermission('Change CompoundDoc', self):
                self.add_delete_objects(form)
                Base.manage_edit(self, dict=form)
            self.processAnnonymousEdits(form)

    security.declarePrivate('updateUserModifiedTimeStamp')
    def updateUserModifiedTimeStamp(self):
        "update the timestamp to current timer"
        if self.hasBeenModified():
            if self.userModificationTimeStamp is not None:
                self.userModificationTimeStamp = DateTime()

    security.declareProtected('Access contents information', 'user_modification_time')
    def user_modification_time(self):
        "return the highest user_modification_time"
        return self.userModificationTimeStamp

    security.declarePrivate('getCorrectForm')
    def getCorrectForm(self, dict):
        "use dict if is exists otherwise use the REQUEST and convert it as needed"
        if dict is not None:
            return dict
        else:
            return FormInputFilter(self.REQUEST.form)()

    security.declarePrivate('processAnnonymousEdits')
    def processAnnonymousEdits(self, dict):
        "Process local edits that might be in this dict"
        seq = [(id, object) for id, object in self.objectItems()
          if id in dict
          and getattr(object, 'annonymousEditAccepted', 0)
          and hasattr(object, 'manage_edit')]
        for name, object in seq:
            object.manage_edit(dict = dict[name])
            del dict[name]

    security.declarePrivate('processAlternateSecurityEdits')
    def processAlternateSecurityEdits(self, dict):
        "do edits under a different security setting this allows things to be edited through a compounddoc but under some other permission"
        localItems = [(id, object) for id, object in self.objectItems()
          if id in dict
          and hasattr(object, 'alternate_manage_edit')]
        for name, object in localItems:
            object.alternate_manage_edit(dict = dict[name])

    def invalidateCaches(self):
        "invalidate all the caches used in various display filters since our data has changed"
        cacheManagers = {}
        if self.DisplayManager is not None:
            for display in self.DisplayManager.objectValues('Display'):
                for displayFilter in display.objectValues('DisplayFilter'):
                    for script in displayFilter.objectValues('Script (Python)'):
                        cacheManager = script.ZCacheable_getManager()
                        if cacheManager is not None:
                            path = cacheManager.getPhysicalPath()
                            if path not in cacheManagers:
                                cacheManagers[path] = cacheManager
        for cacheManager in cacheManagers.values():
            cache = cacheManager.ZCacheManager_getCache()
            cache.clearAccessCounters()
            cache.deleteEntriesAtOrBelowThreshold(0)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, data):
        "process this data for profileTypeKeep so that when it is blank we set it to None"
        profileTypeKeep = data.pop('profileTypeKeep', None)
        if profileTypeKeep is not None:
            if profileTypeKeep == ['']:
                profileTypeKeep = None
            self.setObject('profileTypeKeep', profileTypeKeep)

    security.declarePrivate('processRemoteEdits')
    def processRemoteEdits(self, dict):
        "Process remote edits that might be in this dict"
        #has to be a list since the dict object changes during iteration
        seq = [path for path in dict if path.startswith('/')]
        for path in seq:
            object = self.restrictedTraverse(path, None)
            if object is not None:
                localProcessing = getattr(object, 'localProcessing', None)
                if localProcessing is not None:
                    localProcessing(form = dict.pop(path))

    security.declarePublic('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        objects = self.objectValues()
        objects = (i for i in objects if getattr(i, 'UserObject', None))
        objects = (i for i in objects if i.hasObject('PrincipiaSearchSource'))
        objects = (str(i.PrincipiaSearchSource()) for i in objects)
        return ' '.join(list(objects))

    security.declarePrivate('noremove')
    def noremove(self):
        "return a list of the items that should not be removed"
        return ['Cache', 'CSVDataFilter', 'Calculator', 'CatalogConfig', 'Config',
            'Display', 'DisplayFilter', 'DisplayUserAgent', 'HTMLDataFilter', 'SeperatorDataFilter']

    security.declareProtected('CompoundDoc: Indexing', 'index_object')
    def index_object(self):
        """A common method to allow Findables to index themselves."""
        for catalog in self.getCatalogs():
            utility.addDocToCatalog(catalog, self)

    security.declareProtected('CompoundDoc: Indexing', 'unindex_object')
    def unindex_object(self):
        """A common method to allow Findables to unindex themselves."""
        for catalog in self.getCatalogs():
            utility.removeRecordFromCatalog(catalog, self)

    security.declarePrivate('getCatalogs')
    def getCatalogs(self):
        "return a list of catalog objects suitable for usage in the index and unindex operations"
        if self.CatalogManager is not None:
            catalogs = set(self.CatalogManager.getCatalogs(self))
        else:
            catalogs = set()
        configDoc = self.getConfigDoc()
        if configDoc is not None and configDoc.CatalogManager is not None:
            catalogs.update(configDoc.CatalogManager.getCatalogs(self))
        catalogs.add(self.CDocUpgrader)
        return catalogs

    security.declarePrivate('manage_afterAdd')
    def manage_afterAdd(self, item, container):
        "add to the catalog after this object is added this is called when items are created and renamed"
        self.setupCompoundDoc()
        self.initVersion()
        self.upgradeAll()
        Base.manage_afterAdd(self, item, container)
        try:
            CatalogAware.manage_afterAdd(self, item, container)
        except (NameError, KeyError, ValueError):
            pass

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self, item):
        "add to the catalog after this object is added this is called after an item is cloned"
        self.indexSubDocs()
        self.index_object()
        Base.manage_afterClone(self, item)
        CatalogAware.manage_afterClone(self, item)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.upgradeLayouts()
        self.fixupProfileTypeKeep()
        self.fixUserModificationTime()
        self.removeUnNeededAttributes()
            
    security.declarePrivate('upgradeLayouts')
    def upgradeLayouts(self):
        "upgrade the old layouts to use displays"
        if 'layouts' in self.__dict__:
            self.upgraderSwitchLayouts()
    upgradeLayouts = utility.upgradeLimit(upgradeLayouts, 141)
    
    security.declarePrivate('fixupProfileTypeKeep')
    def fixupProfileTypeKeep(self):
        "fix the profileTypeKeep attribute"
        if self.__dict__.get('profileTypeKeep', None) == []:
            del self.profileTypeKeep
    fixupProfileTypeKeep = utility.upgradeLimit(fixupProfileTypeKeep, 141)
    
    security.declarePrivate('removeUnNeededAttributes')
    def removeUnNeededAttributes(self):
        "remove attributes that are no longer needed"
        self.delObjects(['manage_edit_form', 'manage', 'manage_main', 'manage_workspace', 
            'ControlPanel', 'submitChanges', 'Cache', 'control_panel_help'])
    removeUnNeededAttributes = utility.upgradeLimit(removeUnNeededAttributes, 141)
    
    security.declarePrivate('fixUserModificationTime')
    def fixUserModificationTime(self):
        "fix the userModificationTimeStamp attribute"
        if not 'userModificationTimeStamp' in self.__dict__:
            seq = sorted(i.userModificationTimeStamp for i in self.objectValues() if hasattr(i, 'UserObject') and i.UserObject)
            try:
                self.setObject('userModificationTimeStamp', seq[0])
            except IndexError:
                self.setObject('userModificationTimeStamp', DateTime())        
    fixUserModificationTime = utility.upgradeLimit(fixUserModificationTime, 141)
                
    security.declarePrivate('upgraderSwitchLayouts')
    def upgraderSwitchLayouts(self):
        "Swtich the layouts over to use the DisplayManager"
        for i in self.layouts:
            self.upgradeLayoutDisplayManager(i)
        del self.layouts

    security.declarePrivate('getDisplayManager')
    def getDisplayManager(self):
        "Return the DisplayManager object"
        if not self.hasObject('DisplayManager'):
            self.gen_vars()
        return self.DisplayManager

    security.declarePrivate('upgradeLayoutDisplayManager')
    def upgradeLayoutDisplayManager(self, name):
        "convert the layout named to a DisplayManager entry"
        id = utility.cleanRegisteredId(name)
        dm = self.getDisplayManager()
        dm.addDisplay(id)
        display = getattr(dm, id)
        if hasattr(self, 'layouts'):
            if hasattr(self.layouts[name], 'description'):
                display.setObject('description', self.layouts[name].description)
            if hasattr(self.layouts[name], 'usage'):
                display.setObject('usage', self.layouts[name].usage.lower())
            display.addAndRegisterFilter('%sfilter' % id)
            display.setDefaultFilter('%sfilter' % id)
            filter = getattr(display, '%sfilter' % id)
            if hasattr(self.layouts[name], 'text'):
                filter.setObject('code', self.layouts[name].text)
            if hasattr(self.layouts[name], 'type'):
                filter.setObject('codetype', self.layouts[name].type.upper())
            if hasattr(self.layouts[name], 'required'):
                filter.setObject('required', self.layouts[name].required)
            if hasattr(self.layouts[name], 'optional'):
                filter.setObject('optional', self.layouts[name].optional)

    security.declarePrivate('initVersion')
    def initVersion(self):
        "Set the object version initiially"
        if not 'objectVersion' in self.__dict__:
            self.setObject('objectVersion', 0)
        if not 'updateVersion' in self.__dict__:
            self.setObject('updateVersion', 0)

    security.declarePrivate('upgradeAll')
    def upgradeAll(self):
        "do both the updateUpgrade and the regular upgrade"
        if self.updateVersion < self.classUpdateVersion or self.objectVersion < self.classVersion:
            #Disable SSL protection temporarily for the upgrader and updaters
            sslState = self.SSLRequired
            self.setObject('SSLRequired', 0)
            if self.objectVersion < self.classVersion:
                self.performUpgrade()
            
            if self.updateVersion < self.classUpdateVersion:
                self.gen_vars()
                self.performUpdate()
            
            self.setObject('objectVersion', self.classVersion)
            self.setObject('updateVersion', self.classUpdateVersion)
            
            #Reset the SSL protection to what it was before we disabled it
            self.setObject('SSLRequired', sslState)

    security.declarePublic('denied')
    def denied(self):
        "Generic access denied"
        return 'Access to this object is denied'

    security.declarePublic('submitChanges')
    def submitChanges(self, text='Submit Changes', name="Submit"):
        "draw the submit changes button so we don't need an object for that"
        return '<input type="submit" name="%s" value="%s" class="submitChanges submit">' % (name, text)

    security.declarePublic('menuRenderer')
    def menuRenderer(self, renderer, seq, columns=0, containerClasses=""):
        "use a menuRenderer on this sequence"
        return NestedListURL.listRenderer(renderer, seq, columns, containerClasses=containerClasses)

    security.declarePrivate('getPopulatorInformation')
    def getPopulatorInformation(self):
        "return a string that the pair for this method can accept to recreate that data"
        objectInfo = ['%s %s %s' % (name, item.meta_type, item.populatorInformation()) for name, item in self.objectItems() if hasattr(item, 'populatorInformation')]
        return '\n'.join(objectInfo)

    security.declarePrivate('loadPopulatorInforation')
    def loadPopulatorInformation(self, lines):
        'load this string back into the various objects'
        for line in lines:
            #The first part of the entry is always the id of the object
            #and the second is the meta_type only hand off if both match
            try:
                name, meta_type, data = line.split(' ', 2)
                item = getattr(self, name)
                if item.meta_type == meta_type:
                    item.populatorLoader(data)
            except (IndexError, AttributeError):
                pass

    security.declareProtected('Reset CompoundDoc Name:DANGEROUS', 'resetId')
    def resetId(self, name):
        'Reset the id of this compounddoc when an id mismatch occurs'
        self.id = name
        
    security.declareProtected('View', 'deleteDoc')
    def deleteDoc(self, returnPath='', message=''):
        "construct a deleteDoc url with a proper return path"
        temp = []
        if getSecurityManager().getUser().has_permission('Delete objects', self.aq_parent):
            message = message or "Delete This Document"
            if returnPath:
                temp.append(self.input_hidden('deleteDocReturnPath', var=returnPath))
            temp.append(self.create_button('deleteDocSubmit', message))
        return ''.join(temp)
    
    #backwards compat
    deleteDocUrl = deleteDoc
        
    security.declarePrivate('deleteDocProcessor')
    def deleteDocProcessor(self, form):
        'delete this document'
        if 'deleteDocSubmit' in form and getSecurityManager().checkPermission('Delete objects', self.aq_parent):
            self.aq_parent.manage_delObjects([self.getId()])
            url = form.pop('deleteDocReturnPath', None)
            url = url or self.REQUEST.environ.get('HTTP_REFERER', None) or self.aq_parent.absolute_url()
            self.REQUEST.other['redirectTo'] = url
            #have to clear the form so that we don't try to process anything in it for a document that is to be removed causing it to be reindexed
            form.clear()
            
    security.declareProtected('View', 'addDoc')
    def addDoc(self, container, returnScript, profile, message='', name='', prepend='', autoType=''):
        "construct a creation form for adding a cdoc"
        temp = []
        if getSecurityManager().getUser().has_permission('Add CompoundDoc', container):
            message = message or "Add Document"
            temp.append(self.input_hidden('containerPath', var='/'.join(container.getPhysicalPath()), containers=('addDoc',) ))
            temp.append(self.input_hidden('returnScriptPath', var='/'.join(returnScript.getPhysicalPath()), containers=('addDoc',) ))
            temp.append(self.input_hidden('profile', var=profile, containers=('addDoc',) ))
            temp.append(self.input_hidden('prepend', var=prepend, containers=('addDoc',) ))
            temp.append(self.input_hidden('autoType', var=autoType, containers=('addDoc',) ))
            temp.append(self.input_hidden('name', var=name, containers=('addDoc',) ))
            temp.append(self.create_button('addDocSubmit', message))
        return ''.join(temp)
        
    security.declarePrivate('addDocProcessor')
    def addDocProcessor(self, form):
        'add a new document'
        addForm = form.pop('addDoc', None)
        if 'addDocSubmit' in form and addForm is not None:
            containerPath = addForm.pop('containerPath', '')
            container = None
            if containerPath:
                container = self.restrictedTraverse(containerPath, None)
            
            returnScriptPath = addForm.pop('returnScriptPath', '')
            returnScript = None
            if returnScriptPath:
                returnScript = self.restrictedTraverse(returnScriptPath, None)
            
            profile = addForm.pop('profile', None)
            prepend = addForm.pop('prepend', None)
            autoType = addForm.pop('autoType', None)
            name = addForm.pop('name', None)
            
            if container is not None and returnScript is not None and profile is not None:
                if getSecurityManager().checkPermission('Add CompoundDoc', container):
                    doc = container.manage_addProduct['CompoundDoc'].manage_addCompoundDoc(name, profile=profile,
                      redir=0, prepend=prepend, returnObject=1, autoType=autoType)
                    url = returnScript(self, doc)
                    self.REQUEST.other['redirectTo'] = url

    security.declareProtected('Upgrade CompoundDoc', 'rebuildCDocUpgraderCatalog')
    def rebuildCDocUpgraderCatalog(self):
        "rebuild the CDocUpgrader catalog"
        root = self.getPhysicalRoot()

        if not hasattr(root, 'CDocUpgrader'):
            root._setObject('CDocUpgrader', ZCatalog('CDocUpgrader'))
            catalog = getattr(root, 'CDocUpgrader')
            catalog.manage_delColumn(catalog.schema())
            catalog.manage_delIndex(catalog.indexes())
            catalog.addColumn('objectVersion')
            catalog.addColumn('updateVersion')
            catalog.addColumn('id')
            catalog.addColumn('profile')
            catalog.addIndex('path','PathIndex')
            catalog.addIndex('id', 'FieldIndex')
            catalog.addIndex('profile', 'FieldIndex')
            catalog.addIndex('objectVersion', 'FieldIndex')
            catalog.addIndex('updateVersion', 'FieldIndex')
                       
            catalog.ZopeFindAndApply(root, obj_metatypes=['CompoundDoc'],
                                                search_sub=1,
                                                apply_func=catalog.catalog_object)
        return 'Done'        
        
        
    security.declareProtected('Upgrade CompoundDoc', 'upgradeCdoc')
    def upgradeCdoc(self):
        "upgrade this cdoc"
        self.REQUEST.other['okayToRunNotification'] = 0
        self.upgradeAll()
        return 'Done'
        
    security.declareProtected('Upgrade CompoundDoc', 'upgradeAllCdocs')
    def upgradeAllCdocs(self, path=None):
        "do upgrades on all cdocs"
        self.REQUEST.other['okayToRunNotification'] = 0
        root = self.getPhysicalRoot()
        catalog = root.CDocUpgrader
        
        
        upgradeMe = self.getUpgradeableRecords(path=path)

        removeRecordFromCatalog = utility.removeRecordFromCatalog
        
        write = self.REQUEST.RESPONSE.write
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        for record in com.db.subTrans(upgradeMe,  100):
            write('%s (%s)\n' % (record.getPath(), record.objectVersion))
            try:
                cdoc = record.getObject()
                cdoc_upgradeAll = cdoc.upgradeAll
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError, IndexError, AttributeError):
                cdoc = None
                cdoc_upgradeAll = None
                
            if cdoc is not None and cdoc_upgradeAll is not None:
                cdoc_upgradeAll()
                catalog.catalog_object(cdoc)
                cdoc._p_deactivate()
            else:
                removeRecordFromCatalog(catalog, record)                
            self._p_jar.cacheGC()
 
        write('Done')

    security.declareProtected('Upgrade CompoundDoc', 'upgradeAllCdocsInFolder')
    def upgradeAllCdocsInFolder(self):
        "do upgrades on all cdocs"
        self.upgradeAllCdocs(path='/'.join(self.getCompoundDocContainer().getPhysicalPath()))

    security.declarePrivate('getUpgradeableRecords')
    def getUpgradeableRecords(self, path=None):
        "get all the records for what we can upgrade"
        classVersion = Base.classVersion
        classUpdateVersion = Base.classUpdateVersion
        query = {}
        if path is not None:
            query['path'] = path
        for record in self.getPhysicalRoot().CDocUpgrader(query):
            if record.objectVersion < classVersion or record.updateVersion < classUpdateVersion:
                yield record

    security.declarePrivate('configAddition')
    def configAddition(self):
        "create an addition that allows upgrading cdocs"
        url = self.absolute_url_path()
        return '''<a href="%s/rebuildCDocUpgraderCatalog">Rebuild Catalog</a><br>
        <a href="%s/upgradeAllCdocs">Upgrade All Cdocs</a><br>
        <a href="%s/upgradeAllCdocsInFolder">Upgrade Cdocs in Folder</a><br>
        <a href="%s/upgradeCdoc">Upgrade This Cdoc</a>''' % (url, url, url, url)

Globals.InitializeClass(CompoundDoc)
