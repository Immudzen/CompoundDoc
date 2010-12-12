# -*- coding: utf-8 -*-
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import validators

import utility

class EComControl(base.Base):
    "EComControl hooks up an object for ecommerece addition/subtraction"

    meta_type = "EComControl"
    security = ClassSecurityInfo()
    overwrite=1
    data = '<a href="%(add)s">Add</a>/<a href="%(remove)s">Remove</a>'
    pathToShoppingCart = 'shoppingCart/cart'
    SessionManagerConfig = None

    configurable = ('data', 'pathToShoppingCart')

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        url = self.absolute_url()
        return self.getConfig('data') % {'add':url+'/add', 'remove':url+'/remove'}

    security.declarePublic('remove')
    def remove(self, redirect=1, args=None, url=None):
        "if we have this cdoc in the sessionmanager remove it"
        path = self.getCompoundDoc().getPath()
        self.getShoppingCart().removeOrder(path, args)
        if redirect:
            return self.redirectBackToPage(url)

    security.declarePrivate('redirectBackToPage')
    def redirectBackToPage(self, url=None):
        "redirect back to the referring page and if we don't have one redirect back to the closest compounddoc"
        url = url or self.REQUEST.get('HTTP_REFERER', None)
        if url is None:
            url = self.getCompoundDoc().absolute_url()
        return  self.REQUEST.RESPONSE.redirect(url)

    security.declarePublic('add')
    def add(self, redirect=1, quantity=1, args=None, url=None):
        "if we don't have this cdoc in the sessionmanager add it and set it to 1"
        quantity = validators.checkInt(quantity)
        if quantity is None:
            quantity = 1
        path = self.getCompoundDoc().getPath()
        self.getShoppingCart().addOrder(path, quantity, args)
        if redirect:
            return self.redirectBackToPage(url)

    security.declarePrivate('getShoppingCart')
    def getShoppingCart(self):
        "return the shopping cart object"
        return self.restrictedTraverse(self.getConfig('pathToShoppingCart'))

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = [self.input_text('data', self.data)]
        temp.append('<p>Where is the shopping cart located? %s</p>' % self.input_text('pathToShoppingCart', self.pathToShoppingCart))
        return ''.join(temp)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeSessionManagerConfig()

    security.declarePrivate('removeSessionManagerConfig')
    def removeSessionManagerConfig(self):
        "remove SessionManagerConfig"
        self.delObjects(['SessionManagerConfig'])
    removeSessionManagerConfig = utility.upgradeLimit(removeSessionManagerConfig, 156)


Globals.InitializeClass(EComControl)
import register
register.registerClass(EComControl)