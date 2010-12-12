###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
import base
import validators
import utility

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class TableEcom(base.Base):
    "TableEcom hooks up an object for ecommerece addition/subtraction"

    meta_type = "TableEcom"
    security = ClassSecurityInfo()
    increments = None
    percentDrop = None

    drawDict = base.Base.drawDict.copy()
    drawDict['calc'] = 'calc'
    
    def initObjects(f):
        def wrap(self, *args, **kw ):
            if self.increments is None:
                self.increments = []
                self._p_changed = 1
            if self.percentDrop is None:
                self.percentDrop = []
                self._p_changed = 1 
            return f(self, *args, **kw)
        return wrap

    security.declareProtected('View', 'view')
    def view(self, price, ecom, func=None, customHeader=None):
        "draw the buyable price table using this base price and this ecom object"
        #first entry is the sections, can use that to calculate ranges
        #for a,b in zip(a, a[1:]+[None]):
        #    print a,b
        header, prices = self.getRowsView(price,ecom, func)
        if customHeader is not None:
            header = customHeader(header, self, self.getCompoundDoc())
        return self.createTable([header, prices])

    security.declarePrivate('after_manage_edit')
    def before_manage_edit(self, form):
        "process the edits"
        self.processRowFromForm(form, 'inc', 'increments', validators.checkInt)
        self.processRowFromForm(form, 'percent', 'percentDrop', validators.checkFloat)

        if form.pop('addCol', None):
            self.increments.append(None)
            self.percentDrop.append(None)
            self._p_changed = 1
    before_manage_edit = initObjects(before_manage_edit)

    def processRowFromForm(self, form, rowName, storageName, valid):
        "process a row from the form"
        row = form.pop(rowName, None)
        if row is not None:
            tempDict = {}
            for i, j in row.items():
                tempDict[int(i)] = j
            rows = [valid(value) for index,value in sorted(tempDict.iteritems())]

            if len(rows):
                self.setObject(storageName, rows)
            else:
                self.delObjects((storageName, ))

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append('<p>%s</p>' % self.create_button('addCol', 'Add A New Column'))
        temp.append(self.createTable(self.getRows()))
        return ''.join(temp)

    security.declareProtected('View management screens', 'calc')
    def calc(self, price):
        "draw the calc view of this object"
        return self.createTable(self.drawCalc(price))

    security.declarePrivate('getRows')
    def getRows(self):
        "get the rows with this editing mode where applicable"
        return [['Quantity'] + self.editRow(self.increments, 'inc'),
            ['Percent Drop'] + self.editRow(self.percentDrop, 'percent')]
    getRows = initObjects(getRows)

    security.declarePrivate('drawCalc')
    def drawCalc(self, basePrice):
        return [['Quantity'] + self.increments,
                ['Percent Drop'] + self.percentDrop,
            ['Price'] + self.calcRow(self.percentDrop, basePrice)]
        
    def getRowsView(self, price, ecom, func=None):
        "return a sequence of rows for buying from this item"
        return self.calcRowBuy(self.percentDrop, self.increments, price, ecom, func)
        
    security.declarePrivate('editRow')
    def editRow(self, seq, rowName):
        clean = utility.renderNoneAsString
        return [self.input_text(str(index), clean(value), containers = (rowName,)) for index,value in enumerate(seq)]

    def getPrice(self, basePrice, ecom, args=None):
        "get the current price for this object based on quantity"
        cart = ecom.getShoppingCart()
        if cart is not None:
            path = ecom.getCompoundDoc().getPath()
            quantity = cart.getQuantity(path, args)
            for inc, percent in zip(self.increments, self.percentDrop)[::-1]:
                if inc is not None and percent is not None and inc <= quantity and percent < 100:
                    return float('%.2f' % ((basePrice*(100-percent))/100))
        return 0.0

    security.declarePrivate('calcRow')
    def calcRow(self, seq, basePrice):
        temp = []
        for item in seq:
            if item is None:
                temp.append('Bad Data')
            else:
                currentPrice = (basePrice*(100-item))/100
                if currentPrice <= 0:
                    temp.append('A price can not go below 0')
                else:
                    temp.append('%.2f' % currentPrice)
        return temp

    security.declarePrivate('calcRow')
    def calcRowBuy(self, seq, quantity, basePrice, ecom, func=None):
        prices = []
        quantities = []
        format = '<a href="%s/add?quantity=%s">%s</a>'
        ecomUrl = ecom.absolute_url()
        for percent,number in zip(seq,quantity):
            if percent is not None and number is not None:
                currentPrice = (basePrice*(100-percent))/100
                if currentPrice > 0:
                    stringPrice = '%.2f' % currentPrice
                    prices.append(format % (ecomUrl, number, stringPrice))
                    quantities.append(number)
        return [quantities, prices]

    security.declarePrivate('instance')
    instance = (('SessionManagerConfig', ('create', 'SessionManagerConfig')),)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

Globals.InitializeClass(TableEcom)
import register
register.registerClass(TableEcom)