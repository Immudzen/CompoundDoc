# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from attributebase import AttributeBase

class AttributeText(AttributeBase):
    "This is the AttributeText object and it defines an attribute for storing and editing text for a cdoc"

    meta_type = "AttributeText"
    security = ClassSecurityInfo()
    data = ''
    title = ''

    security.declarePrivate('__init__')
    def __init__(self, id, data=None, title=None):
        "Initialize a new base"
        self.id = id
        if data is not None:
            self.data = data
        if title is not None:
            self.title = title

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        """This is the edit dispatcher. It should dispatch to the appropriate
        object edit view."""
        return '<p>%s: %s</p>\n' % (self.title_or_id().capitalize(), self.input_text('data', self.data))

    security.declareProtected('View management screens', 'config')
    def config(self):
        "return the configuration for this object which is just editing the title"
        return '<p>%s %s: %s</p>\n' % ('Title of ', self.getId(), self.input_text('title', self.data))

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.data.replace('\n', '\\n')

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        self.setObject('data', string.replace('\\n', '\n'))

Globals.InitializeClass(AttributeText)
import register
register.registerClass(AttributeText)