###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from AccessControl import ClassSecurityInfo
import Globals

from autocreator import AutoCreator

class AutoPopulator(AutoCreator):
    "auto object poluator class"

    security = ClassSecurityInfo()
    meta_type = "AutoPopulator"

    security.declarePrivate('createTreeFromDataSource')
    def createTreeFromDataSource(self, data):
        "create a zope tree structure based on a data source"
        try:
            folder = self.restrictedTraverse(self.startFolder)
            self.createDocuments(folder, data)
        except AttributeError:
            pass

    security.declareProtected('Change CompoundDoc', 'createDocuments')
    def createDocuments(self, folder, data):
        "create documents at this path using this data"
        entries = [entry.split('\n') for entry in data.split('\n\n\n')]
        pathEntries = [(entry[0].split(' ', 1), entry[1:]) for entry in entries]
        try:
            for (path, profile), entries in pathEntries:
                self.createCdocAtLocation(path, profile, folder, entries)
        except ValueError: #Catches when the data format is wrong
            pass
        self.getCompoundDoc().processChanges()

Globals.InitializeClass(AutoPopulator)
import register
register.registerClass(AutoPopulator)