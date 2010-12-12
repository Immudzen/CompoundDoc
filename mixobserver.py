# -*- coding: utf-8 -*-
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class MixObserver:
    "this is a mixin class to give objects observer capability"

    meta_type = "MixObserver"
    security = ClassSecurityInfo()

    security.declarePrivate('observerAttached')
    def observerAttached(self, item):
        "Process an attach event"
        path = item.getRelativePath(self)
        if not 'observing' in self.__dict__:
            self.observing = []
        if path not in self.observing:
            self.observing.append(path)
            self._p_changed = 1

    security.declarePrivate('observerDetached')
    def observerDetached(self, item):
        "Process a detach event"
        if 'observing' in self.__dict__ and item.getRelativePath(self) in self.observing:
            self.observing.remove(item.getRelativePath(self))

    security.declarePrivate('observerNotify')
    def observerNotify(self):
        "Notify all observers that I have changed"
        if 'observing' in self.__dict__:
            cdoc = self.getCompoundDoc()
            bad = []
            for i in self.observing:
                item = cdoc.unrestrictedTraverse(i, None)
                if item is not None:
                    item.observerUpdate(self)
                else:
                    bad.append(i)
            if bad:
                self.observing = [i for i in self.observing if i not in bad]

    security.declarePrivate('observerUpdate')
    def observerUpdate(self, item):
        "Process what you were observing"
        return None

    security.declarePrivate('getWatchingMe')
    def getWatchingMe(self):
        "Return a list of all objects that are watching me"
        if 'observing' in self.__dict__:
            cdoc = self.getCompoundDoc()
            observingItems = [cdoc.restrictedTraverse(i, None) for i in self.observing]
            return [i for i in observingItems if i is not None]
        return []

Globals.InitializeClass(MixObserver)
