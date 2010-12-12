#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals


class CreationAssistantString(base.Base):
    "CreationAssistantString class can set string attributes of an object to a specified value after creation"

    meta_type = "CreationAssistantString"
    security = ClassSecurityInfo()
    overwrite=1
    metaType = ''
    idValueMapping = None

    security.declareProtected('View management screens', 'edit')
    def edit(self):
        "Inline edit short object"
        return ''

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return ''

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "Process edits."
        if 'idValueMapping' in dict:
            for i,j in dict['idValueMapping'].items():
                key,value = j
                if key and value:
                    if self.idValueMapping is None:
                        self.idValueMapping = {}
                    self.idValueMapping[key] = value
                else:
                    del self.idValueMapping[i]
                    if not len(self.idValueMapping):
                        self.idValueMapping = None
                self._p_changed=1

        key, value = dict['idValueMappingNew']
        if key and value:
            if self.idValueMapping is None or not key in self.idValueMapping:
                if self.idValueMapping is None:
                    self.idValueMapping = {}
                self.idValueMapping[key] = value
                self._p_changed=1

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        available =[''] + self.getCompoundDoc().availableObjects()
        temp = []
        temp.append('<p>Object Text:%s</p>' % self.option_select(available, 'metaType', [self.metaType]))
        typeformat = '<p>Id: %s Text:%s</p>'
        if self.idValueMapping is not None:
            for i,j in self.idValueMapping.items():
                temp.append(typeformat % (self.input_text(i, i, containers=('idValueMapping',)),
                  self.text_area(i, j, containers=('idValueMapping',))))
        temp.append(typeformat % (self.input_text('idValueMappingNew'),
          self.text_area('idValueMappingNew')))
        return ''.join(temp)

    security.declarePrivate('setupObject')
    def setupObject(self, object):
        "if this object is the kind we are looking for create the other items we need in it"
        if self.idValueMapping is not None and object.meta_type == self.metaType:
            [object.updateObject(id, value) for id,value in self.idValueMapping.items()]

Globals.InitializeClass(CreationAssistantString)
import register
register.registerClass(CreationAssistantString)