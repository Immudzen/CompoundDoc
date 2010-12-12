# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from userobject import UserObject
import nocodestructured

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class TextArea(UserObject):
    "TextArea class"

    meta_type = "TextArea"
    security = ClassSecurityInfo()

    data = ''
    renderCache = ''
    struct = 1
    structstate = 1
    
    configurable = ('structstate', )

    security.declareProtected('View management screens', 'edit')
    def edit(self, struct=None, *args, **kw):
        "Inline edit short object"
        temp = self.text_area('data', self.data)
        if struct is not None:
            struct = self.struct
        if struct:
            format = '<div>%s Click "No" if you don\'t want your text auto-formatted.</div>'
            temp = temp + format % self.editSingleConfig('structstate')
        return temp

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return self.renderCache or self.data

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "update the render cache after all other changes"
        self.updateCache()

    security.declarePrivate('updateCache')
    def updateCache(self):
        "update the cache of this object if applicable"
        if self.getConfig('structstate'):
            self.setObject('renderCache', str(nocodestructured.HTML(self.data , header=0)))
        else:
            self.delObjects(['renderCache',])

    classConfig = {}
    classConfig['struct'] = {'name':'struct', 'type': 'radio'}
    classConfig['structstate'] = {'name':'Structured Text Enabled', 'type': 'radio'}

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.upgraderReplaceStructured()
        self.fixRenderCache()

    security.declarePrivate('upgraderReplacedStructured')
    def upgraderReplaceStructured(self):
        "replace structured object attribute with structstate config"
        if self.hasObject('structured'):
            structured = self.structured
            if structured == 'Y':
                structured = 1
            elif structured == 'N':
                structured = 0
            self.setObject('structstate', int(structured))
            self.delObjects(['structured'])
    upgraderReplaceStructured = utility.upgradeLimit(upgraderReplaceStructured, 141)
            
    security.declarePrivate('fixRenderCache')
    def fixRenderCache(self):
        "remove renderCache if stx is not enabled"
        self.updateCache()
    fixRenderCache = utility.upgradeLimit(fixRenderCache, 154)

    configKeep = ('structstate',)

    security.declarePrivate('configLoader')
    def configLoader(self, config):
        "load the config object for this textarea object"
        if config.hasObject('meta_type') and config.meta_type == 'Config':
            config = config.convertToDict()
        replaceEntries = [key for key in config if key not in self.configKeep]
        for key in replaceEntries:
            self.setObject(key,config[key])

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.data.replace('\n','\\n')

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        self.setObject('data',string.replace('\\n','\n'))
        self.updateCache()

    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, string):
        "set the calculation value of this object"
        self.setObject('data',str(string))
        self.updateCache()

Globals.InitializeClass(TextArea)
import register
register.registerClass(TextArea)
