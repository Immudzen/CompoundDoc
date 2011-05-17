# -*- coding: utf-8 -*-
import types
import __builtin__
from zLOG.EventLogger import log_write
import zLOG
import os
import pickle
import string
from Acquisition import aq_base
import cgi
import urllib
import sys
import time
import tempfile
from BTrees.OOBTree import OOBTree
import transaction
import chardet

import itertools
from PIL import ImageFile
import PIL
ImageFile.MAXBLOCK = 5*1024*1024 #5 megs

import ZODB.blob

def isStringLike(data):
    "check if this item is string like go this from the python cookbook reformatted it and also made it just catch known errors"
    return __builtin__.isinstance(data, basestring)

#isinstance and issubclass stuff got it from  http://www.amk.ca/zodb/guide/node18.html

# The built-in 'isinstance()' and 'issubclass()' won't work on
# ExtensionClasses, so you have to use the versions supplied here.
# (But those versions work fine on regular instances and classes too,
# so you should *always* use them.)
#
# Supposedly, these two can go away when Python 2.1 comes out (and we
# switch to it), since its 'issubclass()' and 'isinstance()' will
# finally be able to deal with extension classes completely in 2.1.
# (It's close in 1.6 and 2.0, but not quite there yet.)

def issubclass(class1, class2):
    """A version of 'issubclass' that works with extension classes
    as well as regular Python classes.
    """

    # Both class objects are regular Python classes, so use the
    # built-in 'issubclass()'.
    if type(class1) is types.ClassType and type(class2) is types.ClassType:
        return __builtin__.issubclass(class1, class2)

    # Both so-called class objects have a '__bases__' attribute: ie.,
    # they aren't regular Python classes, but they sure look like them.
    # Assume they are extension classes and reimplement what the builtin
    # 'issubclass()' does behind the scenes.
    elif hasattr(class1, '__bases__') and hasattr(class2, '__bases__'):
        # XXX it appears that "ec.__class__ is type(ec)" for an
        # extension class 'ec': could we/should we use this as an
        # additional check for extension classes?

        # Breadth-first traversal of class1's superclass tree.  Order
        # doesn't matter because we're just looking for a "yes/no"
        # answer from the tree; if we were trying to resolve a name,
        # order would be important!
        stack = [class1]
        while stack:
            if stack[0] is class2:
                return 1
            stack.extend(list(stack[0].__bases__))
            del stack[0]
        else:
            return 0

    # Not a regular class, not an extension class: blow up for consistency
    # with builtin 'issubclass()"
    else:
        raise TypeError, "arguments must be class or ExtensionClass objects"

# issubclass ()

def cleanEncodingSeq(seq):
    "if this is a string like object rencode it otherwise leave it alone"
    seq = list(seq)
    detect = []
    output = []
    
    for item in seq:
        if __builtin__.isinstance(item, basestring):
            detect.append(item)
    
    encoding = chardet.detect(' '.join(detect))['encoding']
    
    for item in seq:
        if not item:
            output.append(item)
        else:
            try:
                output.append(item.decode(encoding,'replace'))
            except (AttributeError, TypeError):
                output.append(unicode(item))
    return output

def escape_html_seq(seq):
    "escape all the strings in this sequence so they are html safe"
    for i in seq:
        yield cgi.escape(i, 1)


def isinstance(object, klass):
    """A version of 'isinstance' that works with extension classes
    as well as regular Python classes."""

    if type(klass) is types.TypeType:
        return __builtin__.isinstance(object, klass)
    elif hasattr(object, '__class__'):
        return issubclass(object.__class__, klass)
    else:
        return 0

def subTrans(seq,  count):
    "do a subtransaction for every count"
    for idx,  item in enumerate(seq):
        if idx % count == 0:
            transaction.savepoint(optimistic=True)
        yield item
        
def subTransDeactivate(seq, count, cacheGC=None):
    "do a subtransaction for every count and also deactivate all objects"
    cacheGC = cacheGC if cacheGC is not None else lambda :None
    for idx,  item in enumerate(seq):
        if idx % count == 0:
            cacheGC()
            transaction.savepoint(optimistic=True)
        yield item
        item._p_deactivate()

def subTransDeactivateKeyValue(seq, count, cacheGC=None):
    "do a subtransaction for every count and also deactivate all objects"
    cacheGC = cacheGC if cacheGC is not None else lambda :None
    for idx,  item in enumerate(seq):
        if idx % count == 0:
            cacheGC()
            transaction.savepoint(optimistic=True)
        yield item
        item[1]._p_deactivate()

