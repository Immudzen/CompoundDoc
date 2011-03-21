#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CreationAssistant(base.Base):
    "CreationAssistant class this object can bind to a type and then fill that object with other data types on creation"

    meta_type = "CreationAssistant"
    security = ClassSecurityInfo()
    metaType = ''
    idTypeMapping = None

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "Process edits."
        allowed = self.availableObjects()
        #Items that have been removed
        deleted = []
        if 'idTypeMapping' in dict:
            for i, j in dict['idTypeMapping'].items():
                key, value = j
                if key and value and value in allowed:
                    if self.idTypeMapping is None:
                        self.idTypeMapping = {}
                    self.idTypeMapping[key] = value
                else:
                    del self.idTypeMapping[i]
                    if not len(self.idTypeMapping):
                        self.idTypeMapping = None
                    deleted.append(i)
                self._p_changed=1

        key, value = dict['idTypeMappingNew']
        if key and value and value in allowed:
            if self.idTypeMapping is None or not key in self.idTypeMapping:
                if self.idTypeMapping is None:
                    self.idTypeMapping = {}
                self.idTypeMapping[key] = value
                self._p_changed=1

            for i in self.aq_parent.objectValues(self.metaType):
                self.setupObject(i)

        if deleted and self.meta_type == 'CreationAssistant':
            [i.delObjects(deleted) for i in self.aq_parent.objectValues(self.metaType)]

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        available =[''] + self.aq_parent.availableObjects()
        temp = []
        temp.append('<p>Object Type:%s</p>' % self.option_select(available, 'metaType', [self.metaType]))
        typeformat = '<p>Id: %s Type:%s</p>'
        available =[''] + self.availableObjects()
        if self.idTypeMapping is not None:
            for i, j in self.idTypeMapping.items():
                temp.append(typeformat % (self.input_text(i, i, containers=('idTypeMapping',)),
                  self.option_select(available, i, [j], containers=('idTypeMapping',))))
        temp.append(typeformat % (self.input_text('idTypeMappingNew'),
          self.option_select(available, 'idTypeMappingNew')))
        return ''.join(temp)

    security.declarePrivate('setupObject')
    def setupObject(self, object):
        "if this object is the kind we are looking for create the other items we need in it"
        if self.idTypeMapping is not None and object.meta_type == self.metaType:
            for id, type in self.idTypeMapping.items():
                object.updateRegisteredObject(id, type)    


Globals.InitializeClass(CreationAssistant)
import register
register.registerClass(CreationAssistant)