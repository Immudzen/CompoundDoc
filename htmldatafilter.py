# -*- coding: utf-8 -*-
import datafilter

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class HTMLDataFilter(datafilter.DataFilter):
    "HTMLDataFilter apply this to an a list of dicts to make it output a table"

    meta_type = "HTMLDataFilter"
    security = ClassSecurityInfo()

    security.declareProtected('View', 'view')
    def view(self, archive=None, order=None, start=None, stop=None, header=1, query=None, merge=None):
        "Inline draw view"
        if order is None:
            order = self.getFieldOrder()
            
        records = self.getDataRecords(order, archive=archive, start=start, stop=stop, header=header, query=query, merge=merge)
        output = self.createTable(records)
        if output:
            return output
        else:
            return '<p>No Drawable Data Found</p>'

Globals.InitializeClass(HTMLDataFilter)
import register
register.registerClass(HTMLDataFilter)