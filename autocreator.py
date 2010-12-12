###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from AccessControl import ClassSecurityInfo
import Globals

from base import Base
from Acquisition import aq_base

class AutoCreator(Base):
    "auto object creator class"

    security = ClassSecurityInfo()
    meta_type = "AutoCreator"

    startFolder = ''
    filters = None
    
    classConfig = {}
    classConfig['startFolder'] = {'name':'What location do you want to start at?', 'type':'string'}
    classConfig['loadableDataFile'] = {'name':'Load the data from this file:', 'type':'file'}        
    
    security.declarePrivate('getFilters')
    def getFilters(self):
        "return a list of tuples for filters we can use"
        temp = [('', 'No Filter')]
        filters = {}
        if self.filters is not None:
            filters = self.filters
        temp.extend([(value, key) for key, value in filters.items()])
        return sorted(temp)

    security.declarePrivate('configAddition')
    def configAddition(self):
        "create the config interface needed to add scripts as filters"
        temp = []
        typeformat = '<div>Filter Name: %s Script Path:%s</div>'
        filters = {}
        if self.filters is not None:
            filters = self.filters
        items = list(filters.items()) + [('','')]
        for index, (filterName, scriptPath) in enumerate(items):
            temp.append(typeformat % (self.input_text('filterName', filterName, containers=('tabMapping', str(index))),
              self.input_text('scriptPath', scriptPath, containers=('tabMapping', str(index)))))
        return ''.join(temp)

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        tabMapping = dict.pop('tabMapping', None)
        if tabMapping is not None:
            temp = {}
            for i, j in tabMapping.items():
                temp[int(i)] = j
            temp = ((dic['filterName'].strip(), dic['scriptPath'].strip()) for index, dic in sorted(temp.iteritems()))
            cleaned = [(filterName, scriptPath) for filterName, scriptPath in temp if filterName and scriptPath]
            if len(cleaned):
                temp = {}
                for filterName, scriptPath in cleaned:
                    temp[filterName] = scriptPath
                self.setObject('filters', temp)
            else:
                self.delObjects(('filters', ))

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = [self.editSingleConfig('startFolder')]
        temp.append('<p>Filter Script:%s</p>' % self.option_select(self.getFilters(), 'filterScript', selected=['No Filter']))
        temp.append(self.text_area('loadableData', ''))
        temp.append(self.editSingleConfig('loadableDataFile'))
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, dict):
        "Process edits."
        scriptPath = dict.get('filterScript', '')
        loadableData =  dict.get('loadableData', '')
        loadableDataFile = dict.get('loadableDataFile', '')
        if scriptPath:
            script = self.restrictedTraverse(scriptPath, None)
            if script is not None:
                loadableData = script(loadableData)
                loadableDataFile = script(loadableDataFile)
        self.createTreeFromDataSource(loadableDataFile)
        self.createTreeFromDataSource(loadableData)

    security.declarePrivate('createTreeFromDataSource')
    def createTreeFromDataSource(self, data):
        "create a zope tree structure based on a data source"
        try:
            folder = self.restrictedTraverse(self.startFolder)
            paths = [line.split(' ', 1) for line in data.split('\n')]
            try:
                for path, profile in paths:
                    self.createCdocAtLocation(path, profile, folder)
            except ValueError: #Catches when the data format is wrong
                pass
        except AttributeError:
            pass

    security.declarePrivate('createCdocAtLocation')
    def createCdocAtLocation(self, path, profile, container, entries=None):
        "create a cdoc along with path element with this profile"
        pathList = path.split('/')
        cdocId = pathList.pop()
        cursor = container
        for name in pathList:
            if not hasattr(aq_base(cursor), name):
                cursor.manage_addProduct['OFSP'].manage_addFolder(name)
            cursor = getattr(cursor, name)
        if not hasattr(aq_base(cursor), cdocId):
            cdoc = cursor.manage_addProduct['CompoundDoc'].manage_addCompoundDoc(cdocId, profile=profile, redir=0, returnObject=1)
        else:
            cdoc = getattr(cursor, cdocId)
            if cdoc.profile != profile:
                cdoc.changeProfile(profile)
        if entries is not None:
            cdoc.loadPopulatorInformation(entries)

Globals.InitializeClass(AutoCreator)
import register
register.registerClass(AutoCreator)