# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from userobject import UserObject
from simplelist import SimpleList
import utility

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import smtplib

from Products.PythonScripts.standard import DTML

class ListMailer(UserObject):
    "ListMailer class"

    security = ClassSecurityInfo()
    meta_type = "ListMailer"

    listName = ''
    listFrom = ''
    subject = ''
    message = ''
    footer = ''
    header = ''
    server = 'localhost'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        format = '<p>%(name)s %(form)s</p>\n'
        list = [''] + [id for id,object in self.getCompoundDoc().objectItems() if utility.isinstance(object, SimpleList)]
        temp.append(format % {'name':'To', 'form':self.option_select(list, 'listName', [self.listName])})
        temp.append(format % {'name':'From', 'form':self.input_text('listFrom', self.listFrom)})
        temp.append(format % {'name':'Subject', 'form':self.input_text('subject', self.subject)})
        temp.append(format % {'name':'Header', 'form':self.text_area('header', self.header)})
        temp.append(format % {'name':'Message', 'form':self.text_area('message', self.message)})
        temp.append(format % {'name':'Footer', 'form':self.text_area('footer', self.footer)})
        temp.append(format % {'name':'Mail Server', 'form':self.input_text('server', self.server)})
        temp.append(self.create_button("sendMail", "Send All Messages"))
        return ''.join(temp)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        if 'sendMail' in form:
            self.sendAllMessages()

    security.declarePrivate('sendAllMessages')
    def sendAllMessages(self):
        "Send all the messages we have"
        listName = self.listName
        if listName:
            addresses = getattr(self.getCompoundDoc(), listName)
            message = '%s\r\n\r\n%s\r\n\r\n%s\r\n\r\n' % (self.header, self.message, self.footer)
            message = DTML(message)
            From = self.listFrom
            Subject = self.subject
            server = smtplib.SMTP(self.server)
            msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s")
            for address in addresses.getEntries():
                message = message(self, self.REQUEST, address=address)
                server.sendmail(From, address, msg % (From, address, Subject, message))
            server.quit()

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.fixFrom()

    security.declarePrivate('fixFrom')
    def fixFrom(self):
        "fix the from attribute"
        if 'from' in self.__dict__:
            self.listFrom = getattr(self, 'from')
            self.delObjects(['from'])            
    fixFrom = utility.upgradeLimit(fixFrom, 141)        
    
Globals.InitializeClass(ListMailer)
import register
register.registerClass(ListMailer)