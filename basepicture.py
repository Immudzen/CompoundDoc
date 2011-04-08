# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import OFS.Image
from file import File

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import magicfile

import utility

class BasePicture(File):
    "Image class"

    meta_type = "BasePicture"
    security = ClassSecurityInfo()
    
    format = 'JPEG'
    color = 'RGB'
    width = 0
    height = 0
    scriptChangePath = ''
    
    imageFormat = {'BMP' : 'Bitmap', 'PNG' : "PNG", "GIF" : "GIF", "JPEG" : "JPEG", "TIFF" : "TIFF"}
    formats = sorted(imageFormat.iteritems())
    
    colorFormat = {'L' : 'Black and White', 'RGB' : 'Color', 'RGBA' : 'Color + Transparency'}
    colors = sorted(colorFormat.iteritems())
    
    classConfig = {}
    classConfig['width'] = {'name':'Suggested Width of Image:', 'type': 'int'}
    classConfig['height'] = {'name':'Suggested Height of Image:', 'type': 'int'}
    classConfig['format'] = {'name':'', 'type':'list', 'values': formats}
    classConfig['color'] = {'name':'', 'type':'list', 'values': colors}
    classConfig['scriptChangePath'] = {'name':'Path to change notification script', 'type': 'path'}
    
    configurable = ('format', 'color',)

    security.declarePrivate('makeThumbnail')
    def makeThumbnail(self):
        """
        Makes a thumbnail image given an image Id when called on a Zope
        folder.

        The thumbnail is a Zope image object that is a small JPG
        representation of the original image. The thumbnail has a
        'original_id' property set to the id of the full size image
        object.
        """
        size=30
        data = self.data or self.image
        filename, remove_after = utility.createTempFile(data.data)
        content_type = magicfile.magic(filename)
        if content_type.startswith('image'):
            try:
                from PIL import Image
                            
                image=Image.open(filename)
                image=image.convert('RGB')
                (x,y) = image.size
                if x > size: x = size
                if y > size: y = size
                image = image.resize((x,y))
                thumbnail_file = utility.saveImage(image, 'JPEG')
                thumbnail_id = "thumbnail"
                self.setObject(thumbnail_id, OFS.Image.Image(thumbnail_id, thumbnail_id, thumbnail_file))
            except (IOError, ImportError):
                pass
        utility.removeTempFile(filename, remove_after) 

    extensionLookup = {}
    extensionLookup['image/jpeg'] = 'jpg'
    extensionLookup['image/jpeg; charset=binary'] = 'jpg'
    extensionLookup['image/png'] = 'png'
    extensionLookup['image/png; charset=binary'] = 'png'
    extensionLookup['image/gif'] = 'gif'
    extensionLookup['image/gif; charset=binary'] = 'gif'
    
    security.declarePublic("__bobo_traverse__")
    def __bobo_traverse__(self, REQUEST, name):
        "__bobo_traverse__"
        if name.startswith('ver_'):
            name = self.REQUEST.TraversalRequestNameStack.pop()
            self.REQUEST.RESPONSE.setHeader('Cache-Control', 'max-age=315360000')
            self.REQUEST.RESPONSE.setHeader('Expires', 'Thu, 01 Dec 2030 12:00:0')
        obj = getattr(self, name, None)
        if obj is not None:
            return obj
        elif name == self.getImageNameExtension():
            data = self.data or self.image
            return data.index_html

    security.declareProtected('View', 'index_html')
    def index_html(self):
        "the base view of this object"
        if self.exists():
            data = self.data or self.image
            return data.index_html(self.REQUEST, self.REQUEST.RESPONSE)
        return ''

    security.declareProtected('View', 'getImageNameExtension')
    def getImageNameExtension(self):
        "return the name of this image plus extension"
        name = 'data'
        if self.exists():
            data = self.data or self.image
            extension = self.extensionLookup.get(data.content_type, '')
            name = name + '.' + extension
        return name
        
    security.declareProtected('View', 'absolute_url_path_extension')
    def absolute_url_path_extension(self):
        "return the url to this image plus the filename and extension"
        data = self.data or self.image
        return self.absolute_url_path() + '/ver_%s/' % int(data.bobobase_modification_time().timeTime()) + self.getImageNameExtension()

    security.declareProtected('View', 'absolute_url_path_extension_thumbnail')
    def absolute_url_path_extension_thumbnail(self):
        "return the url to this image plus the filename and extension"
        data = self.thumbnail
        return self.absolute_url_path() + '/ver_%s/thumbnail' % int(data.bobobase_modification_time().timeTime())

    security.declareProtected('View', 'absolute_url_extension')
    def absolute_url_extension(self):
        "return the url to this image plus the filename and extension"
        data = self.data or self.image
        return self.absolute_url() + '/ver_%s/' % int(data.bobobase_modification_time().timeTime()) + self.getImageNameExtension()

    security.declarePrivate('small')
    def small(self):
        "Draw a small version of the object"
        if self.exists() and self.thumbnail is None:            
            self.makeThumbnail()

        if self.exists() and self.hasObject('thumbnail'):
            decode = {'url': self.absolute_url_path_extension_thumbnail(),
              'fullUrl':self.absolute_url_path_extension(),
              'height':self.thumbnail.height ,
              'width':self.thumbnail.width ,
              'alt': "",
              'name': "thumbnail"}
            return '<a href="%(fullUrl)s" rel="lightbox"><img src="%(url)s" width="%(width)s" height="%(height)s" alt="%(alt)s"></a>' % decode
        return ""

    security.declarePrivate('addAdditionalVarsSupport')
    def addAdditionalVarsSupport(self):
        "escape any % that might be in the url so that subs work right"
        self.updateImageSrcCache()
    addAdditionalVarsSupport = utility.upgradeLimit(addAdditionalVarsSupport, 168)

Globals.InitializeClass(BasePicture)
import register
register.registerClass(BasePicture)