def log(name, short="", longMessage="", error_level=zLOG.INFO, reraise=0):
    "Log an error to a file"
    log_write(name, error_level, str(short), str(longMessage), None)

def allowed_profile(profile):
    path = os.path.join(os.path.dirname(__file__), 'Profiles', profile)
    if os.path.exists(path) and os.path.isfile(path):
        return 1
    else:
        return 0

def isCleanFileName(filename):
    "return true if the filename is clean to use"
    ok = set(string.digits + string.letters)
    for i in filename:
        if i not in ok:
            return 0
    else:
        return 1
    
def objectStoreFile(data, filename):
    "save this document to a file called filename as a pickle just letters and numbers permitted"
    if isCleanFileName(filename):
        checkProfilesDir()
        path = os.path.join(os.path.dirname(__file__), 'Profiles', filename)
        f = open(path, 'w')
        p = pickle.Pickler(f)
        p.dump(data)
        f.close()

def objectLoadFile(filename):
    "load the pickle of this filename and return the dict to be dispatched just letters and numbers permitted"
    if isCleanFileName(filename):
        checkProfilesDir()
        if allowed_profile(filename):
            path = os.path.join(os.path.dirname(__file__), 'Profiles', filename)
            f = open(path, 'r')
            p = pickle.Unpickler(f)
            data = p.load()
            f.close()
            return data    
    
def upgradeLimit(f, version):
    def wrap(self, *args, **kw ):
        if self.objectVersion < version:
            return f(self, *args, **kw)
    return wrap
    
def createTempFile(data):
    "create a temp file with this data and return the filename"
    if __builtin__.isinstance(data, ZODB.blob.Blob):
        filename = data.open('r').name
        remove_after = 0
        return filename, remove_after
    handle, filename = tempfile.mkstemp()
    temp_file = open(filename, 'wb')
    try:
        temp_file.write(data.read())
    except AttributeError:
        temp_file.write(str(data))
    temp_file.close()
    remove_after = 1
    return filename, remove_after
    
def removeTempFile(filename, remove_after):
    "remove this temp file"
    if remove_after:
        os.remove(filename)
    
def saveImage(pilImage, format):
    "saves the image via the filesystem since StringIO causes errors sometimes"
    temp = tempfile.TemporaryFile()
    try:
        pilImage.save(temp, format, optimize=1)
    except IOError:
        pilImage.save(temp, format)
    temp.seek(0)
    return temp
    
def resaveExistingImage(filename):
    "generate this image"
    image=PIL.Image.open(filename)
    if image.format in ('JPEG', 'PNG'):
        (x, y) = image.size
        temp_file = saveImage(image, image.format)
        return temp_file, x, y
    return None, None, None

def removeRecordFromCatalog(catalog, record):
    "remove this record from the catalog"
    catalog.uncatalog_object(record.getPath())

def addDocToCatalog(catalog, doc):
    "add this object to the catalog"
    mode = doc.getDrawMode()
    doc.setDrawMode('view')
    catalog.catalog_object(doc)
    doc.setDrawMode(mode)


def checkProfilesDir():
    "Check if the profiles dir exists else add it if something else is called Profiles but is not a dir rename it"
    path = os.path.join(os.path.dirname(__file__), 'Profiles')
    if os.path.exists(path):
        if os.path.isdir(path):
            pass #Do nothing everything is okay
        else:
            #Very bad we have a Profiles that is not a dir
            path2 = path = os.path.join(os.path.dirname(__file__), 'Profiles%s' % time.time())
            os.rename(path, path2)
            os.mkdir(path)
    else:
        os.mkdir(path)

def getStoredProfileNames():
    "Return a list of the names of all profiles we have"
    checkProfilesDir()
    path = os.path.join(os.path.dirname(__file__), 'Profiles')
    temp = set(os.listdir(path))
    if 'None' not in temp:
        temp.add('None')
    return sorted(temp)

allowable = set(string.letters + '_' + string.digits)
numMapping={'1':'one', '2':'two', '3':'three', '4':'four',
        '5':'five', '6':'six', '7':'seven', '8':'eight', '9':'nine', '0':'zero'}

def cleanRegisteredId(name):
    "Clean the registered id"
    if not len(name):
        return None
    ok = [i for i in name if i in allowable]
    if ok[0] in numMapping:
        ok[0] = numMapping[ok[0]]
    return ''.join(ok)
    
