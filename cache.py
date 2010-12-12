###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#base object that this inherits from
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from BTrees.OOBTree import OOBTree
from zodblist import ZODBList
from zodbstring import ZODBString

class Cache(base.Base):
    "Cache class used to caching edit, config and view screens and getting that data back out"

    meta_type = "Cache"
    security = ClassSecurityInfo()

    security.declarePrivate('__init__')
    def __init__(self, id):
        "create the initial items for this object mainly the OOBTree"
        self.cache = OOBTree()
        base.Base.__init__(self, id)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        format = "<p>Currently there are %s records</p>"
        if not hasattr(self, 'cache'):
            self.cache = OOBTree()
        return format % len(self.cache)

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return ''

    security.declarePrivate('cacheString')
    def cacheString(self, object, mode, string):
        "find the path that we want to use an add it to the OOBtree encoded in a useful way to get the data back out"
        if not hasattr(self, 'cache'):
            self.cache = OOBTree()
        name = '%s:%s' % (self.getRelativePath(object), mode)
        try:
            self.cache[name].set(string)
        except KeyError:
            self.cache[name] = ZODBString(string)
        return name

    security.declarePrivate('cacheList')
    def cacheList(self, object, mode, list):
        "find the path that we want to use an add it to the OOBtree encoded in a useful way to get the data back out"
        if not hasattr(self, 'cache'):
            self.cache = OOBTree()
        name = '%s:%s' % (self.getRelativePath(object), mode)
        try:
            self.cache[name].set(list)
        except KeyError:
            self.cache[name] = ZODBList(list)
        return name

    security.declarePrivate('getCacheObject')
    def getCacheObject(self, object, mode):
        "find the correct object and mode and return it"
        name =  '%s:%s' % (self.getRelativePath(object), mode)
        return self.cache[name]

    security.declarePrivate('getRelativePath')
    def getRelativePath(self, object):
        "return the relative path of this object to the nearest compounddoc"
        return object.getPath().replace(self.getCompoundDoc().getPath()+'/', '')

    security.declarePrivate('getCacheName')
    def getCacheName(self, name):
        "fine the object with this name and return it"
        return self.cache[name]

    def deleteCacheName(self, name):
        "delete an object from the cache"
        del self.cache[name]

Globals.InitializeClass(Cache)
import register
register.registerClass(Cache)