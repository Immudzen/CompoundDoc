"Import basic functions"
import base
import nestedlisturl as NestedListURL

from controldisplaymanager import ControlDisplayManager
from controlcatalogmanager import ControlCatalogManager
from controlprofilemanager import ControlProfileManager
from controlmodemanager import ControlModeManager
from controllicense import ControlLicense
from controlrequest import ControlRequest
from controleventmanager import ControlEventManager
from controltabmanager import ControlTabManager
from controladddel import ControlAddDel
from controlshared import ControlShared
from controlsecuritymanager import ControlSecurityManager
from controllinkmanager import ControlLinkManager
from controlcallablerender import ControlCallableRender
from controldefaultmanager import ControlDefaultManager
from controlconverter import ControlConverter

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

import os.path

import utility

class ControlPanel(base.Base):
    "This is the control panel class"

    meta_type = "ControlPanel"
    security = ClassSecurityInfo()

    controlNames = ('ControlDisplayManager', 'ControlCatalogManager', 'ControlProfileManager',
      'ControlLicense', 'ControlRequest', 'ControlEventManager', 'ControlTabManager', 'ControlAddDel',
      'ControlShared', "ControlSecurityManager", 'ControlLinkManager',
      'ControlCallableRender', 'ControlDefaultManager', 'ControlModeManager', 'ControlConverter')

    ControlDisplayManager = ControlDisplayManager('ControlDisplayManager')
    ControlCatalogManager = ControlCatalogManager('ControlCatalogManager')
    ControlProfileManager = ControlProfileManager('ControlProfileManager')
    ControlLicense = ControlLicense('ControlLicense')
    ControlRequest = ControlRequest('ControlRequest')
    ControlEventManager = ControlEventManager('ControlEventManager')
    ControlTabManager = ControlTabManager('ControlTabManager')
    ControlAddDel = ControlAddDel('ControlAddDel')
    ControlModeManager = ControlModeManager('ControlModeManager')
    ControlShared = ControlShared('ControlShared')
    ControlSecurityManager = ControlSecurityManager('ControlSecurityManager')
    ControlLinkManager = ControlLinkManager('ControlLinkManager')
    ControlCallableRender = ControlCallableRender('ControlCallableRender')
    ControlDefaultManager = ControlDefaultManager('ControlDefaultManager')
    ControlConverter = ControlConverter('ControlConverter')

    security.declareObjectProtected('Manage Control Panel Form')

    security.declareProtected('Manage Control Panel Form', "index_html")
    def index_html(self):
        "Draw the ControlPanelForm"
        return ''.join([self.getCompoundDoc().begin_manage(), self.edit(), self.manage_page_footer()])

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        if name:
            if name in self.controlNames:
                menuSelected = self.REQUEST.other.get('menuSelected', {})
                menuSelected['ControlPanel'] = name
                self.REQUEST.other['menuSelected'] = menuSelected
            return getattr(self, name)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        queryDict = utility.getQueryDict(self.REQUEST.environ.get('QUERY_STRING', ''))
        return '<div class="configLeftBar">%s</div>%s' % (
                NestedListURL.drawNestedList(self.traverseContainer(queryDict=queryDict)),
                self.drawMenuSelected())

    security.declarePrivate('traverseContainer')
    def traverseContainer(self, queryDict = None):
        "return the items at this index recursively"
        queryDict = queryDict or {}
        temp = []
        menu = self.getMenuSelected()
        if menu:
            title = getattr(self, menu).control_title
        else:
            title = None
        containers = ((name, getattr(self, name)) for name in self.controlNames)
        containers = sorted((object.control_title, object, name) for name, object in containers)
        url = self.absolute_url_path()
        for control_title, object, name in containers:
            if control_title == title:
                temp.append((os.path.join(url, name), control_title, 1, '', queryDict, ''))
                temp.append(object.traverseContainer(queryDict=queryDict))
            else:
                temp.append((os.path.join(url, name), control_title, 0, '', queryDict, ''))
        return temp

Globals.InitializeClass(ControlPanel)
