# -*- coding: utf-8 -*-
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from Acquisition import aq_base

import types
import utility

class GetSet:
    security = ClassSecurityInfo()

    security.declarePrivate('parentPaths')
    def updateParentPaths(self,  names):
        "return a list of the db paths of this objects parents up to the containing cdoc"
        if not hasattr(self, 'aq_chain') or not hasattr(self, 'REQUEST'):
            return None

        if not 'modifiedPaths' in self.REQUEST.other:
            self.REQUEST.other['modifiedPaths'] = set()
        modifiedPaths = self.REQUEST.other['modifiedPaths']
        
        if not 'modifiedDocs' in self.REQUEST.other:
            self.REQUEST.other['modifiedDocs'] = set()
        modifiedDocs = self.REQUEST.other['modifiedDocs']
        
        attr_notified = self.attr_notified
        if attr_notified is None or (attr_notified is not None and names.intersection(attr_notified)):
            modifiedPaths.add(aq_base(self))
        
        modifiedDocs.add(self.getCompoundDoc())
        
    security.declareProtected('Change CompoundDoc', 'setObject')
    def setObject(self, name, content,  runValidation=1):
        "Set the property of an object"
        event = getattr(self, "event_%s" % name, None)
        if event is not None:
            event(content)
            
        validate = getattr(self, "validate_%s" % name, None)
        if validate is not None and runValidation:
            content = validate(content)
        
        if hasattr(self.__class__, name) and getattr(self.__class__, name) == content:
            if name in self.__dict__:
                delattr(self, name)
                self.updateParentPaths(set([name]))
            return
        currentValue = getattr(aq_base(self), name, None)
        if name not in self.__dict__ or content != currentValue:
            setattr(self, name, content)
            self.updateParentPaths(set([name]))
            aq_base(self)._updateMetaMapping(name, aq_base(content))
            
            try:
                func = getattr(self, name).performUpdate
            except AttributeError:
                func = utility.dummy
            func()
            
            post_process = getattr(self, "post_process_%s" % name, None)
            if post_process is not None:
                post_process(before=currentValue, after=content)

    security.declarePrivate('_updateMetaMapping')
    def _updateMetaMapping(self, name, content):
        "Update the meta mapping to include this object"
        meta_type = getattr(content, 'meta_type', None)
        if meta_type is not None:
            if name not in self.objectIds():
                self.setObject('_objects', self._objects + ({'id':name, 'meta_type':content.meta_type}, ))

    security.declareProtected('CompoundDoc: Delete Attributes', 'delObjects')
    def delObjects(self, names):
        "Del object and ref"
        modified = 0
        for name in names:
            try:
                delattr(self, name)
                modified = 1
            except AttributeError:
                pass
            
            try:
                self.setObject('_objects', tuple(filter(lambda i, n=name: i['id']!=n, self._objects)))
            except AttributeError:
                pass
            
        if modified:
            self.updateParentPaths(set(names))

    security.declarePrivate('updateObject')
    def updateObject(self, name, content):
        "Update an object to a new version or add it if it does not exist this will not change content"
        if not name in self.__dict__:
            if isinstance(content, types.TupleType):
                if len(content) and content[0] == 'call':
                    method = content[1]
                    if not callable(method):
                        method = getattr(self, method)
                    if callable(method):
                        self.setObject(name, method())
                elif len(content) and content[0] == 'create':
                    self.updateRegisteredObject(name, content[1])
                else:
                    self.setObject(name, content)
            else:
                self.setObject(name, content)

Globals.InitializeClass(GetSet)
