from base import Base
import useragent

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import utility

class DisplayUserAgent(Base):
    "DisplayFilter apply this to an object to change how it outputs"

    meta_type = "DisplayUserAgent"
    security = ClassSecurityInfo()
    overwrite=1
    data = ''
    clients = None
    setused = ''
    operatingSystems = None

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "process the edits"
        userAgentSelect = dict.pop('userAgentSelect', None)
        if userAgentSelect is not None:
            self.setClients({})
            try:
                del dict['userAgent']
            except KeyError:
                pass

        operatingSystems = dict.pop('operatingSystems', None)
        if operatingSystems is not None:
            allowedOS = useragent.UserAgent.getAllowedOperatingSystems
            temp = [i for i in operatingSystems if i in allowedOS]
            if temp:
                self.setObject('operatingSystems', temp)

        userAgent = dict.pop('userAgent', None)
        if userAgent is not None:
            seq = []
            for i in userAgent:
                i = i.split(' ')
                length = 4 - len(i)
                i.extend([''] * length)
                seq.append(tuple(i))
            clients = utility.mergeSequenceTree(seq)
            if clients:
                self.setClients(clients)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"

        temp = [self.short()]
        temp.append('<p>Supported Clients:</p>%s<div>%s</div>' % (self.create_button('userAgentSelect', 'Unselect All'),
          self.createMultiListDict(useragent.getAvailableClients(), self.getClients(), 'userAgent')))
        format = '<p>Supported Operating Systems:</p><div>%s</div>'
        allowedOS = [''] + list(useragent.UserAgent.getAllowedOperatingSystems)
        os = []
        if self.operatingSystems is not None:
            os = self.operatingSystems
        temp.append(format % self.option_select(allowedOS, 'operatingSystems', os, multiple=1, size=len(allowedOS)))
        return ''.join(temp)

    security.declarePrivate('short')
    def short(self):
        "short editing view for this object"
        return "<p>UserAgent Set : %s</p>\n" % self.option_select(self.clientSets(),
                'setused', [self.setused])

    security.declarePrivate('setClients')
    def setClients(self, clients):
        "set the clients for this object"
        if not clients:
            clients = None
        self.setObject('clients', clients)

    security.declarePrivate('getClients')
    def getClients(self):
        "Get the clients of this object"
        if self.setused:
            return self.getSetClients()
        if self.clients is not None:
            return self.clients
        return {}

    def clientSets(self):
        "returns a list of the client sets that we have"
        return self.clientSetMapping().keys()

    def clientSetMapping(self):
        "Return a dict of sets, funcname mappings"
        sets = {}
        sets['XHTML 1.0 CSS1'] = 'XHTML10CSS1'
        sets['XHTML 1.0 CSS2'] = 'XHTML10CSS2'
        sets['HTML4'] = 'HTML4'
        sets['MSIE 5 and 6'] = 'MSIE56'
        sets['No Detection'] = 'noDetection'
        sets[''] = ''
        return sets

    def getSetClients(self):
        "Return the clients that matches this set name"
        setname = self.setused
        if setname in self.clientSets():
            funcname = self.clientSetMapping()[setname]
            return getattr(self, funcname)()

    def XHTML10CSS1(self):
        "Opera 5 and 6, MSIE 5 and 6"
        return {'':{'Opera': {'6': {'': {}}, '5': {'': {}}}},
          'Mozilla/4': {'MSIE': {'6': {'': {}}, '5': {'': {}}}}}

    def XHTML10CSS2(self):
        "Mozilla/5 and the W3C_Validator selected"
        return {'Mozilla/5': {'': {'': {'': {}}}}, '': {'W3C_Validator': {'': {'': {}}}}}

    def HTML4(self):
        "Mozilla/4 browsers selected"
        return {'Mozilla/4': {'': {'': {'': {}}}}}

    def MSIE56(self):
        "Only IE 5 and 6 selected"
        return {'Mozilla/4': {'MSIE': {'6': {'': {}}, '5': {'': {}}}}}

    def noDetection(self):
        "No UserAgents selected"
        return {}
   
    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.repairSetused()
        self.removeBlankOSClients()
        
    security.declarePrivate('repairSetused')
    def repairSetused(self):
        "fix the xhtml entry for set used"
        if self.setused == 'XTML 1.0 CSS2':
            self.setused = 'XHTML 1.0 CSS2'         
    repairSetused = utility.upgradeLimit(repairSetused, 141)
    
    
    security.declarePrivate('removeBlankOSClients')
    def removeBlankOSClients(self):
        "remove blank operatingSystems and clients entries"
        if not self.clients:
            self.delObjects(['clients'])
        if not self.operatingSystems:
            self.delObjects(['operatingSystems'])
    removeBlankOSClients = utility.upgradeLimit(removeBlankOSClients, 161)
   
Globals.InitializeClass(DisplayUserAgent)
import register
register.registerClass(DisplayUserAgent)
