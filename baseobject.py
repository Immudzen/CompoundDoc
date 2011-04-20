# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import Persistence
from zLOG.EventLogger import log_write
import zLOG
import os.path
from Globals import DTMLFile
from Acquisition import aq_base
import com.javascript
import com.css
import com.detection

from OFS.ObjectManager import ObjectManager

class BaseObject(Persistence.Persistent, ObjectManager, object):
    "This is a BaseObject that defines variables and functions in common to many items"

    meta_type = "BaseObject"
    security = ClassSecurityInfo()

    security.declareObjectProtected('View')

    UserObject = 0 #Used to determine if items should be observable/observing/keep a userModificationTime
    configureable = 1
    _objects = ()
    updateReplaceList = ()

    security.declareProtected('View management screens', 
        'manage_page_style_css', 'manage_page_header',
        'manage_page_footer', 'manage', 'manage_workspace')

    mainEditCSSDataMSIE = open(os.path.join(os.path.dirname(__file__), 'data', 'mainEditMSIE.css')).read()
    manage_page_style_css = DTMLFile('dtml/manage_page_style.css', globals())

    security.declareProtected('View', 'title_or_id')
    def title_or_id(self):
        """Return the title if it is not blank and the id otherwise.
        """
        title=self.title
        if callable(title):
            title=title(mode='view')
        if title: return title
        return self.getId()

    def getConfig(self, name):
        "get the config item of this name, try to get it remotely if we don't have it locally"
        if name in self.__dict__:
            return getattr(self,name)
        obj = self.getConfigObject()
        if obj is not None:
            try:
                return getattr(obj, name)
            except AttributeError:
                pass
        return getattr(self,name)

    def getConfigObject(self):
        "return the config object that matches the current object"
        configDoc = self.getConfigDoc()
        if configDoc is not None:
            cdoc = self.getCompoundDoc()
            selfPath = self.getPath()
            cdocPath = cdoc.getPath()
            if selfPath != cdocPath:
                path = selfPath.replace(cdocPath+'/', '')
            else:
                path = ''
            obj = configDoc.unrestrictedTraverse(path, None)
            return obj    

    security.declarePublic('gzip_extension')
    def gzip_extension(self):
        "see if gzip works and return .gz or '' based on that"
        return '.gz' if com.detection.gzip_enabled(self.REQUEST) else ''

    def manage_page_header(self):
        "draw the manage page header string"
        language = self.getLanguage()
        encoding = self.getEncoding()
        cdocUrl = self.absolute_url_path()
        gzip_extension = self.gzip_extension()
        gzip_enabled = com.detection.gzip_enabled(self.REQUEST)

        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % encoding)

        temp = ['''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
            <html lang="%s"><head>
            <META http-equiv="Content-Type" content="text/html; charset=%s">
            <title>CompoundDoc</title>''' % (language,encoding)]
        
        if getattr(self,'cssDocEdit',None):
            temp.append('<link rel="stylesheet" type="text/css" href="%s/cssDocEditWrapper">' % cdocUrl)

        if self.profile:
            profileCSS = getattr(self, 'cssDocEdit%s' % self.profile, None)
            if profileCSS is not None:
                temp.append('<link rel="stylesheet" type="text/css" href="%s/cssDocEditProfileWrapper">' % cdocUrl)

        if 'MSIE' in self.REQUEST.HTTP_USER_AGENT:
            temp.append('<link rel="stylesheet" type="text/css" href="%s/mainEditCSSMSIE">' % cdocUrl)
        
        temp.append('''
        <link rel="stylesheet" type="text/css" href="http://s3.amazonaws.com/media.webmediaengineering.com/CompoundDoc/mainEdit_1{gz}.css">        
        '''.format(gz=gzip_extension))
        temp.append(com.css.default_css(gzip_enabled, self.getJQueryCSSTheme()))
        temp.append(com.javascript.default_javascript(gzip_enabled))
        temp.append(com.javascript.document_ready([com.javascript.color_picker_init(), 
            com.javascript.nice_submit_button(),
            com.javascript.lightbox_init(),
            com.javascript.tabs_init('control_tabs')]))
        temp.append('</head><body>')
        return ''.join(temp)

    security.declareProtected('View', 'changeCallingContext')
    def changeCallingContext(self, obj, meta_types = None):
        "change the acquisition path of this item to a the context of this object"
        "this is used to make a remote script be treated as if it where in the acquisition path"
        if not meta_types or (meta_types and obj.meta_type in meta_types):
            return aq_base(obj).__of__(self)

    security.declarePrivate('getLanguage')
    def getLanguage(self):
        return getattr(self, 'CompoundDocEditLanguage', 'en')

    security.declarePrivate('getEncoding')
    def getEncoding(self):
        return getattr(self, 'CompoundDocEditEncoding', 'iso-8859-1')
   
    security.declarePrivate('getJQueryCSSTheme')
    def getJQueryCSSTheme(self):
        return getattr(self, 'JQueryCSS', 'smoothness')

    security.declareProtected('View management screens', 'mainEditCSSMSIE')
    def mainEditCSSMSIE(self):
        "return the IE specific hacks for the CSS due to it not supporting css2 selectors"
        self.REQUEST.RESPONSE.setHeader('Content-Type','text/css')
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=259200')   #72 hours caching
        return self.mainEditCSSDataMSIE

    security.declareProtected('View management screens', 'cssDocEditWrapper')
    def cssDocEditWrapper(self):
        "wrap the cssDocEdit object for temp security workaround"
        self.REQUEST.RESPONSE.setHeader('Content-Type','text/css')
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=259200')   #72 hours caching
        return self.cssDocEdit()

    security.declareProtected('View management screens', 'cssDocEditProfileWrapper')
    def cssDocEditProfileWrapper(self):
        "wrap the cssDocEditProfile object for temp security workaround"
        self.REQUEST.RESPONSE.setHeader('Content-Type','text/css')
        self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=259200')   #72 hours caching
        script = getattr(self,'cssDocEdit%s' % self.profile,'')
        if callable(script):
            return script()
        return ''

    security.declareProtected('View management screens', 'manage_page_footer')
    def manage_page_footer(self):
        "draw the manage page header string"
        return '''</div></form></body></html>'''

    security.declarePrivate('__init__')
    def __init__(self, name):
        "Initialize a new base"
        self.id = name

    security.declarePrivate('__hash__')
    def __hash__(self):
        "Return the hash of this object which is its id"
        return id(self)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return str(self.view())

    security.declarePublic('log')
    def log(self, short="", longMessage="", error_level=zLOG.INFO, reraise=0):
        "Log an error to a file"
        log_write(self.getId(), error_level, str(short), str(longMessage), None)

    security.declarePrivate('getMenuSelected')
    def getMenuSelected(self):
        "get the current menu entry that is selected"
        return self.REQUEST.other.get('menuSelected', {}).get(self.getId(), None)

    security.declarePrivate('drawMenuSelected')
    def drawMenuSelected(self):
        "Draw the currently selected menu item"
        selected = self.getMenuSelected()
        if selected is not None:
            render = getattr(self, selected, None)
            if render is not None:
                return render.edit()
        return ''

    security.declarePrivate('getPath')
    def getPath(self):
        """Return the physical path for an object."""
        return '/'.join(self.getPhysicalPath())

    security.declarePrivate('getRelativePath')
    def getRelativePath(self, object):
        "This will return the relative path to a compounddoc from another compounddoc"
        cdocPath = self.getCompoundDoc().getPath()
        if cdocPath == object.getCompoundDoc().getPath():
            return self.getPath().replace(cdocPath+'/', '')
        else:
            return self.getPath()

    security.declarePrivate('getDrawMode')
    def getDrawMode(self):
        "Get the draw mode of this document from the REQUEST"
        try:
            return self.REQUEST.other.get('renderingMode','view')
        except AttributeError:
            return 'view'

    security.declarePrivate('setDrawMode')
    def setDrawMode(self, mode=None):
        "set the current rendering mode"
        if mode is not None:
            try:
                self.REQUEST.other['renderingMode'] = mode
            except AttributeError: #This catches the case where REQUEST does not exist during zope startup
                pass

    security.declarePrivate('getHref')
    def getHref(self, path):
        "return an a href to this path for editing"
        if path:
            cdoc = self.getCompoundDoc()
            script = cdoc.restrictedTraverse(path, None)
            if script is not None:
                try:
                    parent = script.aq_parent
                except AttributeError:
                    parent = self.getCompoundDocContainer()
                try:
                    return '<a href="%s/manage">Edit: %s</a> <a href="%s/manage">Parent Edit: %s</a>' % (
                        script.absolute_url_path(), script.title_or_id(),
                        parent.absolute_url_path(), parent.title_or_id())
                except AttributeError:
                    return ''
            elif '/' in path:
                path = path[:path.rfind('/')]
                parent = cdoc.restrictedTraverse(path, None)
                if parent is not None:
                    try:
                        return '<a href="%s/manage">Parent Edit: %s</a>' % (
                            parent.absolute_url_path(), parent.title_or_id())
                    except AttributeError:
                        return ''
        return ''

Globals.InitializeClass(BaseObject)

