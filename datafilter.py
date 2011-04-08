# -*- coding: utf-8 -*-
from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import utility

import BTrees.OOBTree

class DataFilter(UserObject):
    "DataFilter apply this to an a list of dicts to change how it outputs"

    meta_type = "DataFilter"
    security = ClassSecurityInfo()
    fieldMap = None
    order = None
    visible = None

    updateReplaceList = ('order', 'visible')
    
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ""
    
    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        temp = []
        append = temp.append
        if self.fieldMap is not None and self.order is not None:
            fieldMapKeys = sorted(self.fieldMap.keys())
            dictMap = "fieldMap.%s"
            orderMap = "order.%s"

            elements = [['id','name','order']]
            for i in fieldMapKeys:
                mappedEdit = self.input_text(dictMap % i, self.fieldMap[i])
                orderEdit = self.input_float(orderMap % i, self.order[i])
                elements.append([i,mappedEdit,orderEdit])

            append(self.create_button('clear','Clear Visible Items'))
            append('<br>')
            append(self.option_select(self.fieldMap.keys(), 'visible',self.getVisible(), 1,5))
            append(self.createTable(elements))
        append(self.customEdit())
        return ''.join(temp)

    security.declarePrivate('customEdit')
    def customEdit(self):
        "This is an edit piece that can be overridden by various custom editing features needed by other filters"
        return ""

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        if 'clear' in form:
            self.delObjects(('visible',))
            if 'visible' in form:
                del form['visible']

    security.declarePrivate('getFieldMapKeys')
    def getFieldMapKeys(self):
        "Get the keys to the fieldMap object"
        if self.fieldMap is not None:
            return self.fieldMap.keys()
        return []

    security.declarePrivate('getVisible')
    def getVisible(self):
        "get the visible items"
        if self.visible is not None:
            return self.visible
        return []

    security.declarePrivate('getOrderKeys')
    def getOrderKeys(self):
        "Get the keys to the fieldMap object"
        if self.order is not None:
            return self.order.keys()
        return []

    security.declarePrivate('getFieldOrder')        
    def getFieldOrder(self):
        "get the current field order"
        path = self.aq_parent.getConfig('orderHeaderPath')
        script = None
        if path:
            script = self.restrictedTraverse(path, None)
            if script is not None:
                return script(self.getCompoundDoc())
        
        if self.order is not None and self.visible is not None and self.fieldMap is not None:
            order = sorted((value, key) for key, value in self.order.items())
            visible = set(self.visible)
            fieldMap = self.fieldMap
            return [(name, fieldMap[name]) for i,name in order if name in visible]
        return []
            
    def getDataRecords(self, order, archive=None, start=None, stop=None, header=None, query=None, merge=None, sliceStart=None, sliceStop=None, keys=None):
        "get the records in this data recorder that match these constraints"
        if not order:
            return
        
        if merge is not None:
            records = BTrees.OOBTree.OOBTree()
            if self.records is not None:
                records.update(self.records)
            if self.archive is not None:
                records.update(self.archive)
        elif archive:
            records = self.archive
        else:
            records = self.records

        if records is None:
            return
        
        if start is None and self.startTime is not None:
            startTime = self.startTime(mode='view')
            if startTime:
                start = startTime
            
        if stop is None and self.stopTime is not None:
            stopTime = self.stopTime(mode='view')
            if stopTime:
                stop = stopTime
                
        recordOrder, recordNames = zip(*order)
            
        allowed = None
        
        if query is not None:
            catalog = self.getCatalog(archive)
            if catalog is not None:
                allowed = set(float(record.id) for record in catalog(query))
            
        if header:
            yield recordNames

        recordsGen = None
        if allowed is None:
            if sliceStart is not None and sliceStop is not None:
                recordsGen = records.items(start, stop)[sliceStart:sliceStop]
            else:
                recordsGen = records.items(start, stop)
        else:
            if sliceStart is not None and sliceStop is not None:
                recordsGen = ( (name,value) for name, value in records.items(start, stop)[sliceStart:sliceStop] if name in allowed)
            else:
                recordsGen = ( (name,value) for name, value in records.items(start, stop) if name in allowed)
            
        
        if recordsGen is not None:
            for key,record in utility.subTransDeactivateKeyValue(recordsGen,  100, self.getPhysicalRoot()._p_jar.cacheGC):
                if keys:
                    yield key,[str(record.get(key, '')) for key in recordOrder]
                else:
                    yield [str(record.get(key, '')) for key in recordOrder]

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeNotUsed()

    security.declarePrivate('removeNotUsed')
    def removeNotUsed(self):
        "remove visible, fieldMap, order if not being used"
        toRemove = []
        if not self.visible:
            toRemove.append('visible')
        if not self.fieldMap:
            toRemove.append('fieldMap')
        if not self.order:
            toRemove.append('order')
        self.delObjects(toRemove)
    removeNotUsed = utility.upgradeLimit(removeNotUsed, 158)

Globals.InitializeClass(DataFilter)
