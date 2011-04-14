# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject
import OFS.Image
import magicfile
from Acquisition import aq_base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility
import urllib
import stat
import os
import os.path
import ZODB.blob

class File(UserObject):
    "File Class"

    meta_type = "File"
    security = ClassSecurityInfo()
    data = ''
    fileSize = ''
    openFileInNewWindow = 0
    deletion = 1
    showPreview = 1
    showOpenInNewWindow = 0
    urlExtension = ''
    title = 'Download File'
    filename = 'file'
    fileUrl = ''

    classConfig = {}
    classConfig['deletion'] = {'name':'deletion', 'type': 'radio'}
    classConfig['showPreview'] = {'name':'preview', 'type': 'radio'}
    classConfig['showOpenInNewWindow'] = {'name':'showOpenInNewWindow', 'type': 'radio'}
    classConfig['openFileInNewWindow'] = {'name':'openFileInNewWindow', 'type': 'radio'}
    classConfig['urlExtension'] = {'name':'urlExtension', 'type':'tokens'}
    classConfig['title'] = {'name':'title', 'type':'string'}
    classConfig['filename'] = {'name':'filename', 'type':'string'}
    classConfig['fileUrl'] = {'name':'File Url', 'type':'string'}

    updateReplaceList = ('deletion', 'showPreview', 'showOpenInNewWindow', 'urlExtension', 'openFileInNewWindow')

    configurable = ('openFileInNewWindow',)

    security.declarePrivate('validate_filename')
    def validate_filename(self, value):
        "remove all leading and trailing whitespace"
        try:
            return value.strip()
        except AttributeError:
            return value

    security.declarePrivate('validate_urlExtension')
    def validate_urlExtension(self, value):
        "make sure we get rid of this if the value is false"
        if value:
            return value
        else:
            return ''

    security.declarePublic("__bobo_traverse__")
    def __bobo_traverse__(self, REQUEST, name):
        "__bobo_traverse__"
        if name.startswith('ver_'):
            name = self.REQUEST.TraversalRequestNameStack.pop()
            self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=315360000')
            self.REQUEST.RESPONSE.setHeader('Expires', 'Thu, 01 Dec 2030 12:00:0')
        extensions = []
        if self.getConfig('urlExtension'):
            extensions = self.getConfig('urlExtension')
        stack = self.REQUEST.TraversalRequestNameStack
        if stack and stack[0] in extensions:
            extension = stack[0]
            self.REQUEST.TraversalRequestNameStack = []
            return getattr(self, extension)
        if self.exists() and name == self.filename:
            if self.fileUrl:
                return self.redir
            object = self.data
            type = object.content_type
            if type == 'application/msword' or type == "":
                type = 'application/octet-stream'
                object.content_type = type
            self.REQUEST.RESPONSE.setHeader('Content-Type',type)
            return object.index_html
        elif hasattr(self, name):
            return getattr(self, name)
    
    security.declareProtected('View', 'redir')
    def redir(self):
        "redirect to the real file"
        return self.REQUEST.RESPONSE.redirect(self.fileUrl)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        if self.showPreview:
            preview = self.preview()
            if preview:
                temp.append(preview)
        temp.append(self.editSingleConfig('title'))
        temp.append(self.editSingleConfig('filename'))
        temp.append(self.editSingleConfig('fileUrl'))
        temp.append('<p>%s</p>' % self.input_file('data'))
        if self.exists() and self.deletion:
            temp.append('<p>Delete Current File: %s </p>' % self.check_box('_del', 'Y'))
        if self.showOpenInNewWindow:
            temp.append('<p>Open File in New Window: %s </p>' % self.true_false('openFileInNewWindow', self.openFileInNewWindow,0))
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "This is the object specific edit stuff"
        delFile = dict.pop('_del', None)
        if delFile == 'Y':
            self.delObjects(('data','fileSize'))
        
        data = dict.pop('data', None)
        if data is not None:
            try:
                temp = OFS.Image.File(id='data',title=self.getId(),file=data)
                self.setObject('data', temp)
                self.setFileSize()
                self.updateFileContentType() 
            except ValueError: #catches no file uploaded
                pass

    def updateFileContentType(self):
        "Update the content type of the installed file"
        if self.exists():
            if self.hasObject('data'):
                file_obj = aq_base(self.data)
                if hasattr(file_obj, 'data'):
                    filename, remove_after = utility.createTempFile(file_obj.data)
                    file_obj.content_type = magicfile.magic(filename)
                    utility.removeTempFile(filename, remove_after)

    def storeContentType(self, content_type):
        "store the content type for to this object"
        if self.exists():
            self.data.content_type = content_type

    security.declareProtected('View', 'getFileSize')
    def getFileSize(self):
        "Return the file size of this object"
        return self.fileSize

    security.declareProtected('View', 'view')
    def view(self, title='', extension='', disableExtension=None, query=None, url=None, showSize=1, openFileInNewWindow=None):
        "Render page"
        queryString = ''
        if query is not None:
            queryString = '?' + urllib.urlencode(query)
        if not self.fileUrl and self.data == "":
            pass
        else:
            if not title:
                title = self.title
            if url is None:
                url = self.getUrlWithExtension(extension, disableExtension)
            openFileInNewWindow = openFileInNewWindow if openFileInNewWindow is not None else self.getConfig('openFileInNewWindow')
            if openFileInNewWindow:
                target = 'target="_blank"'
            else:
                target = ''
            if self.fileUrl:
                fileSize = ''
            elif showSize:
                fileSize = self.getFileSize()
                if fileSize:
                    fileSize = '(%s)' % fileSize
            else:
                fileSize = ''
            return '<a href="%s%s" %s>%s</a> %s' % (url, queryString, target, title, fileSize)
        return ""

    security.declareProtected('View', 'getUrlWithExtension')
    def getUrlWithExtension(self, extension='', disableExtension=None):
        "process for a url extension and make sure it goes to a valid location otherwise just give back our current url"
        urlExtension = self.getConfig('urlExtension')
        if urlExtension and not (extension and extension in urlExtension):
            extension = urlExtension[0]
        if extension and not disableExtension:
            try:
                self.getCompoundDocContainer().restrictedTraverse(extension)
                return urllib.quote(os.path.join(self.absolute_url_path(), self.filename, extension))
            except KeyError:
                pass

        if self.fileUrl:
            return urllib.quote(self.fileUrl)
        else:
            version = 'ver_%s' % int(self.data.bobobase_modification_time().timeTime())
            return os.path.join(self.absolute_url_path(), version, urllib.quote(self.filename))

    security.declarePrivate('setFileSize')
    def setFileSize(self):
        "Store the file size of this object"
        try:
            fileSize = utility.fileSizeString(self.data.size)
            self.setObject('fileSize', fileSize)
        except AttributeError:
            pass

    security.declareProtected("Access contents information", 'exists')
    def exists(self):
        "Check if object has data in it"
        try:
            return bool(self.data and hasattr(aq_base(self.data), 'data') or self.fileUrl)
        except AttributeError:
            return 0

    security.declareProtected('View management screens', 'preview')
    def preview(self):
        "Preview of a file"
        if self.exists():
            if self.fileUrl:
                url = self.fileUrl
                fileType = ''
                fileSize = ''
            else:
                version = 'ver_%s' % int(self.data.bobobase_modification_time().timeTime())
                url = os.path.join(self.absolute_url_path(), version, urllib.quote(self.filename))
                fileType = self.data.content_type
                fileSize = self.getFileSize()
            title = self.title

            return '<p>Preview: <a href="%s">%s</a> (%s) %s</p>' % (url, title, fileSize, fileType)
        return ""

    security.declarePrivate("PrincipiaSearchSource")
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        obj = self.data
        search = [self.title, self.filename]
        if self.exists() and not self.fileUrl and obj.content_type.count("text"):
            if isinstance(obj.data, ZODB.blob.Blob):
                search.append(obj.data.open('r').read())
            else:
                search.append(str(obj.data))
        return ' '.join(search)

    security.declarePrivate('dataLoader')
    def dataLoader(self, dict):
        "load the data from this dict into this object"
        self.before_manage_edit(dict)
        self.filename.manage_edit(dict['filename'])
        self.title.manage_edit(dict['title'])

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.updateTitle()
        self.updateFilename()
        self.updatePreview()
        self.removeAttributeText()
        self.changeUrlExtension()
        self.fixFileId()

    security.declarePrivate('updateTitle')
    def updateTitle(self):
        "update the title object from a string to an AttributeText"
        if isinstance(self.title, basestring):
            return
        if getattr(self.title, 'meta_type', None) != 'AttributeText':
            if 'title' in self.objectConfig and hasattr(self.objectConfig.title, 'value'):
                self.addRegisteredObject('title', 'AttributeText', data=self.title, title=self.objectConfig.title.value)
            else:
                self.addRegisteredObject('title', 'AttributeText', data='')
    updateTitle = utility.upgradeLimit(updateTitle, 141)
            
    security.declarePrivate('updateFilename')            
    def updateFilename(self):
        "update the filename object from a string to an AttributeText"
        if getattr(self.filename, 'meta_type', None) != 'AttributeText' and hasattr(self.objectConfig.filename, 'value'):
            self.addRegisteredObject('filename', 'AttributeText', data=self.filename, title=self.objectConfig.filename.value)
        if getattr(self.filename, 'meta_type', None) != 'AttributeText':
            self.addRegisteredObject('filename', 'AttributeText', data='')
    updateFilename = utility.upgradeLimit(updateFilename, 141)
            
    security.declarePrivate('updatePreview')        
    def updatePreview(self):
        "fix the preview setting up"            
        if 'preview' in self.__dict__:
            self.setObject('showPreview', self.preview)
            self.delObjects(('preview',))
    updatePreview = utility.upgradeLimit(updatePreview, 141)

    security.declarePrivate('removeAttributeText')
    def removeAttributeText(self):
        "remove the attributetext items and replace them with basic attributes"
        self.fixupTitle()
        self.fixupFileName()
    removeAttributeText = utility.upgradeLimit(removeAttributeText, 150)

    security.declarePrivate('fixupFileName')
    def fixupFileName(self):
        "fixup the filename attribute"
        try:
            filename = self.filename.data
            self.delObjects(('filename',))
            self.setObject('filename', filename)
        except AttributeError:
            pass

    security.declarePrivate('fixupTitle')
    def fixupTitle(self):
        "fixup the title attribute"
        try:
            title = self.title.data
            self.delObjects(('title',))
            self.setObject('title', title)
        except AttributeError:
            pass

    security.declarePrivate('changeUrlExtension')
    def changeUrlExtension(self):
        "change urlExtension to a sequence"
        if self.urlExtension:
            self.setObject('urlExtension', self.urlExtension.split())
    changeUrlExtension = utility.upgradeLimit(changeUrlExtension, 151)
    
    security.declarePrivate('fixFileId')
    def fixFileId(self):
        "change urlExtension to a sequence"
        if self.data:
            self.data.__name__ = 'data'
    fixFileId = utility.upgradeLimit(fixFileId, 152)    

            
Globals.InitializeClass(File)
import register
register.registerClass(File)
