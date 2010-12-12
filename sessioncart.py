# -*- coding: utf-8 -*-
import base
from AccessControl import getSecurityManager
import zExceptions

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from Products.ZCatalog.ZCatalog import ZCatalog
import DateTime
import utility
import bisect

import urllib
import cgi

from BTrees.OOBTree import OOBTree

class SessionCart(base.Base):
    "SessionCart provides a session based cart functionality to be used with an EComControl aware object"

    meta_type = "SessionCart"
    security = ClassSecurityInfo()
    overwrite=1
    annonymousEditAccepted = 1
    priceLocation = ''
    priceScriptPath = ''
    orderLocation = ''
    orderProfile = 'Default'
    orderOwnership = ''
    pathToUserFolder = ''
    preloadData = 0
    preload = None
    orderCatalog = ''
    freightEnabled = 1
    totalPriceEnabled = 1
    orderOkayAddScript = ''
    runInSecureMode = 1
    viewerRole = ''
    scriptOkayToPreload = ''
    preloadLocal = 0
    preloadLocalData = None
    
    classConfig = {}
    classConfig['orderOkayAddScript'] = {'name':'Script: is it okay to add an item to this order?', 'type':'path'}
    classConfig['runInSecureMode'] = {'name':'Use SSL for the checkout procedure?', 'type': 'radio'}
    classConfig['viewerRole'] = {'name':'What role (if any) should be assigned to the customer after the order is closed?', 'type':'string'}
    classConfig['scriptOkayToPreload'] = {'name':'Path to script to see if it so okay to preload data?', 'type':'path'}
    classConfig['priceScriptPath'] = {'name':'Path to the price script?', 'type':'path'}
    classConfig['preloadLocal'] = {'name':'Use local data instead of previous orders to preload data?', 'type': 'radio'}

    drawDict = base.Base.drawDict.copy()
    drawDict['maintenance'] = 'maintenance'
    drawDict['records'] = 'recordInformation'

    security.declareProtected('View management screens', 'maintenance')
    def maintenance(self, deleteAll=1, deleteCompleted=1, deleteUncompleted=1, addLocalData=1):
        "maintenance display"
        temp = []
        if deleteAll:
            temp.append('<p>%s orders where deleted</p>' % self.REQUEST.other.get('deletedAll', 0))
        if deleteCompleted:
            temp.append('<p>%s completed orders where deleted</p>' % self.REQUEST.other.get('deletedCompleted', 0))
        if deleteUncompleted:
            temp.append('<p>%s uncompleted orders where deleted</p>' % self.REQUEST.other.get('deletedUnCompleted', 0))
        if addLocalData:
            temp.append('<p>%s</p>' % self.create_button('addLocalData', 'Add Orders to local data', title='Add Orders to local data'))
        if deleteAll:
            temp.append('<p>Delete all orders older than: %s days</p>' % self.input_text('deleteAllDays','', containers=['maintenance']))
        if deleteCompleted:
            temp.append('<p>Delete all completed orders older than: %s days</p>' % self.input_text('deleteCompletedDays','', containers=['maintenance']))
        if deleteUncompleted:
            temp.append('<p>Delete all uncompleted orders older than: %s days</p>' % self.input_text('deleteUnCompletedDays','', containers=['maintenance']))
        return ''.join(temp)

    security.declareProtected('View management screens', 'recordInformation')
    def recordInformation(self):
        "maintenance display"
        temp = []
        temp.append('<p>%s</p>' % self.create_button('clearRecords', 'Clear Records'))
        temp.append(self.getMenu())
        name, value = self.getSelectedDocument()
        if name is not None and value is not None:
            temp.append('<p>%s</p>' % repr(name))
            temp.append('<p>%s</p>' % repr(value.items()))
        return ''.join(temp)

    security.declarePrivate('getMenu')
    def getMenu(self):
        "return the menu for these documents this is used in selectOne mode"
        temp = []
        selected = self.REQUEST.form.get('selectedDocument', None)
        if selected is not None:
            temp.append('<input type="hidden" name="selectedDocument:default" value="%s">' % selected)
        
        js = 'onchange="submit()"'
        seq = []
        if self.preloadLocalData:
            seq = list(self.preloadLocalData.keys())
        seq.insert(0, ('', 'Load Document') )
        temp.append(self.option_select(seq, 'selectedDocument', dataType='list:ignore_empty', events=js, selected=[selected]))
 
        temp.append(self.submitChanges('Load Record'))
        return ''.join(temp)


    security.declarePrivate('getSelectedDocument')
    def getSelectedDocument(self):
        "get the currently selected document"
        name = self.REQUEST.form.get('selectedDocument', None)
        if name is not None:
            try:
                return name, self.preloadLocalData[name]
            except (TypeError, KeyError):
                pass
        return None, None

    security.declarePrivate('processMaintenance')
    def processMaintenance(self, form):
        "process the maintenance"
        now = DateTime.DateTime()
        try:
            deleteAllDays = int(form.get('deleteAllDays', None))
        except ValueError:
            deleteAllDays = None
        if deleteAllDays is not None:
            self.REQUEST.other['deletedAll'] = self.deleteOrders(stop =now - deleteAllDays) or 0
            
        try:
            deleteCompletedDays = int(form.get('deleteCompletedDays', None))
        except ValueError:
            deleteCompletedDays = None
        if deleteCompletedDays is not None:
            self.REQUEST.other['deletedCompleted'] = self.deleteOrders(stop = now - deleteCompletedDays, completed=1) or 0
                        
        try:
            deleteUnCompletedDays = int(form.get('deleteUnCompletedDays', None))
        except ValueError:
            deleteUnCompletedDays = None
        if deleteUnCompletedDays is not None:
            self.REQUEST.other['deletedUnCompleted'] = self.deleteOrders(stop = now - deleteUnCompletedDays, completed=0) or 0
            

    security.declarePrivate('getPreload')
    def getPreload(self):
        "get the preload list structure"
        if self.preload is not None:
            return self.preload
        return []

    security.declarePrivate('okayToPreloadData')
    def okayToPreloadData(self, checkout):
        "check if it is okay to preload data"
        if self.scriptOkayToPreload:
            script = self.getCompoundDocContainer().restrictedTraverse(self.scriptOkayToPreload, None)
            if script is not None:
                return script(checkout)
        return True

    security.declareProtected('Delete objects', 'deleteOrders')
    def deleteOrders(self, start=None, stop=None, completed=None):
        "delete orders"
        container = self.getCompoundDocContainer()
        folder = container.restrictedTraverse(self.orderLocation, None)
        
        toDelete = 0
        if getSecurityManager().checkPermission('Delete objects', folder):
            orderIds = self.findOrderIdsBetween(start=start, stop=stop, completed=completed)
            toDelete = len(orderIds)
            folder.manage_delObjects(orderIds)
        return toDelete

    security.declareProtected('View management screens', 'findOrderIdsBetween')
    def findOrderIdsBetween(self, start=None, stop=None, completed=None):
        "find order ids that are between start and stop or have it open if either is None"
        container = self.getCompoundDocContainer()
        folder = container.restrictedTraverse(self.orderLocation, None)
        orderIds = list(cdocId for cdocId in folder.objectIds('CompoundDoc') if cdocId.startswith('order'))
        
        startIndex = None
        stopIndex = None
        
        if start is not None:
            start = utility.cleanRegisteredId('order'+str(start.timeTime()))
        
        if stop is not None:
            stop = utility.cleanRegisteredId('order'+str(stop.timeTime()))
        
        if start is not None:
            startIndex = bisect.bisect(orderIds, start)
            
        if stop is not None:
            stopIndex = bisect.bisect(orderIds, stop)
        orderIds = orderIds[startIndex:stopIndex]
        if completed is not None:
            orderIds = self.filterCompleted(folder, orderIds, completed)
        return orderIds

    security.declarePrivate('filterCompleted')
    def filterCompleted(self, folder, orderIds, completed):
        "filter these orderIds to find all the completed or not completed orders"
        orders = ((orderId, getattr(folder, orderId, None)) for orderId in orderIds)
        
        okProfile = self.orderProfile
        if completed:
            okProfile = ''
        
        temp = []
        for orderId, order in orders:
            if order.profile == okProfile:
                temp.append(orderId)
        return temp
        

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form):
        "process the cart actions and update the session data to the new information"
        if form.pop('clearRecords',  None) is not None:
            self.preloadLocalData = None
        
        selected = form.pop('selectedDocument',  None)
        if selected is not None:
            for i in selected:
                if i:
                    selected = i
                    break
            else:
                selected = ''
            self.setSelectedDocument(selected)
        
        preload = form.pop('preload',  None)
        if preload is not None:
            preload = preload.split()
            if not len(preload):
                preload = None
            self.setObject('preload', preload)
      
        if form.pop('addLocalData',  None) is not None:
            self.addAllOrderObjectsToLocalData()

        maintenance = form.pop('maintenance',  None)
        if maintenance is not None:
            self.processMaintenance(maintenance)

        actions = form.pop('cart_actions','')
        if actions == 'Clear Cart':
            self.clearCart()
        elif actions == "Update":
            self.updateCart(form)
        elif actions == "Remove Selected":
            self.removeSelectedFromCart(form)
        elif actions == 'Checkout':
            self.beginCheckoutProcess()

    security.declarePrivate('addAllOrderObjectsToLocalData')
    def addAllOrderObjectsToLocalData(self):
        "add all the order objects the current exist to the local data"
        container = self.getCompoundDocContainer()
        folder = container.restrictedTraverse(self.orderLocation, None)
        
        if self.preloadLocalData is None:
                self.preloadLocalData = OOBTree()
        localData = self.preloadLocalData
        
        for cdoc in utility.subTrans(reversed(folder.objectValues('CompoundDoc')), 100):
            if not cdoc.profile:
                username = cdoc.customerLogin(mode='view')
                if username not in localData:
                    self.createLocalDataStorage(cdoc,  username=username,  preloadLocal=1)
                self._p_deactivate()
                self._p_jar.cacheGC()

    security.declarePrivate('getSessionManager')
    def getSessionManager(self):
        "get the session data object"
        return self.SessionManagerConfig.getSessionManager()
            
    security.declarePrivate('getSession')
    def getSession(self):
        "get the session data object"
        return self.getSessionManager().getSessionData()
            
    security.declareProtected('Checkout Immediately', 'beginCheckoutProcess')
    def beginCheckoutProcess(self):
        "begin the checkout process"
        sessionData = self.getSession()
        username = getSecurityManager().getUser().getUserName()
        url = None
        if sessionData.has_key('checkoutObject'):
            url = sessionData['checkoutObject']
        elif not sessionData.has_key('checkoutObject') and username != 'Anonymous User':
            self.createCheckoutObject()
            url = sessionData['checkoutObject']
        elif username == 'Anonymous User':
            sessionData.set('needToLogin', 1)
            sessionData.set('redirectToAddingProduct', 1)
            url = self.getCompoundDocContainer().unrestrictedTraverse(self.pathToUserFolder).absolute_url()
        if url is not None:
            self.REQUEST.RESPONSE.redirect(url)

    security.declarePrivate('removeSelectedFromCart')
    def removeSelectedFromCart(self, form):
        "remove the selected items from the cart"
        if 'delete' in form:
            sessionData = self.getSession()
            orders = sessionData.get('orders', {})
            for formName in form['delete']:
                try:
                    path,args = formName.split(' /-\ ' )
                    if args:
                        args = tuple(sorted(cgi.parse_qsl(args)))
                    else:
                        args = None
                    del orders[(path, args)]
                    if self.freightEnabled:
                        self.FreightOrderListing.recalculateFreight()
                except KeyError:
                    pass
            sessionData.set('orders', orders)

    security.declarePublic('clearCart')
    def clearCart(self):
        "clear the shopping cart"
        sessionData = self.getSession()
        removalKeys = ('orders',  'needToLogin',  
            'redirectToAddingProduct',  'checkoutObject',  
            'freightList',  'freightCost',  'freightClass')
        
        for key in removalKeys:
            try:
                del sessionData[key]
            except KeyError:
                pass
        
    security.declarePrivate('updateCart')
    def updateCart(self, form):
        "update the shopping cart"
        modified = 0
        sessionData = self.getSession()
        orders = sessionData.get('orders', {})
        cartDict = self.parseForm(form)
        for key in orders.keys():  #need keys since we mutate the dict during iteration
            try:
                newValue = cartDict[key]
                if newValue < 0:
                    pass
                elif newValue and orders[key] != newValue:
                    orders[key] = newValue
                    modified = 1
                elif newValue == 0:
                    del orders[key]
                    modified = 1
            except KeyError:
                pass
        sessionData.set('orders', orders)
        if modified and self.freightEnabled:
            self.FreightOrderListing.recalculateFreight()

    security.declarePrivate('parseForm')
    def parseForm(self, form):
        "parse this form into a new dictionary and split out the shopping cart keys"
        temp = {}
        for key, value in form.iteritems():
            if ' /-\ ' in key:
                path,args = key.split(' /-\ ' )
                if args:
                    args = tuple(sorted(cgi.parse_qsl(args)))
                else:
                    args = None
                temp[(path, args)] = value
            else:
                temp[key] = value
        return temp

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "add the catalog, add the appropriate indexes to it, and cause it to reindex if we modify it"
        folder = self.getCompoundDocContainer().restrictedTraverse(self.orderLocation, None)
        if folder is not None and not hasattr(folder, self.orderCatalog):
            folder._setObject(self.orderCatalog, ZCatalog(self.orderCatalog))
            catalog = getattr(folder, self.orderCatalog)
            catalog.addIndex('customerLogin','FieldIndex')
            catalog.addIndex('id', 'FieldIndex')
            catalog.addIndex('bobobase_modification_time', 'FieldIndex')
            path = '/'.join(folder.getPhysicalPath())

            catalog.ZopeFindAndApply(folder, obj_metatypes=['CompoundDoc'],
                                                search_sub=1,
                                                apply_func=catalog.catalog_object,
                                                apply_path=path)
            self.addToCatalog(folder)
            transaction.get().commit()

            
    security.declarePrivate('addToCatalog')
    def addToCatalog(self,base):
        "reindex all the compoundocs at this base and then continue on"
        catalogName = self.orderCatalog  
        for doc in base.objectValues('CompoundDoc'):
            if doc.CatalogManager is None:
                doc.addRegisteredObject('CatalogManager', 'CatalogManager')
            doc.CatalogManager.append(catalogName)
        for folder in base.objectValues('Folder'):
            self.addToCatalog(folder)            
            
    security.declarePrivate('createCheckoutObject')
    def createCheckoutObject(self):
        "Create the checkout object for this cookie data"
        sessionData = self.getSession()
        username = getSecurityManager().getUser().getUserName()

        container = self.getCompoundDocContainer()
        folder = container.restrictedTraverse(self.orderLocation, None)
        checkout = folder.manage_addProduct['CompoundDoc'].manage_addCompoundDoc('', prepend="order", profile=self.orderProfile, redir=0, returnObject=1, autoType='timestamp')
        checkout.compoundChangeOwnership(username)
        
        if self.preloadData and self.okayToPreloadData(checkout):
            
            values = None
            if self.preloadLocal:
                values = self.loadDataFromLocal(username)
            else:
                values = self.loadDataFromOrders(container, username)
            
            if values:
                for name, i in values:
                    try:
                        getattr(checkout,name).dataLoader(i)
                    except AttributeError:
                        pass


        url = checkout.absolute_url()
        if url.startswith('https') or not self.runInSecureMode:
            sessionData['checkoutObject'] = url
        else:
            sessionData['checkoutObject'] = 'https' + url[4:]

    security.declarePrivate('loadDataFromLocal')
    def loadDataFromLocal(self, username):
        "load data from local"
        if self.preloadLocalData is not None:
            return self.preloadLocalData.get(username, {}).items()

    security.declarePrivate('loadDataFromOrders')
    def loadDataFromOrders(self, container, username):
        "load data from previous orders"
        lastOrder = self.getLastOrder(container, username)

        if lastOrder is not None:
            temp = []
            for name in self.getPreload():
                obj = getattr(lastOrder, name, None)
                if obj is not None:
                    try:
                        loader = obj.createDataLoader
                    except AttributeError:
                        loader = None
                    if loader is not None:
                        temp.append((name, loader()))
            return temp

    security.declarePrivate('getLastOrder')
    def getLastOrder(self, container, username):
        "get the last order from this user"
        folder = container.restrictedTraverse(self.orderLocation, None)
        catalog = getattr(folder, self.orderCatalog)
        oldOrders = catalog(customerLogin= username, sort_on='bobobase_modification_time', sort_order='descending')

        lastOrder = None
        for order in oldOrders:
            try:
                lastOrder = oldOrders[0].getObject()
                if lastOrder is not None:
                    break
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                pass
        return lastOrder

    security.declarePublic('handleCookieEvents')
    def handleCookieEvents(self):
        "handle the cookie events for this object by redirecting as needed"
        sessionData = self.getSession()
        username = getSecurityManager().getUser().getUserName()
        needToLogin = sessionData.get('needToLogin', 0)
        redirectToAddingProduct = sessionData.get('redirectToAddingProduct',0)

        url = None
        if needToLogin and username == 'Anonymous User':
            url = self.getCompoundDocContainer().unrestrictedTraverse(self.pathToUserFolder).absolute_url()
        elif username != 'Anonymous User' and redirectToAddingProduct and not sessionData.has_key('checkoutObject'):
            self.createCheckoutObject()
            url = sessionData['checkoutObject']
            del sessionData['needToLogin']
            del sessionData['redirectToAddingProduct']
        if url is not None:
            return url

    security.declareProtected('View', 'finishOrder')
    def finishOrder(self, sessionData=None, username=None):
        "finish the order on this object which involves changing the ownership and setting who the customer is"
        if username is None:
            username = getSecurityManager().getUser().getUserName()
        if sessionData is None:
            sessionData = self.getSession()
        url = sessionData['checkoutObject'].replace(self.REQUEST.BASE0+'/', '')
        order = self.getCompoundDocContainer().restrictedTraverse(url, None)
        #needed explicitely here since in this method we may have found the order not from the session data
        self.setOrder(order)
        if username in order.users_with_local_role('Owner'):
            order.customerLogin.data = username
            order.orderDate.data = DateTime.DateTime()

            self.recordOrderSelectionDetails(order)

            order.profile = ''
            if sessionData:
                self.storeFreightInfo(order, sessionData)
                self.storePriceInfo(order)
                self.clearCart()
            
            if order.CatalogManager is None:
                order.addRegisteredObject('CatalogManager', 'CatalogManager')
            order.CatalogManager.append(self.orderCatalog)
            order.index_object()

    security.declareProtected('View', 'isOrderOpenForAdditions')
    def isOrderOpenForAdditions(self, order):
        "return True or False depending on if the order has had the cookie destroyed and written to the order object"
        if order.orderRecorder.getListDict():
            return False
        return True
        

    security.declareProtected('View', 'closeOrder')
    def closeOrder(self, order):
        "close the security on this order"
        username = order.customerLogin(mode='view')
        order.manage_delLocalRoles([username])
        self.createLocalDataStorage(order, username)
        viewerRole = self.viewerRole
        if viewerRole:
            order.manage_addLocalRoles(username, [viewerRole])
        order.compoundChangeOwnership(self.orderOwnership)
    
    security.declarePrivate('createLocalDataStorage')
    def createLocalDataStorage(self, order, username=None,  preloadLocal=None):
        "create the local data storage information"
        username = username or order.customerLogin(mode='view')
        preloadLocal = preloadLocal or self.preloadLocal
        if preloadLocal:
            if self.preloadLocalData is None:
                self.preloadLocalData = OOBTree()
            values = [(name, getattr(order, name, None)) for name in self.getPreload()]
            values = [(name, i.createDataLoader()) for name,i in values if i is not None and hasattr(i, 'createDataLoader')]
            self.preloadLocalData[username] = dict(values)
    
    security.declarePrivate('addOrder')
    def addOrder(self,path, quantity=1, args=None):
        "add this order"
        sessionData = self.getSession()
        if not sessionData.has_key('orders'):
            sessionData.set('orders', {})
        
        if self.isOkayToAdd(sessionData['orders'],path, args):
            if args is not None:
                args = tuple(sorted(args.items()))
            data = sessionData.get('orders')
            data[(path, args)] = quantity
            sessionData.set('orders', data)
            if self.freightEnabled:
                self.FreightOrderListing.recalculateFreight()
                
    security.declarePrivate('isOkayToAdd')
    def isOkayToAdd(self,orderData, path, args=None):
        "is it okay to add this item?"
        scriptOkay = 1
        if self.orderOkayAddScript:
            script = self.getCompoundDoc().restrictedTraverse(self.orderOkayAddScript,None)
            if script is not None:
                try:
                    scriptOkay = script(orderData.copy(),path)
                except TypeError:
                    scriptOkay = script(orderData.copy(),path, args)
        if scriptOkay:
            if args is not None:
                args = tuple(sorted(args.items()))
            return not orderData.has_key((path, args))
    
    security.declareProtected('View', 'getOrderObjects')
    def getOrderObjects(self):
        "get the items in the order as objects"
        temp = []
        orderPaths = self.getSession().get('orders', {}).keys()
        if orderPaths:
            folder = self.getCompoundDocContainer()
            temp = [folder.restrictedTraverse(path, None) for path, args in orderPaths]
            temp = [i for i in temp if i is not None]
        return temp
                
                
    security.declarePrivate('removeOrder')
    def removeOrder(self,path, args=None):
        "remove this path from the order"
        manager = self.SessionManagerConfig.getSessionManager()
        if manager.hasSessionData():
            sessionData = manager.getSessionData()
            if not sessionData.has_key('orders'):
                sessionData.set('orders', {})
            if args is not None:
                args = tuple(sorted(args.items()))
            try:
                data = sessionData.get('orders')
                del data[(path, args)]
                sessionData.set('orders', data)
                if self.freightEnabled:
                    self.FreightOrderListing.recalculateFreight()
            except KeyError:
                pass
            
    security.declarePrivate('storePriceInfo')
    def storePriceInfo(self, order):
        "store the total and subtotal for this order"
        order.subTotal.data = self.getSubTotal()
        if self.totalPriceEnabled:
            order.total.data = self.getTotal()

    security.declarePrivate('storeFreightInfo')
    def storeFreightInfo(self, order, sessionData):
        "store the freight information for this order"
        if self.freightEnabled:
            order.freightClass.data = sessionData.get('freightClass', 'No Freight Set')
            order.freightCost.data = self.getFreightCost()

    security.declarePrivate('recordOrderSelectionDetails')
    def recordOrderSelectionDetails(self, order):
        "record the details of what the client ordered"
        records = self.createOrderDict()
        for record in records:
            order.orderRecorder.addDictObject(record)
        order.orderRecorder.orderHeaderPath = '/'.join(self.getPhysicalPath()) + '/orderRecorderSettings'

    security.declarePublic('orderRecorderSettings')
    def orderRecorderSettings(self, cdoc=None):
        "return the order recorder settings"
        return (('product', 'Product'), ('title', 'Title'), ('args', 'Customizations'), ('quantity', 'Quantity'), ('unitPrice', 'UnitPrice'), ('price', 'Price')) 

    security.declareProtected('Shopping Cart Info','createOrderDict')
    def createOrderDict(self):
        "create the nested order dict"
        storage = []
        orders = self.getSession().get('orders', {})
        if orders:
            for (product, args),quantity in orders.items():
                try:
                    object = self.unrestrictedTraverse(product)
                    unitPrice = self.getPrice(object, args)
                    price =  unitPrice * quantity
                    title = object.title_or_id()
                    if args is not None:
                        args = tuple(sorted(args.items()))
                    else:
                        args = ''
                    storage.append({'price': price, 'quantity':quantity, 'unitPrice':unitPrice, 'product':product, 'title':title, 'args':args})
                except KeyError:
                    pass
        return storage

    security.declareProtected('View', 'view')
    def view(self, formatScript=None):
        "Inline draw view"
        temp = []
        if self.hasOrders():
            temp.append('<form action="" method="post"><div>')
            temp.append("<p>%s item(s) in your shopping cart</p>" % self.numberOfItemsInShoppingCart())
            
            temp.append('<table>')

            headerFormat = '<tr><th>%(product)s</th><th>%(quantity)s</th><th>%(delete)s</th><th>%(price)s</th></tr>'
            lineFormat = '<tr><td>%(product)s</td><td>%(quantity)s</td><td>%(delete)s</td><td>$%(price)0.2f</td></tr>'

            lines = self.getOrderItems()
            header = {'product':'Product', 'quantity':'Quantity', 'delete':'Delete', 'price':'Price'}
            
            spanSize = 3
            if formatScript is not None:
                header, lines, headerFormat, lineFormat = formatScript(header=header, lines=lines, headerFormat=headerFormat, lineFormat=lineFormat)
                spanSize = len(header) - 1

            temp.append(headerFormat % header)
            for line in lines:
                temp.append(lineFormat % line)
            
            temp.append('<tr><td colspan="%s">SubTotal</td><td>$%0.2f</td></tr>' % (spanSize, self.getSubTotal()))
            if self.freightEnabled:
                temp.append('<tr><td colspan="%s">Shipping and Handling</td><td>$%0.2f</td></tr>' % (spanSize, self.getFreightCost()))
            if self.totalPriceEnabled:
                temp.append('<tr><td colspan="%s">Total</td><td>$%0.2f</td></tr>' % (spanSize, self.getTotal()))
            temp.append('</table>')
            buttons = ("Clear Cart", 'Update', 'Remove Selected', 'Checkout')
            temp.extend(self.create_buttons("cart_actions", buttons))
            if self.freightEnabled:
                temp.append('<div>%s</div>' % self.FreightOrderListing.view())
            temp.append('</div></form>')
        return ''.join(temp)

    security.declarePrivate('getOrderItems')
    def getOrderItems(self):
        "return a list of tuples for the items in the order which is used in view"
        output = []
        for (path, args),quantity in self.getSession().get('orders', {}).items():
            try:
                item = self.unrestrictedTraverse(path)
                price = self.getPrice(item, args) * quantity
                if args is not None:
                    formArgs = urllib.urlencode(args)
                else:
                    formArgs = ''
                formName = path + ' /-\ ' + formArgs
                output.append({'product':item.title_or_id(), 'quantity':self.input_number(formName, quantity),
                  'delete':self.check_box(formName, 1, ['delete',]), 'price':price, 'args':args, 'item':item, 'number':quantity})
            except KeyError:
                pass
        return output

    security.declareProtected('Access contents information', 'getQuantity')
    def getQuantity(self, path, args=None):
        "see how many items are for this order"
        manager = self.SessionManagerConfig.getSessionManager()
        if manager.hasSessionData():
            sessionData = manager.getSessionData()
            if not sessionData.has_key('orders'):
                sessionData.set('orders', {})
            if sessionData['orders'].has_key((path, args)):
                return sessionData['orders'][(path, args)]
        return 0

    security.declarePrivate('numberOfItemsInShoppingCart')
    def numberOfItemsInShoppingCart(self):
        "return the number of items in the shopping cart"
        return len(self.getSession().get('orders', {}))

    security.declarePublic('short')
    def short(self):
        "Inline short view"
        return '''<p>%s item(s) in your shopping cart</p><p>Current price is $%0.2f</p>
          <p><a href="%s">Go to shopping cart.</a></p>''' % (self.numberOfItemsInShoppingCart(),
          self.getSubTotal(), self.getCompoundDoc().absolute_url())

    security.declarePublic('hasOrders')
    def hasOrders(self):
        "return true if we have orders"
        return bool(self.getSession().get('orders', {}))

    security.declarePrivate('getOrder')
    def getOrder(self):
        "get the current order from the REQUEST and if we can't find one set go ahead and set one from the session data"
        order = self.REQUEST.other.get('currentOrder',None)
        if order is None:
            sessionData = self.getSession()
            if sessionData.has_key('checkoutObject'):
                url = sessionData['checkoutObject'].replace(self.REQUEST.BASE0+'/', '')
                order = self.getCompoundDocContainer().restrictedTraverse(url, None)
                self.setOrder(order)
        return order 
                
    security.declarePrivate('setOrder')
    def setOrder(self,order):
        "set the current order object in the REQUEST object"
        self.REQUEST.other['currentOrder'] = order
    
    security.declarePrivate('getPrice')
    def getPrice(self, product, args=None):
        "Return the sort value for this object and 0.0 if nothing else can be found"
        priceScriptPath = self.priceScriptPath
        if priceScriptPath:
            priceScript = self.getCompoundDocContainer().unrestrictedTraverse(priceScriptPath, None)
            if priceScript is not None:
                return priceScript(product,  self.getOrder(),  args)
            else:
                return 0.0
        else:
            price = product.unrestrictedTraverse(self.priceLocation, 0.0)
            if hasattr(price, 'float'):
                price = price.float()
            if callable(price):
                order = self.getOrder()
                try:
                    return price(order)
                except TypeError:
                    return price(order, args)
            return price

    security.declareProtected("Access contents information", 'getFreightCost')
    def getFreightCost(self):
        "return the current freight cost and 0.0 if there is none"
        try:
            return self.getSession().get('freightCost', 0.0)
        except (AttributeError,KeyError):
            return 0.0

    security.declareProtected("Access contents information", 'getSubTotal')
    def getSubTotal(self):
        "get the current sub total"
        subTotal = 0.0
        try:
            for (product, args),quantity in self.getSession()['orders'].items():
                price = self.getPrice(self.unrestrictedTraverse(product), args)
                subTotal += price * quantity
            return subTotal
        except (AttributeError,KeyError):
            return subTotal

    security.declareProtected("Access contents information", 'getTotal')
    def getTotal(self):
        "return the total for this order"
        return self.getFreightCost() + self.getSubTotal()

    security.declarePublic('count')
    def count(self):
        "return how many items we have in the cart"
        return len(self.getSession().get('orders', {}))

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        profileNames = utility.getStoredProfileNames()
        temp = []
        temp.append('<p>Price location:%s</p>' % self.input_text('priceLocation', self.priceLocation))
        temp.append(self.SessionManagerConfig.edit())
        temp.append(self.FreightOrderListing.edit())
        temp.append('<p>Order Location:%s</p>' % self.input_text('orderLocation', self.orderLocation))
        temp.append('<p>Order Profile:%s</p>' % self.option_select(profileNames, 'orderProfile', [self.orderProfile]))
        temp.append('<p>Order Ownership:%s</p>' % self.input_text('orderOwnership', self.orderOwnership))
        temp.append('<p>Path To User Folder:%s</p>' % self.input_text('pathToUserFolder', self.pathToUserFolder))
        temp.append('<p>Preload Data from a Customers Previous order?:%s</p>' % self.true_false('preloadData', self.preloadData,0))
        temp.append('<p>Preload Vars:%s</p>' % self.input_text('preload', ' '.join(self.getPreload())))
        temp.append('<p>Order Catalog Name:%s</p>' % self.input_text('orderCatalog', self.orderCatalog))
        temp.append('''<p>The Order Catalog will be auto created do not create anything else in the Order Location folder
          with the name you want this catalog to have.</p>''')
        temp.append("<p>Total Price Calculation MUST be enabled if you want to use a CreditCardManager on the orders.</p>")
        temp.append('<p>Enable Total Price Calculation:%s</p>' % self.true_false('totalPriceEnabled', self.totalPriceEnabled,0))
        temp.append('<p>Enable Freight:%s</p>' % self.true_false('freightEnabled', self.freightEnabled,0))
        temp.append(self.editSingleConfig('orderOkayAddScript'))
        temp.append(self.editSingleConfig('runInSecureMode'))
        temp.append(self.editSingleConfig('viewerRole'))
        
        return ''.join(temp)

    security.declarePrivate('instance')
    instance = (('SessionManagerConfig',('create', 'SessionManagerConfig')),
      ('FreightOrderListing',('create', 'FreightOrderListing')))

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

Globals.InitializeClass(SessionCart)
import register
register.registerClass(SessionCart)
