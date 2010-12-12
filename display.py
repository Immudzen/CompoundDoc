import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class Display(base.Base):
    "This is a dispatcher for display filter objects based on the type of viewer request"

    meta_type = "Display"
    security = ClassSecurityInfo()
    overwrite=1


#quick hack remove later with a usage object
    security.declarePrivate('getAllowedUsages')
    def getAllowedUsages(self):
        "Get the allowed usages of a Display"
        return ['edit', 'view']

    description = ''
    usage = 'view'
    defaultFilter = ''

    security.declarePrivate('afterDeleteRegisteredObject')
    def afterDeleteRegisteredObject(self, name):
        "do something after a registered object is deleted"
        self.setAutoDefaultFilter()

    security.declarePrivate('afterAddRegisteredObject')
    def afterAddRegisteredObject(self, name, metatype):
        "do something after a registered object has been added"
        if metatype == 'DisplayFilter':
            self.setAutoDefaultFilter()

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self,dict):
        "after a display is edited notify the parent of our usage"
        self.DisplayManager.addMapping(self.getId())            
        self.DisplayManager.cleanupDefaultDisplays(self)
            
    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        filters = self.objectValues('DisplayFilter')
        if len(filters) == 1:
            f = filters[0]
            if not 'header' in self.REQUEST.other: #used to check if a render is already default
                if not 'DisplayFilter' in self.REQUEST.other:
                    self.REQUEST.other['DisplayFilter'] = f
            return f.view()
        filters = sorted(i.willRender() for i in filters)
        if filters:
            first = filters.pop()
            #check for match on browser and language
            if first[0] != 0:
                filter = first.pop()
                if not 'DisplayFilter' in self.REQUEST.other:
                    self.REQUEST.other['DisplayFilter'] = filter
                return filter.view()
        if self.defaultFilter:
            filter = getattr(self, self.defaultFilter)
            if not 'DisplayFilter' in self.REQUEST.other:
                self.REQUEST.other['DisplayFilter'] = filter
            return filter.view()
        else:
            return ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = ["<p>Usage is : %s</p>\n" % self.option_select(self.getAllowedUsages(),
                      'usage', [self.usage])]
        displayIds = self.objectIds('DisplayFilter')
        if displayIds:
            temp.append("<p>Default Filter is : %s</p>\n" % self.option_select(displayIds,
                        'defaultFilter', [self.defaultFilter]))
        temp.append(self.addDeleteObjectsEdit())
        temp.append('<p>Description:</p>')
        temp.append(self.text_area('description', self.description))
        return ''.join(temp)

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        return ['DisplayFilter']

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

    security.declarePrivate("setAutoDefaultFilter")
    def setAutoDefaultFilter(self):
        "set the default filter to a filter if one is not already set"
        filters = self.objectIds('DisplayFilter')
        currentFilter = self.defaultFilter
        if currentFilter not in filters:
            currentFilter = None
        if not currentFilter and len(filters):
            self.setObject("defaultFilter", filters[0])

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.upgraderChangeDisplayObjectRef()
        self.removeOldVars()

    security.declarePrivate('removeOldVars')
    def removeOldVars(self):
        "remove some old variables"
        self.delObjects(['alias', 'registeredFilters'])
    removeOldVars = utility.upgradeLimit(removeOldVars, 141)    
        
    security.declarePrivate('upgraderChangeDisplayObjectRef')
    def upgraderChangeDisplayObjectRef(self):
        "Change the object refs in default edit to a name instead"
        id = self.getId()
        default = 'defaultFilter'
        self.delObjects([id+'edit'])
        try:
            self.setObject(default, getattr(self, default).getId())
        except AttributeError:
            pass
    upgraderChangeDisplayObjectRef = utility.upgradeLimit(upgraderChangeDisplayObjectRef, 141)

Globals.InitializeClass(Display)
import register
register.registerClass(Display)