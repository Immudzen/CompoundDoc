# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from commonradio import CommonRadio

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ActionRadio(CommonRadio):
    "ActionRadio class"

    security = ClassSecurityInfo()
    meta_type = "ActionRadio"

    data = 0
    name = "Radio Button"

    classConfig = {}
    classConfig['name'] = {'name':'name', 'type':'string'}

    updateReplaceList = ('name',)
    configurable = ('name',)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return '<p>%s:%s</p>' % (self.getConfig('name'), self.true_false('data', self.data, 0))

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.data

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        try:
            self.setObject('data', bool(int(string)))
        except ValueError:
            pass
       
Globals.InitializeClass(ActionRadio)
import register
register.registerClass(ActionRadio)