def drawFolderPath(path, container, folderType='Folder'):
    "create the folder structure from this container or the container of the cdoc if left none"
    temp = []

    if path[0] == '':
        folder = container.getPhysicalRoot()
        del path[0]
        temp.append('')
    else:
        folder = container
    for name in path:
        name = cleanRegisteredId(name)
        temp.append(name)
        if not hasattr(aq_base(folder), name):
            if folderType == 'Folder':
                folder.manage_addProduct['OFSP'].manage_addFolder(name)
            elif folderType  == 'BTree':
                folder.manage_addProduct['BTreeFolder2'].manage_addBTreeFolder(name)
        folder = getattr(folder, name)
    return temp
            
def updateQueryString(queryString, updates):
    "create a new query string that has certain values replaced"
    query = dict(cgi.parse_qsl(queryString))
    query.update(updates)
    return urllib.urlencode(query)         
            
def getQueryDict(queryString):
    "get the query dictionary from this queryString"
    return dict(cgi.parse_qsl(queryString))           
            
def dictInQuery(queryDict, query):
    "see if queryDict is in query"
    for key,value in queryDict.iteritems():
        if key in query and query[key] == value:
            pass
        else:
            return False
    return True
            
def fileSizeString(size):
    "return a string that has the file size"
    unit = "B"
    MB = 1048576.0
    KB = 1024.0

    if size > MB:
        unit = "MB"
        size = size/MB
    if size > KB:
        unit = "KB"
        size = size/KB
    return "%.1f %s" % (size, unit)
    
def fileSizeToInt(fileString):
    "turns a filesize into an int in bytes"
    lookup = {'B':1, 'KB':1024.0, 'MB':1048576.0}
    size, unit = fileString.split()
    return float(size) * lookup[unit]
    
def callOptional(obj, arg1, arg2):
    "try to call with both args and if that fails call with only one arg"
    try:
        return obj(arg1, arg2)
    except TypeError:
        return obj(arg1)
    
    
def you_rang():
    try:
        raise RuntimeError
    except RuntimeError:
        exc, val, tb = sys.exc_info()
        frame = tb.tb_frame.f_back
        del exc, val, tb
    try:
        n = 1
        currentFrame = frame.f_back
        while n:
            try:
                print n, currentFrame.f_code.co_name, currentFrame.f_code.co_filename
                n += 1
                currentFrame = currentFrame.f_back
            except AttributeError:
                break
        print '\n\n\n'
    except AttributeError:  # called from the top
        pass
        
def mergeSequenceTree(sequence):
    "Merge this sequence into a tree and make it into a dict"
    temp = {}
    if __builtin__.isinstance(sequence, types.TupleType) or __builtin__.isinstance(sequence, types.ListType):
        for i in sequence:
            locator = temp
            for j in i:
                if not j in locator:
                    locator[j] = {}
                locator = locator[j]
        return temp
                
def renderNoneAsString(item, string=''):
    "if the item is None then return the string we have here otherwise return the item"
    if item is None:
        return string
    return item

def hasLocalEdit(dict):
    "return true if we have any local items to edit"
    for path in dict:
        if not path.startswith('/'):
            return True
        
def addRender(cdoc, name, header, body, footer):
    "add a render object"
    if name is not None and body:
        if cdoc.displayMap is None:
            cdoc.setObject('displayMap',OOBTree())
        cdoc.displayMap[name] = (header, body, footer)

def setDefaultEdit(cdoc, display):
    "set the default rendering object"
    setDefault(cdoc, display, 'edit')

def setDefaultView(cdoc, display):
    "set the default rendering object"
    setDefault(cdoc, display, 'view')

def setDefault(cdoc, display, mode):
    "set the default rendering object for this mode"
    if cdoc.displayMap.has_key(display):
        if cdoc.defaultDisplay is None:
            cdoc.setObject('defaultDisplay',OOBTree())
        cdoc.defaultDisplay[mode] = display
        
def dtmlToScript(data):
    "put this dtml into a python script so that it can render there"
    return '''from Products.PythonScripts.standard import DTML
myString = """%s"""

return DTML(myString)(context, context.REQUEST, context.REQUEST.RESPONSE)''' % data


def dummy(*args, **kw):
    """do nothing just a dummy function to make it easier to deal 
    with attribute errors on functions not being found but not hiding attribute errors 
    inside the function"""
    return None
