# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

from base import Base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class FreightCompanyWatcher(Base):
    "watch a FreightCompanyCreator for changes and apply them internally when they do"

    meta_type = "FreightCompanyWatcher"
    security = ClassSecurityInfo()
    freightCompanyCreatorPath = ''

    def after_manage_edit(self, dict):
        "Process edits."
        object = self.getRemoteObject(self.freightCompanyCreatorPath, 'FreightCompanyCreator')
        if object is not None:
            self.observerUpdate()
            object.observerAttached(self)
        if self.hasBeenModified():
            self.genFreightCompanyListings()

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declarePrivate('observerUpdate')
    def observerUpdate(self, object=None):
        "Process what you were observing"
        freightCompanyCreator = self.getRemoteObject(self.freightCompanyCreatorPath, 'FreightCompanyCreator')
        if freightCompanyCreator is not None:
            containedObjects = freightCompanyCreator.getFreightCompanies()
            cleanNames = [utility.cleanRegisteredId(id) for id in containedObjects]
            for id in self.objectIds('FreightCompany'):
                if id not in cleanNames:
                    self.delObjects([id])
            for id,name in zip(cleanNames,containedObjects):
                if not self.hasObject(id):
                    self.addRegisteredObject(id, 'FreightCompany')
                    getattr(self, id).freightCompanyName = name

            freightClasses = freightCompanyCreator.getFreightClasses()
            for object in self.objectValues('FreightCompany'):
                object.syncFreightClasses(freightClasses)
            self.genFreightCompanyListings()

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append(self.input_text('freightCompanyCreatorPath', self.freightCompanyCreatorPath))
        seq = sorted(self.objectItems('FreightCompany'))
        temp.extend((object.edit() for name,object in seq))
        return ''.join(temp)

    security.declarePrivate('genFreightCompanyListings')
    def genFreightCompanyListings(self):
        "generate the freight company listing dict"
        listing = {}
        for company in self.objectValues('FreightCompany'):
            listing.update(company.getFreightCompanyListing())
        self.setObject('listing', listing)

    security.declarePrivate('getAllFreightCompanyListings')
    def getAllFreightCompanyListings(self):
        "return the listing for all the freight companies"
        if not self.hasObject('listing'):
            self.genFreightCompanyListings()
        return self.listing

    security.declarePrivate('eventProfileLast')
    def eventProfileLast(self):
        "run this event as the last thing the object will do before the profile is returned"
        object = self.getRemoteObject(self.freightCompanyCreatorPath, 'FreightCompanyCreator')
        if object is not None:
            self.observerUpdate()
            self.genFreightCompanyListings()
            object.observerAttached(self)

Globals.InitializeClass(FreightCompanyWatcher)
import register
register.registerClass(FreightCompanyWatcher)
