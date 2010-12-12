# -*- coding: utf-8 -*-
import base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

from baseevent import BaseEvent

class EventManager(base.Base):
    "EventManager manages all Events"

    meta_type = "EventManager"
    security = ClassSecurityInfo()
    overwrite=1

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append('<div class="outline">')
        for i in self.getAllEvents():
            temp.append(i.edit())
        temp.append("</div>")
        return ''.join(temp)

    security.declarePrivate("getAllEvents")
    def getAllEvents(self):
        "Return a list of all items that are a BaseEvent"
        return [object for object in self.objectValues() if utility.isinstance(object, BaseEvent)]

Globals.InitializeClass(EventManager)
import register
register.registerClass(EventManager)