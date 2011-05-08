# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import OFS.Image
from basepicture import BasePicture

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import utility
import magicfile
import PIL
import com.html
import com.detection
from string import Template

image_template = Template('<img src="$url" width="$width" height="$height" alt="$alt" $tags $additionalAttributes>')

class ImageFilter(BasePicture):
    "Image class"

    security = ClassSecurityInfo()
    meta_type = "ImageFilter"
    image = ''
    data = ''
    location = ''
    fileSize = ''
    imagesrc = '' #obsolete
    imagesrc_template = ''
    thumbnail = None
    
    classConfig = BasePicture.classConfig.copy()
    classConfig['location'] = {'name':'Location of Image:', 'type': 'string'}
        
    updateReplaceList = ('format', 'color', 'location', )
    
    configurable = BasePicture.configurable + ('deletion', 'location')
    attr_notified = set(['format',  'color',  'width',  'height'])
    
    security.declareProtected('View management screens', 'edit')   
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        if self.exists():
            object = self.image
            width, height = object.width, object.height
            size = self.getFileSize()
            if not size:
                self.setFileSize()
                size = self.getFileSize()
            imageType = self.image.content_type
            format = '<p>Preview: %s  (%s px/%s px) %s %s </p>'
            temp.append(format % (self.small(), width, height, size, imageType))
        temp.append('<p>These heights and widths will be used as closely as possible and keep aspect ratio.</p>')
        width = self.editSingleConfig('width', format='%(form)s')
        height = self.editSingleConfig('height', format='%(form)s')
        temp.append('<p class="imageSize">Suggested Width:%s px  Height:%s px</p>' % (width, height))
        return ''.join(temp)

    security.declarePrivate('setFileSize')
    def setFileSize(self):
        "Store the file size of this object"
        try:
            fileSize = utility.fileSizeString(self.image.size)
            self.setObject('fileSize', fileSize)
        except AttributeError:
            pass

    security.declarePrivate('post_process_location')    
    def post_process_location(self, before, after):
        "if the location is changed we need to ensure we unhook from the old picture"
        #detach old picture
        picture = self.getRemoteImage(before)
        if picture is not None:
            picture.observerDetached(self)
        
        #attach new picture
        picture = self.getRemoteImage(after)
        if picture is not None:
            picture.observerAttached(self)
            self.observerUpdate(picture)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "cache some information after this object has been modified"
        if self.hasBeenModified() and not self.getConfig('scriptChangePath'):
            self.regenImages()

    security.declarePrivate('getRemoteImage')
    def getRemoteImage(self, location=None):
        "Get the remote image"
        location = location if location is not None else self.getConfig('location')
        return self.getRemoteObject(location, 'Picture')

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

    security.declarePrivate('observerUpdate')
    def observerUpdate(self, pic):
        "Process what you were observing"
        self.regenImages(pic)

    security.declareProtected('Change CompoundDoc', 'regenImages')
    def regenImages(self, pic=None):
        "regenerate the image and thumbnail"
        #this handles the case where we can't find the remote object we should be attached to
        remote = self.getRemoteImage()
        if remote is None and self.getConfig('location'):
            self.delObjects(['image', 'thumbnail', 'fileSize'])
                
        #this is the normal case
        pic = pic if pic is not None else self.getRemoteImage()
        if pic is not None and pic.exists():
            self.generateImage(pic)
        else:
            self.delObjects(['image', 'thumbnail', 'fileSize'])

    security.declareProtected('Change CompoundDoc', 'resaveExistingImage')
    def resaveExistingImage(self):
        "reisze existing images"
        if self.exists():
            filename, remove_after = utility.createTempFile(self.image.data)
            content_type = magicfile.magic(filename)
            if content_type.startswith('image'):
                temp = utility.resaveExistingImage(filename, 'image')
                beforeSize = utility.fileSizeToInt(self.getFileSize())
                if temp is not None:
                    afterSize = utility.fileSizeToInt(utility.fileSizeString(temp.data))
                else:
                    afterSize = beforeSize
                if temp is not None and afterSize < beforeSize:
                    self.setObject('image', temp)
                    #have to redo the content_type after we modify the image in case it has changed
                    content_type = magicfile.magic(filename)
                    self.setFileSize()
                    self.image.content_type = content_type
            utility.removeTempFile(filename, remove_after)

    security.declarePrivate('generateImage')
    def generateImage(self, pic):
        "generate an image and thumbnail based on this data"
        filename, remove_after = utility.createTempFile(pic.data.data)
        content_type = magicfile.magic(filename)
        if content_type.startswith('image'):
            self.genImage(filename)
            self.updateImageSrcCache()
        utility.removeTempFile(filename, remove_after)
        self.makeThumbnail()

    security.declarePrivate('updateImageSrcCache')
    def updateImageSrcCache(self,  remote=None):
        "update the imagesrc cache string"
        if self.exists():
            decode = {}
            decode['height'] = self.image.height
            decode['width'] = self.image.width
            
            remote = remote or self.getRemoteImage()
            if remote is None:
                alt = ''
                tags = ''
                url = ''
            else:
                alt = remote.alt
                tags = remote.tags
                url = remote.url
            
            
            if com.detection.no_dtml(alt):
                decode['alt'] = self.convert(alt)
            else:
                decode['alt'] = alt

            decode['tags'] = tags

            self.setObject('imagesrc_template', image_template.safe_substitute(decode))

    security.declarePrivate('genImage')
    def genImage(self, filename):
        "generate this image"
        image=PIL.Image.open(filename)
        if image.mode != self.getConfig('color'):
            image=image.convert(self.getConfig('color'))
        crop_left = self.getConfig('crop_left')
        crop_upper =  self.getConfig('crop_upper')
        crop_right =  self.getConfig('crop_right')
        crop_lower = self.getConfig('crop_lower')
        if crop_right and crop_lower:
            image = image.crop((crop_left, crop_upper, crop_right, crop_lower))
        (x, y) = image.size
        if x> self.width:
            y = y * self.width / x
            x = self.width
        if y> self.height:
            x = x * self.height / y
            y = self.height
        if x == 0:
            x = 1
        if y == 0:
            y = 1
        image = image.resize((x, y))
        tempFile = utility.saveImage(image, self.getConfig('format'))
        newimage = OFS.Image.Image('image', 'image', tempFile)
        self.setObject('image', newimage)
        self.image.width = int(x)
        self.image.height = int(y)
        self.setFileSize()

    security.declareProtected('View', 'view')
    def view(self, urlCallable=None, parent=None, additionalAttributes='', drawHref=1):
        "Render page"
        remote = self.getRemoteImage()
        parent = parent if parent is not None else remote
        if remote is None:
            url = ''
        else:
            url = remote.url
        if self.exists():
            decode = {}
            decode['url'] = self.absolute_url_path_extension()
            decode['additionalAttributes'] = additionalAttributes
            if not self.imagesrc_template:
                self.REQUEST.other['okayToRunNotification'] = 0
                self.updateImageSrcCache()
                self.delObjects(['imagesrc'])
            image = Template(self.imagesrc_template).safe_substitute(decode)

            if drawHref and url:
                href = com.html.generate_url(url, parent, self.REQUEST, url_callable=urlCallable)
                if href is not None:
                    image = '<a href="%s">%s</a>' % (href,image)
            return image
        return ''

    security.declareProtected("Access contents information", 'exists')
    def exists(self):
        "Check if object has data in it"
        try:
            #just seeing if that image exists
            self.image.image
            return True
        except AttributeError:
            return False

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.percentEscape()
        self.addAdditionalVarsSupport()

    security.declarePrivate('percentEscape')
    def percentEscape(self):
        "escape any % that might be in the url so that subs work right"
        self.updateImageSrcCache()
    percentEscape = utility.upgradeLimit(percentEscape, 159)

    security.declarePrivate('convert_to_template')
    def convert_to_template(self):
        "escape any % that might be in the url so that subs work right"
        self.updateImageSrcCache()
    convert_to_template = utility.upgradeLimit(convert_to_template, 174) 

Globals.InitializeClass(ImageFilter)
import register
register.registerClass(ImageFilter)
