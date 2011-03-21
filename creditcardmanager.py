###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CreditCardManager(base.Base):
    "CreditCardManager manages all displays"

    meta_type = "CreditCardManager"
    security = ClassSecurityInfo()

    creditCardProcessor = None
    creditCard = None
    ordersLocation = ''
    processedVar = ''
    processedOkayVar = ''
    shoppingCartLocation = ''

    classConfig = {}
    classConfig['ordersLocation'] = {'name':'Order Folder Location:', 'type':'string'} 
    classConfig['processedVar'] = {'name':'Processed Var Name:', 'type':'string'}
    classConfig['processedOkayVar'] = {'name':'Processed Okay Var Name:', 'type':'string'} 
    classConfig['shoppingCartLocation'] = {'name':'Shopping Cart Location:', 'type':'string'}   

    security.declarePrivate('configAddition')
    def configAddition(self):
        "Inline edit view"
        temp = []
        processors = ['Disabled'] + self.restrictedUserObject()
        temp.append('<p>Credit Card Processor: %s</p>' % self.option_select(processors, 'creditCardProcessor',
          [self.creditCardProcessor]))
        return ''.join(temp)

    security.declarePrivate('getShoppingCart')
    def getShoppingCart(self):
        "return the shopping card object"
        if self.shoppingCartLocation:
            return self.getCompoundDocContainer().restrictedTraverse(self.shoppingCartLocation,None)    
    
    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        if 'creditCardProcessor' in dict:
            ccType = dict['creditCardProcessor']
            if ccType == 'Disabled':
                self.setObject('creditCard', None)
                return
            if self.creditCard is None:
                self.addRegisteredObject('creditCard', ccType)
                return
            elif self.creditCard is not None and self.creditCard.meta_type != ccType:
                self.addRegisteredObject('creditCard', ccType)
                return

    security.declarePrivate('restrictedUserObject')
    def restrictedUserObject(self):
        "Return a list of the types that are allowed to be added or deleted from this object by a user"
        return ['CreditCardECHO', 'CreditCardVerisignPaymentLink']

    security.declarePrivate('getUnProcessedOrders')
    def getUnProcessedOrders(self):
        "get the unprocesssed orders"
        folder = self.unrestrictedTraverse(self.ordersLocation, None)
        temp = []
        if folder is not None:
            processedVarName = self.processedVar
            for cdoc in folder.objectValues('CompoundDoc'):
                processed = getattr(cdoc, processedVarName, None)
                #An order is valid if it is unprocessed, its profile has been set to a blank string (order was completed)
                #And it has a total that is non 0 ammount.
                if processed is not None and not processed.checked() and cdoc.profile == '' and cdoc.total():
                    temp.append(cdoc)
        return temp

    def isOrderProcessed(self,order):
        "has this order been processed?"
        return getattr(order, self.processedVar).checked()

    def isOrderComplete(self, order):
        "is this order complete?"
        return self.isOrderProcessed(order) and order.profile == '' and order.total()


    def markProcessedOrders(self,orders):
        "mark these orders as processed so they are not run again"
        processedVarName = self.processedVar
        for order in orders:
            getattr(order, processedVarName).setObject('data',1)

    def markOkayOrdersIds(self,orders):
        "mark these orders as okay/cleared so that we can do other stuff with them"
        processedOkayVar = self.processedOkayVar
        orderObjects = []
        orderFolder = self.unrestrictedTraverse(self.ordersLocation, None)
        for orderId in orders:
            order = getattr(orderFolder, orderId)
            orderObjects.append(order)
            getattr(order, processedOkayVar).setObject('data',1)
        return orderObjects

Globals.InitializeClass(CreditCardManager)
import register
register.registerClass(CreditCardManager)