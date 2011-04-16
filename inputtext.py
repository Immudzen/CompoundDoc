#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class InputText(UserObject):
    "Input text class"

    security = ClassSecurityInfo()
    meta_type = "InputText"
    data = ''
    inputType = 'Text'
    
    allowedListTypes = ('Text',  'Color')
    
    typeLookup = {}
    typeLookup['Text'] = ''
    typeLookup['Color'] = 'color_picker'

    classConfig = {}
    classConfig['inputType'] = {'name':'Type of Input', 'type':'list', 'values': allowedListTypes}
    
    updateReplaceList = ('inputType', )
    
    configurable = ('inputType',)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        inputType = self.typeLookup[self.getConfig('inputType')]
        return self.input_text('data', self.data,  cssClass=inputType)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.data

    security.declarePrivate('createDataLoader')
    def createDataLoader(self):
        "return the data needed to rebuild this object as a dictionary that it can then take back to restore its information"
        return {'data': self.data}

    security.declarePrivate('dataLoader')
    def dataLoader(self, dict):
        "load the data from this dict into this object"
        if 'data' in dict:
            self.setObject('data', dict['data'])

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.data.replace('\n','\\n')

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        self.setObject('data',string.replace('\\n','\n'))
        
    security.declareProtected('Change CompoundDoc', 'store')
    def store(self, string):
        "set the calculation value of this object"
        self.setObject('data',str(string))

Globals.InitializeClass(InputText)
import register
register.registerClass(InputText)
