# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import os.path

class BaseControlManager(ControlBase):
    "Input text class"

    meta_type = "BaseControlManager"
    security = ClassSecurityInfo()
    control_title = ''
    drawMode = ''
    skipIds = ('ControlPanel',)
    startLoc = ''
    cssClass = ''
    drawBlankPath = 1

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        if len(self.REQUEST.other['TraversalRequestNameStack']):
            return self
        else:
            return self.index_html

    security.declarePrivate('getFixedUpPath')
    def getFixedUpPath(self):
        "return the fixed up path so we can use it for traversal"
        url = self.REQUEST.URLPATH0.split('/')
        cpath = self.absolute_url_path().split('/')
        path = url[len(cpath):]
        if path[0] == 'index_html':
            path.pop()
        return path

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        """This draws the inline forms for the objects present."""
        origin = self.getOrigin()
        path = self.getFixedUpPath()
        if path or (not path and self.drawBlankPath) and origin is not None:
            object = origin.unrestrictedTraverse(path, None)
        else:
            object = None
        if object is not None:
            temp = '<div class="%(cssClass)s"><p>%(submit)s</p>%(draw)s</div>'
            lookup = {'submit':self.submitChanges(),
              'draw':object.draw(self.drawMode), 'cssClass':self.cssClass}
            return temp % lookup
        return ""

    security.declarePrivate('isOkay')
    def isOkay(self, name, object):
        "determine if this object with this name is okay to have in the menu"
        notMenuNames = self.skipIds
        return name not in notMenuNames and object.hasObject('draw')

    security.declarePrivate('traverseContainer')
    def traverseContainer(self, container=None, path=None, url=None, queryDict=None):
        "used for the dynamic menu system"
        queryDict = queryDict or {}
        if path is None:
            path = self.getFixedUpPath()
            path.reverse()
        try:
            selected = path.pop()
        except IndexError:
            selected = None
        if url is None:
            url = self.absolute_url_path()
            
        if container is None:
            container = self.getOrigin()    
        temp = []
        if container is not None:
            containers = container.objectItems()
            containers = sorted((name, object) for name, object in containers if self.isOkay(name, object))
    
            for name, object in containers:
                if name == selected:
                    temp.append((os.path.join(url, name), name, 1, '', queryDict, ''))
                    temp.append(self.traverseContainer(object, path, url=os.path.join(url, selected), queryDict=queryDict))
                else:
                    temp.append((os.path.join(url, name), name, 0, '', queryDict, ''))
        return temp

    security.declarePrivate('getOrigin')
    def getOrigin(self):
        "get the origin document"
        if self.startLoc:
            return getattr(self.getCompoundDoc(), self.startLoc)
        else:
            return self.getCompoundDoc()
    
Globals.InitializeClass(BaseControlManager)
