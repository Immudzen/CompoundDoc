#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class Button(UserObject):
    "Input text class"

    meta_type = "Button"
    security = ClassSecurityInfo()
    overwrite=1
    buttonTitle = "Submit Changes"

    classConfig = {'buttonTitle':{'name':'Button Title', 'type':'string'}}
    
    updateReplaceList = ('buttonTitle', )
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return self.create_button(self.buttonTitle, self.buttonTitle)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.getTitleFromObjectConfig()
            
    security.declarePrivate('getTitleFromObjectConfig')
    def getTitleFromObjectConfig(self):
        "if we have objectConfig try and get the title from it and use it for the button title"
        if 'objectConfig' in self.__dict__:
            self.setObject('buttonTitle', self.objectConfig['title'])
            del self.objectConfig['title']
    getTitleFromObjectConfig = utility.upgradeLimit(getTitleFromObjectConfig, 141)

Globals.InitializeClass(Button)
import register
register.registerClass(Button)
