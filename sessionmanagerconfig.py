import basesessionmanager

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class SessionManagerConfig(basesessionmanager.BaseSessionManager):
    "SessionManagerConfig tracks this objects usage of session managers"

    meta_type = "SessionManagerConfig"
    security = ClassSecurityInfo()
    overwrite=1
    sessionManager = None

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ""

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        if self.sessionManager is None:
            self.sessionManager = self.getDefaultSessionManager()
        return "<div>Available Session Managers : %s</div>\n" % self.option_select(self.getAvailableSessionManagers(),
                      'sessionManager', [self.sessionManager])

Globals.InitializeClass(SessionManagerConfig)
import register
register.registerClass(SessionManagerConfig)