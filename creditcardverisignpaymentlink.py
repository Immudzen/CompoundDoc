# -*- coding: utf-8 -*-
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
import string
import copy

from AccessControl.SecurityManagement import newSecurityManager
import AccessControl.User

def filterNumber(char):
    return char in string.digits

class CreditCardVerisignPaymentLink(base.Base):
    "Verisign Real Time PaymentLink Processor"

    meta_type = "CreditCardVerisignPaymentLink"
    security = ClassSecurityInfo()

    userName = ''
    password = ''
    postURL = 'https://payflowlink.verisign.com/payflowlink.cfm'
    partner = 'VeriSign'
    orderCompleteScript = ''

    security.declarePrivate('instance')
    instance = (('VerisignSent',('create', 'DataRecorder')),('Accounting',('create', 'DataRecorder')),
      ('discountRate',('create', 'InputText')),('transactionFee',('create', 'InputText')),
      ('VerisignPOST',('create', 'DataRecorder')))

    classConfig = {}
    classConfig['userName'] = {'name':'User Name:', 'type':'string'} 
    classConfig['password'] = {'name':'Password:', 'type':'string'}
    classConfig['partner'] = {'name':'Partner:', 'type':'string'}
    classConfig['postURL'] = {'name':'POST URL:', 'type':'string'}
    classConfig['orderCompleteScript'] = {'name':'Location of the Order Completion Script:', 'type':'string'} 

    security.declarePrivate('configAddition')
    def configAddition(self):
        "Inline edit view"
        temp = []
        temp.append('<p>Using Verisign PaymentLink credit card processor</p>')
        temp.append('<p>Discount Rate: %s</p>' % self.discountRate.edit())
        temp.append('<p>Transaction Fee: %s</p>' % self.transactionFee.edit())
        return ''.join(temp)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "edit view"
        temp = []
        temp.append('<p>Record of what Verisign returned in the silent post.</p>')
        temp.append(self.VerisignPOST.edit())
        temp.append(self.VerisignPOST.CSVDataFilter.view())
        temp.append('<p>Accounting Information</p>')
        temp.append(self.Accounting.edit())
        temp.append(self.Accounting.CSVDataFilter.view())
        temp.append('<p>Record of what we sent to Verisign.</p>')
        temp.append(self.VerisignSent.edit())
        temp.append(self.VerisignSent.CSVDataFilter.view())
        return ''.join(temp)

    def doAccountingInfo(self,order):
        "Do the basic accounting info needed and store that in a DataRecorder"
        date = self.ZopeTime().aCommon()
        total = order.total.float()
        discountRate = float(self.discountRate())
        transactionFee = float(self.transactionFee())
        totalMinusDiscountRate = total - (discountRate*total)
        totalTransactionFee = transactionFee
        depositTotal = totalMinusDiscountRate - totalTransactionFee
        record = {}
        record['CurrentDate'] = date
        record['discountRate'] = '%.4f' % discountRate
        record['transactionFee'] = '%.2f' % transactionFee
        record['totalMinusDiscountRate'] = '%.2f' % totalMinusDiscountRate
        record['depositTotal'] = '%.2f' % depositTotal
        record['totalTransactionFee'] = totalTransactionFee
        record['total'] = '%.2f' % total
        self.Accounting.addDictObject(record)

    security.declarePublic('processPOST')
    def processPOST(self):
        "process the results of the silent post back from verisign"
        form = self.REQUEST.form
        self.VerisignPOST.addDictObject(copy.copy(form))
        RESULT = form.get('RESULT', '')
        RESPMSG = form.get('RESPMSG', '')
        orderId = form.get('USER1', '')
        orderOwner = form.get('USER2', '')
        AMOUNT = form.get('AMOUNT', '')
        order = self.getOrder(orderId)
        
        self.storeData(order, 'result', RESULT)
        self.storeData(order, 'respmsg', RESPMSG)
        
        AUTHCODE = form.get('AUTHCODE', '')
        self.storeData(order, 'authcode', AUTHCODE)

        AVSDATA = form.get('AVSDATA', '')
        self.storeData(order, 'avsdata', AVSDATA)

        PNREF = form.get('PNREF', '')
        self.storeData(order, 'pnref', PNREF)

        TYPE = form.get('TYPE', '')
        self.storeData(order, 'transactionType', TYPE)
        
        CSCMATCH = form.get('CSCMATCH', '')
        self.storeData(order, 'cscmatch', CSCMATCH) 
               
        if self.responseIsOkay(RESULT, RESPMSG) and order is not None and self.isOrderOkay(order, AMOUNT, orderOwner):
            NAME = form.get('NAME', '')
            if NAME:
                order.billName.setObject('data', NAME)

            ADDRESS = form.get('ADDRESS', '')
            if ADDRESS:
                order.billStreet.setObject('data', ADDRESS)

            CITY = form.get('CITY', '')
            if CITY:
                order.billCity.setObject('data', CITY)

            STATE = form.get('STATE', '')
            if STATE:
                order.billState.setObject('data', STATE)

            ZIP = form.get('ZIP', '')
            if ZIP:
                order.billZip.setObject('data', ZIP)

            PHONE = form.get('PHONE', '')
            if PHONE:
                order.billPhone.setObject('data', PHONE)

            self.markOkayOrdersIds([orderId])
            self.doAccountingInfo(order)
            if self.orderCompleteScript:
                #user = self.getUser(orderOwner)
                #FIXME use less privelage
                newSecurityManager(None, AccessControl.User.system)
                order.unrestrictedTraverse(self.orderCompleteScript)()
            self.getShoppingCart().closeOrder(order)
            return ' '

    def storeData(self, container, name, data):
        "store data we got back from verisign"
        container.updateRegisteredObject(name, 'InputText')
        getattr(container, name).setObject('data', data)
                
    def cleanSecureData(self, record):
        "block out data that should be secure so it is not stored"
        temp = record.copy()
        if 'CARDNUM' in temp:
            temp['CARDNUM'] = 11* 'x' + temp['CARDNUM'][-5:]
        return temp

    def getOrder(self, orderId):
        "return the order object if it seems okay to do so"
        orderFolder = self.unrestrictedTraverse(self.ordersLocation, None)
        if orderFolder is not None:
            return getattr(orderFolder, orderId,None)

    def isOrderOkay(self, order, amount, orderOwner):
        "is this order okay to process?"
        cameFromVerisign = 1 #Need to figure this out
        sameTotal = '%.2f' % order.total.float() == amount
        sameOwner =  order.customerLogin.view() == orderOwner
        processed = self.isOrderProcessed(order)
        if cameFromVerisign and processed and sameTotal and sameOwner:
            return True
        else:
            return False


    def responseIsOkay(self, result, respmsg):
        "check the result and response and see if this response from verisign is ok"
        if respmsg not in ('AVSDECLINED', 'CSCDECLINED') and result == '0':
            return True
        else:
            return False

    security.declareProtected('CompoundDoc: Credit Card Processing', 'submitCard')
    def submitCard(self, order=None, additionalData=None, transaction='S'):
        "submit the card to verisign"
        if not order:
            return None
        #Close out the order so we can do all of this processing
        cart = self.getShoppingCart()
        if cart.isOrderOpenForAdditions(order):
            cart.finishOrder()
                
        userName = self.userName
        orderOwner = order.customerLogin.view()
        city = order.billCity.view()[0:32] #32 Character Max Accepted
        total = '%.2f' % order.total.float()
        zipCode = filter(filterNumber, order.billZip.view()) #Can only contain numbers
        address = order.billStreet.view()[0:60] #Must be 20 chars or less so slice it at 20
        orderId = order.getId()[0:31]
        state = order.billState.view()[0:20]
        country = order.billCountry.view()[0:32]
        phone = order.billPhone.view()[0:20]
        name = order.billName.view()[0:60]
        #Some basic sanity checks
        if total and zipCode and address and transaction in ('S', 'A'):
            post = {}
            post['TYPE'] = transaction
            post['AMOUNT'] = total
            post['PARTNER'] = self.partner
            post['LOGIN'] = userName
            post['METHOD'] = 'CC'
            post['USER1'] = orderId
            post['USER2'] = orderOwner
            post['NAME'] = name
            post['ADDRESS'] = address
            post['CITY'] = city
            post['STATE'] = state
            post['ZIP'] = zipCode
            post['COUNTRY'] = country
            post['PHONE'] = phone
            #email
            
            if additionalData is not None:
                for key,value in additionalData.iteritems():
                    if key not in post:
                        post[key] = value
            
            self.markProcessedOrders([order])
            record = self.cleanSecureData(post)
            self.VerisignSent.addDictObject(record)
         
            return self.createPOSTForm(post)

    security.declarePrivate('createPOSTForm')
    def createPOSTForm(self, data):
        "create the form for the POST to verisign"
        inputHidden = '<input type="hidden" name="%s" value="%s">'
        temp = []
        temp.append('<form action="%s" method="post"><div>' % self.postURL)
        for key,value in data.iteritems():
            temp.append(inputHidden % (key, value))
        temp.append(self.submitChanges("Submit Data to Verisign for Credit Card Authentication"))
        temp.append('</div></form>')
        temp = ''.join(temp)
        return temp
        
Globals.InitializeClass(CreditCardVerisignPaymentLink)
import register
register.registerClass(CreditCardVerisignPaymentLink)