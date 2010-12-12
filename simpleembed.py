#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from userobject import UserObject
import mixremoteembed
from Acquisition import aq_base

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class SimpleEmbed(UserObject, mixremoteembed.MixRemoteEmbed):
    "Base for all objects that embed remote objects"

    meta_type = "SimpleEmbed"
    security = ClassSecurityInfo()
    overwrite=1
    path = ''

    security.declareProtected('View', 'embedded')
    def embedded(self):
        "return the object"
        item = getattr(self,'embed',None)
        if item is not None:
            return item
        if not self.path:
            return None
        item = self.restrictedTraverse(self.path, None)
        if item is not None:
            self.setObject('embed', aq_base(item))
            return item

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        self.setDrawMode('edit')
        item = self.embedded()
        if item is not None and getattr(item, 'meta_type', None) == 'CompoundDoc':
            return item.__of__(self).gen_html(item.render(mode='edit', name=self.editDisplayName))
        else:
            return ''

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        self.setDrawMode('view')
        item = self.embedded()
        if item is not None and getattr(item, 'meta_type', None) == 'CompoundDoc':
            return item.__of__(self).gen_html(item.render(mode='view', name=self.viewDisplayName))
        else:
            return ''

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.removeDTMLAttributes()

    security.declarePrivate('removeDTMLAttributes')
    def removeDTMLAttributes(self):
        "remove the DTML attributes"
        self.delObjects(['editDTML','viewDTML'])    
    removeDTMLAttributes = utility.upgradeLimit(removeDTMLAttributes, 141)
        
    security.declarePrivate('performUpgrade')
    def performUpgrade(self):
        "perform the upgrade on this object but do no descend to the children"
        self.upgrader()
        
Globals.InitializeClass(SimpleEmbed)
import register
register.registerClass(SimpleEmbed)