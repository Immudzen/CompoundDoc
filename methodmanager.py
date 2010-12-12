###########################################################################
#    Copyright (C) 2005 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################


#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from base import Base
import utility

class MethodManager(Base):
    "IMethod object which binds a remote callable object"

    security = ClassSecurityInfo()
    meta_type = "MethodManager"
    lookup = None
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        typeformat = '<div>name: %s path:%s</div>'
        lookup = sorted(self.getLookup().items())
        lookup.append(('',''))
        for index, (nameValue, pathValue) in enumerate(lookup):
            temp.append(typeformat % (self.input_text('name', nameValue, containers=('lookup', str(index))),
              self.input_text('path', pathValue,  containers=('lookup', str(index)))))
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        lookup = dict.pop('lookup', None)
        if lookup is not None:
            temp = {}
            for i, j in lookup.items():
                temp[int(i)] = j
            temp = ((dictionary['name'].strip(), dictionary['path'].strip()) for index, dictionary in sorted(temp.iteritems))
            cleaned = [(name, display) for name, display in temp if name and display]
            if len(cleaned):
                temp = {}
                for name, display in cleaned:
                    temp[name] = display
                self.setObject('lookup', temp)
            else:
                self.delObjects(('lookup',))
    
    security.declarePrivate('getMethod')
    def getMethod(self, name):
        "Inline draw view"
        cdoc = self.getCompoundDocContainer()
        path = self.getLookup()[name]
        item = cdoc.restrictedTraverse(path,None)
        if item is not None:
           return cdoc.changeCallingContext(item) 

    security.declareProtected('Access contents information', '__contains__')
    def __contains__(self, name):
        "see if name is in me"
        return name in self.getLookup()
    
    security.declarePrivate('getLookup')
    def getLookup(self):
        "get the current lookup variable"
        if self.lookup is not None:
            return self.lookup
        return {}

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.transferAndDelete()

    security.declarePrivate('transferAndDelete')
    def transferAndDelete(self):
        "transfer all the data to the LinkManager object and delete this one"
        cdoc = self.getCompoundDoc()
        link = cdoc.LinkManager
        for name,path in self.getLookup().items():
            link.addPath(path)
        cdoc.delObjects([self.getId()])
    transferAndDelete = utility.upgradeLimit(transferAndDelete, 147)

Globals.InitializeClass(MethodManager)
import register
register.registerClass(MethodManager)