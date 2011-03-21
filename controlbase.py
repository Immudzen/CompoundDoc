#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from base import Base
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class ControlBase(Base):
    "Base for all control items abstract"

    meta_type = "ControlBase"
    security = ClassSecurityInfo()

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return ""

    def index_html(self):
        "Default view of this object"
        return self.getCompoundDoc().ControlPanel.index_html()

    security.declarePrivate('getControlTitle')
    def getControlTitle(self):
        "Get the title of this control panel if possible"
        try:
            return self.control_title
        except AttributeError:
            return self.getId()

    def traverseContainer(self, queryDict = None):
        "used for the dynamic menu system"
        queryDict = queryDict or {}
        temp = []
        containers = sorted(self.objectItems())
        selected = self.getMenuSelected()
        for name,item in containers:
            try:
                if name == selected:
                    temp.append((item.absolute_url_path(), item.title_or_id(),1, '', queryDict, ''))
                    temp.append(item.traverseContainer(queryDict=queryDict))
                else:
                    temp.append((item.absolute_url_path(), item.title_or_id(),0, '', queryDict, ''))
            except AttributeError:
                pass
        return temp

Globals.InitializeClass(ControlBase)
