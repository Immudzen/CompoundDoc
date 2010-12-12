#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from mixaddregistered import MixAddRegistered
from simpleembed import SimpleEmbed
from Acquisition import aq_base
import utility

class MultiSimpleEmbed(SimpleEmbed, MixAddRegistered):
    "uses a container to give access to a view of many compounddocs using simpleembed"

    meta_type = "MultiSimpleEmbed"
    security = ClassSecurityInfo()

    editDisplayName = ''
    viewDisplayName = ''

    security.declarePrivate('instance')
    instance = (('CreationAssistant',('create', 'CreationAssistant')),)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''    
    
    classConfig = {}
    classConfig['editDisplayName'] = {'name':'Display for editing:', 'type':'string'}
    classConfig['viewDisplayName'] = {'name':'Display for viewing:', 'type':'string'}
    classConfig['path'] = {'name':'Path:', 'type':'string'}   
    
    security.declarePrivate('observerUpdate')
    def observerUpdate(self, object=None):
        "Process what you were observing"
        object = self.getCompoundDoc().restrictedTraverse(self.path,None)

        useObjects = object.getUseObjects()

        simplemethodobjects = self.objectValues('SimpleEmbed')
        if object:
            if useObjects is not None:
                for i in useObjects:
                    path = i.getPath()
                    if not hasattr(aq_base(self), path):
                        embed = SimpleEmbed(path)
                        embed.path = path
                        self.setObject(path, embed)
        else:
            self.delObjects(self.objectIds('SimpleEmbed'))
            return None

        useObjects = object.getUseObjects()

        if useObjects is not None:
            paths = [i.getPath() for i in useObjects]
            for embed in simplemethodobjects:
                if embed.embedded() is not None:
                    path = embed.getId()
                    if path not in paths:
                        self.delObjects([path])
                else:
                    self.delObjects([embed.getId()])

    def after_manage_edit(self, dict):
        "Process edits."
        try:
            object = self.getCompoundDoc().restrictedTraverse(self.path)
        except KeyError:
            object = None
        if object is not None:
            object.observerAttached(self)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        self.setDrawMode('edit')
        format = '<p>ID:%s</p> %s'
        return ''.join([format % (id, object.edit()) for id,object in self.objectItems('SimpleEmbed')])

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        object = self.getCompoundDoc().restrictedTraverse(self.path,None)
        if object is not None and object.limitOkay():
            return ''.join([object.view() for object in self.objectValues('SimpleEmbed')])
        return ''

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeOldAttributes()
        self.fixupObservation()

    security.declarePrivate('removeOldAttributes')
    def removeOldAttributes(self):
        "remove attributes that are no longer needed"
        self.delObjects(['editDTML', 'viewDTML', 'CreationAssistantString'])
    removeOldAttributes = utility.upgradeLimit(removeOldAttributes, 141)
    
    security.declarePrivate('fixupObservation')
    def fixupObservation(self):
        "fix the observation stuff"
        try:
            object = self.getCompoundDoc().restrictedTraverse(self.path)
        except KeyError:
            object = None
        if object is not None:
            object.observerAttached(self)
            if object.inuse == []:
                self.delObjects(self.objectIds('SimpleEmbed'))        
    fixupObservation = utility.upgradeLimit(fixupObservation, 141)
                                
Globals.InitializeClass(MultiSimpleEmbed)
import register
register.registerClass(MultiSimpleEmbed)