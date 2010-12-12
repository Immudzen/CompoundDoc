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

import os.path

class FreightOrderListing(Base):
    "return a list structure based on all the freightcompanywatchers we are using that has only the commonalities"

    meta_type = "FreightOrderListing"
    security = ClassSecurityInfo()
    annonymousEditAccepted = 1
    freightLocation = ''
    freightLimit = 0.0
    staticCost = 0.0
    
    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the cart actions and update the session data to the new information"
        if 'freight' in form and form['freight']:
            manager = self.SessionManagerConfig.getSessionManager()
            if manager.hasSessionData():
                sessionData = manager.getSessionData()
                freightList = sessionData.get('freightList',None)
                if freightList is None:
                    return None
                freightClass, freightCost = form['freight'].split('$')
                freightCost = float(freightCost)
                freightClass = freightClass.strip()
                if (freightCost,freightClass) in freightList:
                    sessionData.set('freightClass', freightClass)
                    sessionData.set('freightCost', freightCost)
                else:
                    self.recalculateFreight()

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        try:
            sessionData = self.SessionManagerConfig.getSessionManager().getSessionData()
            format = '%s  $%.2f'
            freightList = sessionData.get('freightList',[])
            formattedList = [format % (name,value) for value,name in freightList]
            freightClass = sessionData.get('freightClass', None)
            if freightClass is not None:
                selected = format % (freightClass, sessionData.get('freightCost', 0.0))
            else:
                selected = formattedList[0]
            return self.option_select(formattedList, 'freight', [selected])
        except (AttributeError,KeyError):
            return ""

    security.declarePrivate('recalculateFreight')
    def recalculateFreight(self):
        "recalculate the freight cost and selection"
        try:
            sessionData = self.SessionManagerConfig.getSessionManager().getSessionData()
            #find all dicts that we need and stick them in this list
            freights = {}
            subTotal = self.getSubTotal()
            try:
                for (path,args),number in sessionData['orders'].items():
                    freightpath = os.path.join(path,self.freightLocation)
                    try:
                        listing = self.unrestrictedTraverse(freightpath).getAllFreightCompanyListings()
                        for freightMethod,cost in listing.items():
                            if self.staticCost:
                                freightCost = self.staticCost
                            elif not self.staticCost and self.freightLimit and subTotal > self.freightLimit:
                                freightCost = 0.0
                            else:
                                freightCost = number*cost + freights.get(freightMethod,0)
                            freights[freightMethod] = freightCost
                    except (AttributeError, KeyError):
                        pass
            except KeyError:
                pass
            freightList = sorted((value, key) for key, value in freights.items())
            if len(freightList):
                lowestFreightPrice, lowestFreightClass = freightList[0]
                try:
                    currentFreightPrice = freights[sessionData['freightClass']]
                except KeyError:
                    currentFreightPrice = 0.0
                if currentFreightPrice == lowestFreightPrice:
                    sessionData.set('freightCost', lowestFreightPrice)
                else:
                    sessionData.set('freightCost', lowestFreightPrice)
                    sessionData.set('freightClass', lowestFreightClass)
            sessionData.set('freightList', freightList)
        except (AttributeError, KeyError):
            pass

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        format = '<p>Freight Location:%s</p><p>Freight Limit:%s</p><p>Static Freight Cost: %s</p>'
        return format % (self.input_text('freightLocation', self.freightLocation),
          self.input_float('freightLimit', self.freightLimit), self.input_float('staticCost', self.staticCost))

Globals.InitializeClass(FreightOrderListing)
import register
register.registerClass(FreightOrderListing)