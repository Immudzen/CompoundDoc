# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import OFS.Image
from basepicture import BasePicture

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from incrementalrender import IncrementalRender
import utility
import magicfile
import PIL

class Picture(BasePicture):
    "Image class"

    meta_type = "Picture"
    security = ClassSecurityInfo()
    imagesrc = ''
    data = ''
    image = ''
    fileSize = ''
    deletion = 1
    preview = 1
    showTags = 1
    showAlt = 1
    showURL = 1
    url = ''
    alt = ''
    tags = ''
    thumbnail = None
    resizeOnUpload = 0
    resaveOnUpload = 1

    classConfig = BasePicture.classConfig.copy()
    classConfig['deletion'] = {'name':'deletion', 'type': 'radio'}
    classConfig['preview'] = {'name':'preview', 'type': 'radio'}
    classConfig['showTags'] = {'name':'showTags', 'type': 'radio'}
    classConfig['resaveOnUpload'] = {'name':'Resave Images on Upload', 'type': 'radio'}
    classConfig['tags'] = {'name':'tags', 'type': 'string'}
    classConfig['alt'] = {'name':'alt', 'type': 'string'}
    classConfig['url'] = {'name':'url', 'type': 'string'}
    classConfig['showAlt'] = {'name':'showAlt', 'type': 'radio'}
    classConfig['showURL'] = {'name':'showURL', 'type': 'radio'}
    classConfig['resizeOnUpload'] = {'name':'Resize uploaded images?', 'type': 'radio'}

    configurable = BasePicture.configurable + ('deletion', 'showAlt', 'showTags', 'showURL', 
        'preview', 'scriptChangePath',  'resizeOnUpload', 'resaveOnUpload')
    attr_notified = set(['url',  'alt',  'tags',  'showUrl',  'showAlt',  'showTags',  'preview',  'deletion',  'data'])

    security.declareProtected('View management screens', 'edit')
    def edit(self, showTags=None, showAlt=None, showURL=None, preview=None, *args, **kw):
        "Inline edit short object"
        temp = []
        if preview is None:
            preview = self.getConfig('preview')
        if self.exists() and preview:
            object = self.data
            width,height = object.width, object.height
            size = self.getFileSize()
            if not size:
                self.setFileSize()
                size = self.getFileSize()
            type = object.content_type
            format = '<p>Preview: %s  (%s px/%s px) %s %s </p>'
            temp.append(format % (self.small(), width, height, size, type))
        
        if showTags is None:
            showTags = self.getConfig('showTags')
        if showTags:
            temp.append(self.editSingleConfig('tags'))
        
        if showAlt is None:
            showAlt = self.getConfig('showAlt')
        if showAlt:
            temp.append(self.editSingleConfig('alt'))
        
        if showURL is None:
            showURL = self.getConfig('showURL')
        if showURL:
            temp.append(self.editSingleConfig('url'))
        
        temp.append('<div>%s</div><p>Click [Browse] to enter the picture</p>' % self.input_file('data'))
        if self.getConfig('deletion') and self.exists():
            temp.append('<p>Delete Current Image: %s </p>' % self.check_box('_del', 'Y'))
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "This is the object specific edit stuff"
        if dict.pop('_del',None) == 'Y' and self.getConfig('deletion'):
            self.delObjects(('data','imagesrc','thumbnail', 'fileSize'))

        if dict.get('data', None):  #don't process if data does not have anything in it
            temp = OFS.Image.Image('data',self.getId(),dict['data'])
            filename, remove_after = utility.createTempFile(temp.data)
            content_type = magicfile.magic(filename)
            if content_type.startswith('image'):
                if self.getConfig('resizeOnUpload'):
                    temp = self.resizeImage(filename)
                elif self.getConfig('resaveOnUpload'):
                    resaved = utility.resaveExistingImage(filename, 'data')
                    if resaved is not None:
                        temp = resaved
                self.setObject('data', temp)
                self.makeThumbnail()
                self.setFileSize()
                self.storeContentType(content_type)
            utility.removeTempFile(filename, remove_after)    
        try:
            del dict['data']
        except KeyError:
            pass
                
    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "cache some information after this object has been modified"
        if self.hasBeenModified():
            self.updateImageSrcCache()

    security.declareProtected('Change CompoundDoc', 'resizeImage')
    def resizeImage(self,  filename):
        "generate this image"
        image=PIL.Image.open(filename)
        if image.mode != self.getConfig('color'):
            image=image.convert(self.getConfig('color'))
        maxWidth = self.getConfig('width')
        maxHeight = self.getConfig('height')
        (x, y) = image.size
        if x> maxWidth:
            y = y * maxWidth / x
            x = maxWidth
        if y> maxHeight:
            x = x * maxHeight / y
            y = maxHeight
        if x == 0:
            x = 1
        if y == 0:
            y = 1
        image = image.resize((x, y))
        tempFile = utility.saveImage(image, self.getConfig('format'))
        newImage = OFS.Image.Image('data', 'data', tempFile)
        newImage.width = x
        newImage.height = y
        return newImage

    security.declareProtected('Change CompoundDoc', 'resaveExistingImage')
    def resaveExistingImage(self):
        "reisze existing images"
        if self.exists():
            filename, remove_after = utility.createTempFile(self.data.data)
            content_type = magicfile.magic(filename)
            if content_type.startswith('image'):
                if self.getConfig('resaveOnUpload'):
                    temp = utility.resaveExistingImage(filename, 'data')
                    beforeSize = utility.fileSizeToInt(self.getFileSize())
                    if temp is not None:
                        afterSize = utility.fileSizeToInt(utility.fileSizeString(temp.data))
                    else:
                        afterSize = beforeSize
                    if temp is not None and afterSize < beforeSize:
                        self.setObject('data', temp)
                        #have to redo the content_type after we modify the image in case it has changed
                        content_type = magicfile.magic(filename)
                        self.setFileSize()
                        self.storeContentType(content_type)
            utility.removeTempFile(filename, remove_after) 

    security.declareProtected('Change CompoundDoc', 'resizeExistingImage')
    def resizeExistingImage(self):
        "reisze existing images"
        if self.exists():
            filename, remove_after = utility.createTempFile(self.data.data)
            content_type = magicfile.magic(filename)
            if content_type.startswith('image'):
                if self.getConfig('resizeOnUpload'):
                    temp = self.resizeImage(filename)
                    self.setObject('data', temp)
                    #have to redo the content_type after we modify the image in case it has changed
                    content_type = magicfile.magic(filename)
                    self.makeThumbnail()
                    self.setFileSize()
                    self.storeContentType(content_type)
                    self.updateImageSrcCache()
            utility.removeTempFile(filename, remove_after)  

    security.declareProtected('Change CompoundDoc', 'updateImageSrcCache')
    def updateImageSrcCache(self):
        "update the imagesrc cache string"
        if self.exists():
            decode = {}
            decode['height'] = self.data.height
            decode['width'] = self.data.width
            if utility.dtmlFree(self.alt):
                decode['alt'] = self.convert(self.alt)
            else:
                decode['alt'] = self.alt

            decode['tags'] = self.tags

            inc = IncrementalRender(decode)
            imagesrc = '<img src="%(url)s" width="%(width)s" height="%(height)s" alt="%(alt)s" %(tags)s %(additionalAttributes)s >' % inc
            url = self.url
            if url and (not utility.dtmlFree(url) or '://' in url):
                #the replace part is needed because the url might have % in them for spaces etc and it needs to be escaped
                imagesrc = '<a href="%s">%s</a>' % (url.replace('%', '%%'),imagesrc)
            self.setObject('imagesrc', imagesrc)

    security.declareProtected('View', 'view')
    def view(self, urlCallable=None, parent=None, additionalAttributes=''):
        "Render page"
        parent = parent or self.getCompoundDocContainer()
        if self.exists():
            decode = {}
            decode['url'] = self.absolute_url_path_extension()
            decode['additionalAttributes'] = additionalAttributes
            image = self.imagesrc % decode

            url = self.url
            href = None
            if urlCallable is not None:
                href = urlCallable(url)
            elif url and utility.dtmlFree(url) and '://' not in url:
                item = parent.restrictedTraverse(url,None)
                if item is not None:
                    href = item.absolute_url_path()
                    
            if href is not None:
                return '<a href="%s">%s</a>' % (href,image)
            return image
        return ""

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        if self.exists():
            return str(self.alt)
        else:
            return ""

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.fixupAlt()
        self.fixupUrl()
        self.fixupTags()
        self.removeAttributeText()
        self.fixFileId()
        self.percentEscape()
        self.addAdditionalVarsSupport()

    security.declarePrivate('fixupAlt')
    def fixupAlt(self):
        "fix up the alt attribute"
        alt = getattr(self, 'alt', '')
        if getattr(alt, 'meta_type', None) != 'AttributeText':
            self.addRegisteredObject('alt', 'AttributeText', data=alt)
    fixupAlt = utility.upgradeLimit(fixupAlt, 141)
            
    security.declarePrivate('fixupUrl')
    def fixupUrl(self):
        "fix up the url attribute"
        url = getattr(self, 'url', '')
        if getattr(url, 'meta_type', None) != 'AttributeText':
            self.addRegisteredObject('url', 'AttributeText', data=url)
    fixupUrl = utility.upgradeLimit(fixupUrl, 141)
            
    security.declarePrivate('fixupTags')
    def fixupTags(self):
        "fix up the tags attribute"        
        tags = getattr(self, 'tags', '')
        if getattr(tags, 'meta_type', None) != 'AttributeText':
            self.addRegisteredObject('tags', 'AttributeText', data=tags)
    fixupTags = utility.upgradeLimit(fixupTags, 141)

    security.declarePrivate('removeAttributeText')
    def removeAttributeText(self):
        "remove the attributetext items and replace them with basic attributes"
        for name, value in self.objectItems('AttributeText'):
            self.delObjects((name,))
            self.setObject(name, value.data)
        self.updateImageSrcCache()
    removeAttributeText = utility.upgradeLimit(removeAttributeText, 148)
            
    security.declarePrivate('percentEscape')
    def percentEscape(self):
        "escape any % that might be in the url so that subs work right"
        self.updateImageSrcCache()
    percentEscape = utility.upgradeLimit(percentEscape, 159)            
            
Globals.InitializeClass(Picture)
import register
register.registerClass(Picture)
