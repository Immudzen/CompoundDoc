# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from AccessControl import ClassSecurityInfo
import Globals
import zExceptions

from base import Base

class AutoCreatorGetter(Base):
    "auto object creator getter class which can construct data to be used by the auto creator"

    security = ClassSecurityInfo()
    meta_type = "AutoCreatorGetter"

    startFolder = ''
    
    classConfig = {}
    classConfig['startFolder'] = {'name':'What location do you want to start at?', 'type':'string'}
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = [self.editSingleConfig('startFolder')]
        temp.append(self.text_area('returnedData', '\n'.join(self.createDataSourceFromTree())))
        return '<br>'.join(temp)

    security.declarePrivate('createDataSourceFromTree')
    def createDataSourceFromTree(self):
        "create an appropriate data source to be used to create another cdoc structure based on what is below folder"
        try:
            return ['%s %s' % (path, profile) for path, profile, object in self.getCdocList()]
        except AttributeError:
            return ['Bad folder Location Given']

    security.declarePrivate('getCdocList')
    def getCdocList(self):
        "return the list of cdocs from startFolder"
        folderUrl = '%s/' % self.restrictedTraverse(self.startFolder).absolute_url_path()

        cdoclist = []
        for i in self.CDocUpgrader(path=folderUrl):
            try:
                profile = i.profile
                object = i.getObject()
                if profile and object is not None:
                    path = i.getPath().replace(folderUrl,'')
                    cdoclist.append((path, profile, object))
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                pass
                
        cdoclist.sort()
        return cdoclist

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

Globals.InitializeClass(AutoCreatorGetter)
import register
register.registerClass(AutoCreatorGetter)