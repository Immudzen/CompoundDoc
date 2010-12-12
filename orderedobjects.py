###########################################################################
#    Copyright (C) 2007 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class OrderedObjects(UserObject):
    "Order a list of objects for later usage"

    security = ClassSecurityInfo()
    meta_type = "OrderedObjects"
    data = None
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, allowedData=None, *args, **kw):
        "Inline edit short object"
        cdoc = self.getCompoundDoc()
        temp = []
        for index, (key, value) in enumerate(self.getChoices(allowedData)):
            temp.append((self.input_number(key, index, containers=['order']), value))
        return self.createTable(temp)

    security.declareProtected('View', 'view')
    def view(self, allowedData=None):
        "Inline draw view"
        return [key for key,value in self.getChoices(allowedData)]
    
    def getChoices(self, allowedData=None):
        "get the allowed choices to work with in the right order"
        if allowedData is None:
            allowedData = {}
        renderData = []
        if self.data is not None:
            for path in self.data:
                if path in allowedData:
                    renderData.append((path, allowedData[path]))
                    del allowedData[path]
            renderData.extend(allowedData.items())
        else:
            renderData = allowedData.items()
        return renderData

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        order = form.pop('order', None)
        if order is not None:
            temp = [(value,key) for key,value in order.items()]
            temp.sort()
            self.setObject('data', [key for value,key in temp])

Globals.InitializeClass(OrderedObjects)
import register
register.registerClass(OrderedObjects)
