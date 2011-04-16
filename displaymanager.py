import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class DisplayManager(base.Base):
    "DisplayManager manages all displays"

    meta_type = "DisplayManager"
    security = ClassSecurityInfo()
    overwrite=1

    data = ''
    defaultEdit = ''
    defaultView = ''
    get_default = {'edit':'defaultEdit', 'view':'defaultView'}
    usageMapping = None

    security.declarePrivate('render')
    def render(self, purpose, display=None):
        "Please render an item with this purpose"
        get_default = self.get_default

        try:
            return getattr(self, display).view()
        except (AttributeError,TypeError):
            pass

        try:
            return getattr(self, getattr(self, get_default[purpose])).view()
        except (AttributeError,KeyError):
            pass

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = [self.addDeleteObjectsEdit()]
        editDisplays = self.displayUsage('edit')
        if editDisplays:
            temp.append('<p>Default Display for editing: %s</p>' % self.option_select(editDisplays, 'defaultEdit',
              [self.defaultEdit]))
        viewDisplays = self.displayUsage('view')
        if viewDisplays:
            temp.append('<p>Default Display for viewing: %s</p>' % self.option_select(viewDisplays, 'defaultView',
              [self.defaultView]))
        return ''.join(temp)

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        return ['Display']

    security.declarePrivate('displayUsage')
    def displayUsage(self, usage):
        "Return all objects that match this usage"
        if self.usageMapping is None:
            return []
        return self.usageMapping.get(usage,[])

    security.declarePrivate('performUpdate')
    def performUpdate(self):
        "Update object to newest version"
        if not self.checkShared():
            super(DisplayManager, self).performUpdate()

    security.declarePrivate('performUpgrade')
    def performUpgrade(self):
        "perform the upgrade on this object and its children"
        if not self.checkShared():
            super(DisplayManager, self).performUpgrade()

    security.declarePrivate('beforeProfileLoad')
    def beforeProfileLoad(self):
        "run this action before loading the object with profile information"
        self.delObjects(self.objectIds('Display'))
        self.performUpdate()

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeBadEditName()
        self.fixupCurrentEdit()
        for i in self.objectValues('Display'):
            i.performUpgrade()
        self.fixupDefaultEdit()
        self.fixupDefaultView()
        self.addUsageMapping()
        self.fixedDefaultDisplay()
        
    security.declarePrivate('fixupDefaultEdit')
    def fixupDefaultEdit(self):
        "fix the defaultEdit attribute"
        if self.defaultEdit == '':
            temp = self.displayUsage('edit')
            if len(temp):
                self.setObject('defaultEdit',temp[0])
    fixupDefaultEdit = utility.upgradeLimit(fixupDefaultEdit, 141)
    
    security.declarePrivate('fixupDefaultView')            
    def fixupDefaultView(self):
        "fixup the defaultView attribute"
        if self.defaultView == '':
            temp = self.displayUsage('view')
            if len(temp):
                self.setObject('defaultView',temp[0])
    fixupDefaultView = utility.upgradeLimit(fixupDefaultView, 141)
    
    security.declarePrivate('fixupCurrentEdit')            
    def fixupCurrentEdit(self):
        "remove the currentEdit attribute"
        if 'currentEdit' in self.__dict__:
            self.delObjects(['currentEdit'])
    fixupCurrentEdit = utility.upgradeLimit(fixupCurrentEdit, 141)
    
    security.declarePrivate('removeBadEditName')        
    def removeBadEditName(self):
        "remvoe a bad edit name from this object"
        badName = self.getId()+'edit'
        if badName in self.__dict__:
            self.delObjects([badName])                
    removeBadEditName = utility.upgradeLimit(removeBadEditName, 141)

    security.declarePrivate('addUsageMapping')
    def addUsageMapping(self):
        """add a usage mapping object to look up usages faster and so displays don't need to
        be opened that are not needed should reduce memory usage and increase speed at the
        cost of a little disk space"""
        if self.usageMapping is None:
            self.usageMapping = {}
            for name,display in self.objectItems('Display'):
                self.usageMapping.setdefault(display.usage, []).append(name)
            self._p_changed = 1    
    addUsageMapping = utility.upgradeLimit(addUsageMapping, 144)
    
    security.declarePrivate('fixDefaultDisplay')
    def fixedDefaultDisplay(self):
        "fix the defaultEdit and defaultView items if they are set to non existant items"
        if self.defaultEdit and self.defaultEdit not in self.usageMapping.get('edit',[]):
            self.setObject('defaultEdit', '')
        if self.defaultView and self.defaultView not in self.usageMapping.get('view', []):
            self.setObject('defaultView', '')
        self.setAutoDisplay()
    fixedDefaultDisplay = utility.upgradeLimit(fixedDefaultDisplay, 145)
    
    security.declarePrivate('afterDeleteRegisteredObject')
    def afterDeleteRegisteredObject(self, name):
        "do something after a registered object is deleted"
        for defaultDisplay in self.get_default.itervalues():
            if name == getattr(self, defaultDisplay):
                self.setObject(defaultDisplay, '')
        self.removeMapping(name)
        self.setAutoDisplay()

    security.declarePrivate('removeMapping')
    def removeMapping(self, name):
        "remove a mapping item"
        for usage, displays in self.usageMapping.iteritems():
            if name in displays:
                displays.remove(name)
                self._p_changed = 1        
            
    security.declarePrivate('addMapping')        
    def addMapping(self, name):
        "add a mapping"
        display = getattr(self, name)
        if self.usageMapping is None:
            self.usageMapping = {}
        displayUsage = display.usage
        displays = self.usageMapping.setdefault(displayUsage, [])
        if name not in displays:
            displays.append(name)
            self._p_changed = 1
        for usage,displays in self.usageMapping.iteritems():
            if usage != displayUsage and name in displays:
                displays.remove(name)
                self._p_changed = 1        
            
    security.declarePrivate('cleanupDefaultDisplays')
    def cleanupDefaultDisplays(self, display):
        "make sure our default displays exist and are for the usage they have been set for"
        for usage, defaultDisplay in self.get_default.iteritems():
            displayName = getattr(self, defaultDisplay)
            if displayName == display.getId() and usage != display.usage:
                self.setObject(defaultDisplay, '')
        self.setAutoDisplay()
                
    
    #need to check if an item currently being g =used is missing or non existent
    #and then see if any of our current items could do that job        
                       
    security.declarePrivate("setAutoDisplay")
    def setAutoDisplay(self):
        "set the default filter to a filter if one is not already set"
        for usage, defaultDisplay in self.get_default.iteritems():
            displayName = getattr(self, defaultDisplay)
            if not displayName:
                displays = self.displayUsage(usage)
                if displays:
                    self.setObject(defaultDisplay, displays[0])
                
    security.declarePrivate('checkShared')
    def checkShared(self):
        "return true if we are in a shared object"
        cdoc = self.getCompoundDoc()
        return cdoc.masterLocation is not None and cdoc.masterLocation != cdoc.getPath()
                                        
Globals.InitializeClass(DisplayManager)
import register
register.registerClass(DisplayManager)