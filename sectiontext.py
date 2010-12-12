# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from textarea import TextArea
import types
import nocodestructured

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class SectionText(TextArea):
    "SectionText class"

    meta_type = "SectionText"
    security = ClassSecurityInfo()

    header = '2'
    heading = ''

    classConfig = {}
    classConfig['struct'] = {'name':'struct', 'type': 'radio'}
    classConfig['structstate'] = {'name':'Structured Text Enabled', 'type': 'radio'}
    classConfig['header'] = {'name':'header', 'type':'list', 'values': ['1', '2', '3', '4', '5', '6']}
    classConfig['heading'] = {'name':'heading', 'type': 'string'}

    configKeep = ('structstate', 'header')
    configurable = ('structstate', 'header')


    security.declareProtected('View management screens', 'edit')
    def edit(self, struct=None, *args, **kw):
        "Inline edit short object"
        temp = [self.editSingleConfig('heading'), self.text_area('data', self.data)]
        if struct is not None:
            struct = self.struct
        if struct:
            format = '<div>%s Click "No" if you don\'t want your text auto-formatted.</div>'
            temp.append(format % self.editSingleConfig('structstate'))
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        if self.getConfig('structstate'):
            return self.renderCache
        else:
            return self.renderCache + self.data
        
    security.declarePrivate('updateCache')
    def updateCache(self):
        "update the cache of this object if applicable"
        string = ''
        heading = self.heading
        if heading:
            header = self.getConfig('header')
            string = '<h%s>%s</h%s>\n' % (header, heading, header)
        if self.getConfig('structstate'):
            string = string + str(nocodestructured.HTML(self.data , header=0))
        self.setObject('renderCache', string)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.upgradeStringToAttributeText()
        self.removeAttributeText()

    security.declarePrivate('upgradeStringToAttributeText')
    def upgradeStringToAttributeText(self):
        "upgrade a string header to an attributetext one"
        if isinstance(self.heading, types.StringType):
            self.addRegisteredObject('heading', 'AttributeText', data=self.heading)        
    upgradeStringToAttributeText = utility.upgradeLimit(upgradeStringToAttributeText, 141)
            
    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return '%s /-\ %s' % (self.heading, self.data.replace('\n', '\\n'))

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        heading, data = string.split(' /-\ ', 1)
        self.setObject('data', data.replace('\\n', '\n'))
        self.setObject('heading', heading.replace('\\n', '\n'))
        self.updateCache()

    security.declarePrivate('removeAttributeText')
    def removeAttributeText(self):
        "remove the attributetext items and replace them with basic attributes"
        heading = self.heading.data
        self.delObjects(('heading',))
        self.setObject('heading', heading)
        self.updateCache()
    removeAttributeText = utility.upgradeLimit(removeAttributeText, 149)

    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, data, heading):
        "set the calculation value of this object"
        self.setObject('data',str(data))
        self.setObject('heading', str(heading))
        self.updateCache()

Globals.InitializeClass(SectionText)
import register
register.registerClass(SectionText)