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
import urllib2_file
import urllib2
import time
import StringIO
import urllib
import httplib
import itertools

def filterNumber(char):
    return char in string.digits

class CreditCardECHO(base.Base):
    "ECHO batch credit card processing class"

    meta_type = "CreditCardECHO"
    security = ClassSecurityInfo()

    userName = ''
    password = ''

    security.declarePrivate('instance')
    instance = (('ECHOSubmit',('create', 'ObjectRecorder')),('ECHOResponse',('create', 'ObjectRecorder')),
      ('ECHOBadOrder',('create', 'ObjectRecorder')),('BatchAmount',('create', 'DataRecorder')),
      ('discountRate',('create', 'InputText')),('transactionFee',('create', 'InputText')))

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    classConfig = {}
    classConfig['userName'] = {'name':'User Name:', 'type':'string'} 
    classConfig['password'] = {'name':'Password:', 'type':'string'}
    
    security.declarePrivate('configAddition')
    def configAddition(self):
        "Inline edit view"
        temp = []
        temp.append('<p>Using ECHO credit card processor</p>')
        temp.append('<p>Discount Rate: %s</p>' % self.discountRate.edit())
        temp.append('<p>Transaction Fee: %s</p>' % self.transactionFee.edit())
        return ''.join(temp)

    def edit(self, *args, **kw):
        "edit view"
        temp = ['<p>']
        temp.extend(self.create_buttons('runECHO', ('Send', 'Process')))
        temp.append('</p>')
        temp.append('<p>Record of what ECHO responsed to our submission with.</p>')
        temp.append(self.ECHOSubmit())
        temp.append('<p>Record of what ECHO processed to our submission with.</p>')
        temp.append(self.ECHOResponse())
        temp.append('<p>Orders that ECHO thinks are bad.</p>')
        temp.append(self.ECHOBadOrder())
        temp.append('<p>Accouning Information</p>')
        temp.append(self.BatchAmount())
        return ''.join(temp)

    def after_manage_edit(self,dict):
        'run the manual card processing stuff'
        lookup = {'Send':self.processCards, 'Process':self.getCardResults}
        if 'runECHO' in dict:
            run = dict['runECHO']
            if run in lookup:
                lookup[run]()

    def processCards(self):
        "process the cards"
        result = self.submitCards()
        if result is not None:
            self.ECHOSubmit.setObject('recordType', 'File')
            self.ECHOSubmit.addRecord(result)

    def getCardResults(self):
        "get the results of the card processing"
        marks = []
        for position,result in self.getUnProcessedResults():
            if self.validECHOTransaction(result):
                response = self.submitResult(result)
                self.ECHOResponse.setObject('recordType', 'File')
                self.ECHOResponse.addRecord(response)
                marks.append(position)
        self.markECHOSubmitItemsProcessed(marks)
        self.processCardResponses()

    def processCardResponses(self):
        "process the card responses and mark them as processed"
        marks = []
        for position,response in self.getUnProcessedResponses():
            if self.validEchoResponse(response):
                goodOrders,badOrders = self.processResponse(response)
                orders = self.markOkayOrdersIds(goodOrders)
                self.doAccountingInfo(orders)
                if badOrders:
                    self.saveBadOrders(badOrders)
            marks.append(position)
        self.markECHOResponseItemsProcessed(marks)

    def doAccountingInfo(self,orders):
        "Do the basic accounting info needed and store that in a DataRecorder"
        date = self.ZopeTime().aCommon()
        cards = len(orders)
        total = sum([order.total.float() for order in orders])
        discountRate = float(self.discountRate())
        transactionFee = float(self.transactionFee())
        totalMinusDiscountRate = total - (discountRate*total)
        totalTransactionFee = (cards*transactionFee)
        depositTotal = totalMinusDiscountRate - totalTransactionFee
        record = {}
        record['CurrentDate'] = date
        record['NumCards'] = cards
        record['discountRate'] = '%.4f' % discountRate
        record['transactionFee'] = '%.2f' % transactionFee
        record['totalMinusDiscountRate'] = '%.2f' % totalMinusDiscountRate
        record['depositTotal'] = '%.2f' % depositTotal
        record['totalTransactionFee'] = totalTransactionFee
        record['total'] = '%.2f' % total
        self.BatchAmount.addDictObject(record)

    def saveBadOrders(self, badOrders):
        "Save the bad orders just in case"
        temp = '\r\n'.join([','.join(line) for line in badOrders])
        self.ECHOBadOrder.setObject('recordType', 'File')
        self.ECHOBadOrder.addRecord(temp)

    def processResponse(self,response):
        "process the response into a set of good and bad orders"
        format = "order%s"
        goodOrderNames = []
        parsedRows = self.CSVParse(response) #Python 2.3 replace me also the first line is the header info
        badOrderNames = []
        for row in parsedRows[1:]:
            status = row[8]
            avsstatus = row[10]
            trace = row[13]
            name = format % trace
            if status == 'G':
                goodOrderNames.append(name)
            else:
                badOrderNames.append(row)
        if badOrderNames:
            badOrderNames.insert(0,parsedRows[0])
        return goodOrderNames,badOrderNames

    def CSVParse(self,result):
        'break up this string into a list of lists'
        temp = []
        for line in result.split('\r\n'): #windows formatted
            if line:
                temp.append(line.split(','))
        return temp

    def markECHOSubmitItemsProcessed(self, marks):
        "mark the items in ECHOSubmit as processed we do this after we get our card results back"
        self.markProcessed(marks, self.ECHOSubmit.getRecordObject())

    def markECHOResponseItemsProcessed(self, marks):
        "mark the items in ECHOResponse as processed we do this after we get our card results back"
        self.markProcessed(marks, self.ECHOResponse.getRecordObject())

    def markProcessed(self, marks, tree):
        "marks the items in this tree as processed"
        for mark in marks:
            record = tree[int(mark)]
            record['processed'] = 1
            tree[int(mark)] = record

    def getUnProcessedResults(self):
        "get the results from the ECHOSubmit object that have not been processed yet"
        return self.getUnProcessed(self.ECHOSubmit.getRecordObject())

    def getUnProcessedResponses(self):
        "get the responses from the ECHOResponse object that have not been processed yet"
        return self.getUnProcessed(self.ECHOResponse.getRecordObject())

    def getUnProcessed(self, btree):
        "get all the unprocessed items from this tree"
        temp = []
        for position,entry in btree.items():
            if entry['processed'] == 0:
                temp.append((position,entry['record'].data.data))
        return temp

    def submitResult(self,result):
        "submit the result of submitting the cards to echo to find out what happened to each one"
        batchId = result.split('\r\n')[1].split(',')[3]
        userName = self.userName
        password = self.password
        data = [ ('echo_id', userName),
          ('merchant_pin',password),
          ('batchId',batchId)]
        data = urllib.urlencode(data)
        return urllib2.urlopen('https://wwws.echo-inc.com/ECHOnlineBatch/download.asp',data).read()

    def submitCards(self):
        "submit the cards to echo"
        orders = self.getUnProcessedOrders()
        if not orders:
            return None
        temp = []

        self.setDrawMode('view')
        userName = self.userName
        transactionCode = 'EV'
        authCode = ''
        productDesc = ''
        merchantOrderNumber = ''
        purchaseOrderNumber = ''
        salesTax = ''
        securityCodePresence = 0
        securityCode = ''
        recurring = 'N'

        for order in orders:
            creditCardNumber = filter(filterNumber, order.creditCardNumber()) #Can only contain numbers
            creditCardExpire = filter(filterNumber, '%s%s' % (order.creditCardMonth(), order.creditCardYear()[2:])) #format MMYY
            #total = int(order.total.float()*100) #Must be an int 2 decimal places are assumed so multiply the float by 100
            total = ('%.2f' % order.total.float()).replace('.', '')
            zipCode = filter(filterNumber, order.billZip()) #Can only contain numbers
            address = order.billStreet().replace(',', ' ')[0:20] #Must be 20 chars or less so slice it at 20
            #if address.find(',') != -1: #Quote the field if it has a comma in it
            #  address = '"%s"' % address
            merchantTraceCode = order.getId()[5:] #Remove the order part to make sure the number always fits

            #Some basic sanity checks
            if total and creditCardNumber and zipCode and address and len(creditCardExpire) == 4 and creditCardExpire:
                record = [userName, transactionCode, creditCardNumber, creditCardExpire,total,authCode,zipCode,
                  address,merchantTraceCode,productDesc,merchantOrderNumber,purchaseOrderNumber,salesTax,
                  securityCodePresence,securityCode,recurring]
                temp.append(','.join(itertools.imap(str,record)))
        if temp:
            batch = '\r\n'.join(temp)
            batch = StringIO.StringIO(batch)
            batch.name = '%s.csv' % repr(time.time()).replace('.', '_')
            data = [ ('echo_id', userName),
              ('merchant_pin',self.password),
              ('allow_duplicates','n'),
              ('batch_file',batch)]
            req = urllib2.Request('https://wwws.echo-inc.com/echonlinebatch/upload.asp', data)
            result = urllib2.urlopen(req).read()
            if self.validEchoSubmission(result):
                self.markProcessedOrders(orders)
            return result

    def validEchoSubmission(self,result):
        "check if this is a valid echo result for a submission so we can mark the orders as processed"
        #This is the first line that is sent for a valid transmission so lets check for that
        return result.startswith('Filename,Records,Bytes,BatchId,TraceFile')

    def validEchoResponse(self,response):
        "check if this is a valid echo result for a submission so we can mark the orders as processed"
        #This is the first line that is sent for a valid transmission so lets check for that
        return response.startswith('ID,Date,Time,TC,ECHO-ID,PAN,ExpDt,Amount,Status,AuthOrErr,AvsStatus,OrderNumber,Line,TraceCode')

    def validECHOTransaction(self,result):
        "check that we have a valid transaction to query echo for to get the results of the first submission"
        #This is the first line that is sent for a valid transmission so lets check for that
        return result.startswith('Filename,Records,Bytes,BatchId,TraceFile')

Globals.InitializeClass(CreditCardECHO)
import register
register.registerClass(CreditCardECHO)