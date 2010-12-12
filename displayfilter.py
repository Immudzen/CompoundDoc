import base
import operator

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from Acquisition import aq_base
from Products.PythonScripts.PythonScript import PythonScript
import cgi #used for escape
import utility
from useragent import UserAgent

class DisplayFilter(base.Base):
    "DisplayFilter apply this to an object to change how it outputs"

    meta_type = "DisplayFilter"
    security = ClassSecurityInfo()
    overwrite=1

    code = ''
    codeScript = None
    codetype = 'PythonScript'
    language = 'en'
    wrapperHeader = 'return context.standard_html_header()'
    wrapperHeaderScript = None
    wrapperFooter = 'return context.standard_html_footer()'
    wrapperFooterScript = None
    wrapperHeaderDTML = '<dtml-var standard_html_header>'
    wrapperFooterDTML = '<dtml-var standard_html_footer>'
    flags = None

    security.declarePrivate('instance')
    instance = (('UserAgent', ('create', 'DisplayUserAgent')), )

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        if self.codetype in ('DTML','Static'):
            return self.code
        elif self.codetype =='PythonScript':
            return self.codeScript
        return ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append('''<script type="text/javascript">
            $(function() {
            $("#tabsMode").tabs({ cache: true});
            });
            </script>
            ''')
        temp.append('<div id="tabsMode"><ul>')
        
        url = self.absolute_url_path()
        temp.append('<li><a href="%s/%s">%s</a></li>' % (url,  'editCode',  'Code'))
        temp.append('<li><a href="%s/%s">%s</a></li>' % (url,  'editSettings',  'Settings'))
        temp.append('<li><a href="%s/%s">%s</a></li>' % (url,  'editObjects',  'Objects'))
        temp.append('</ul></div>')
        temp.append(self.submitChanges())
        return ''.join(temp)

    security.declareProtected('View management screens', 'editObjects')
    def editObjects(self):
        "return a table of object listings with id and meta_type sorted by id"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % self.getEncoding())
        temp = []
        temp.append('<div>')
        items = self.getCompoundDoc().objectItems()
        table = sorted((key, value.meta_type) for key, value in items)
        temp.append(self.createTable(table))
        temp.append('</div>')
        return ''.join(temp)


    security.declareProtected('View management screens', 'editCode')
    def editCode(self):
        "draw the code edit interface"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % self.getEncoding())
        temp = []
        temp.append('<div>')
        if self.codetype == 'PythonScript' and self.codeScript:
            temp.append(self.drawScriptErrorsAndWarnings(self.codeScript))
        temp.append(self.text_area('code', self.code))
        temp.append('</div>')
        return ''.join(temp)

    security.declareProtected('View management screens', 'editSettings')
    def editSettings(self):
        "draw the settings edit interface"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % self.getEncoding())
        temp = []
        temp.append('<div>')
        temp.append("<p>Type is :</p>%s\n" % self.option_select(self.getAllowedTypes(),
                      'codetype', [self.codetype]))
        temp.append("<p>Language is :</p>%s\n" % self.option_select(UserAgent.getAllowedLanguages,
                      'language', [self.language]))

        if self.codetype == 'PythonScript' and self.wrapperHeaderScript:
            temp.append(self.drawScriptErrorsAndWarnings(self.wrapperHeaderScript))
        temp.append('<p>Header:</p>%s' % self.input_text('wrapperHeader', self.wrapperHeader))

        if self.codetype == 'PythonScript' and self.wrapperFooterScript:
            temp.append(self.drawScriptErrorsAndWarnings(self.wrapperFooterScript))
        temp.append('<p>Footer:</p>%s' % self.input_text('wrapperFooter', self.wrapperFooter))
        temp.append(self.UserAgent.short())
        temp.append('</div>')
        return ''.join(temp)


    def drawScriptErrorsAndWarnings(self, script):
        "draw the script errors and warnings for this script"
        temp = []
        if script.errors:
            temp.append('<p>Errors Found</p><pre class="scriptErrors">%s</pre>' % cgi.escape('\n'.join(script.errors), 1))
        if script.warnings:
            temp.append('<p>Warnings Found</p><pre class="scriptWarnings">%s</pre>' % cgi.escape('\n'.join(script.warnings), 1))
        return ''.join(temp)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "recompile the python script if we have one"
        if self.codetype == 'PythonScript':
            for i in ('code', 'wrapperHeader', 'wrapperFooter'):
                self.recompileScript(i)

    security.declarePrivate('recompileScript')
    def recompileScript(self, baseName):
        "recompile python script"
        scriptName = '%sScript' % baseName
        pyscript = getattr(self, scriptName, None)
        if pyscript is None:
            pyscript = PythonScript(scriptName)
            self.setObject(scriptName, pyscript)
        pyscript.ZPythonScript_edit('', getattr(self, baseName))

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

    security.declarePrivate("getAllowed")
    def getAllowedTypes(self):
        "Return the allowed types as a tuple"
        return ('DTML', 'PythonScript', 'Static')

    security.declarePrivate('willRender')
    def willRender(self):
        "return true if I can render given the current client language etc"
        Agent = self.getUserAgent()
        return [Agent.checkClientCompat(self.UserAgent.getClients(), self.UserAgent.operatingSystems),
            Agent.checkClientLanguage(self.language),
            self]

    security.declarePrivate('getWrappers')
    def getWrappers(self):
        "return the header and footer wrapper"
        if self.codetype == 'PythonScript':
            return (self.wrapperHeaderScript(), self.wrapperFooterScript())
        gen_html = self.getCompoundDoc().gen_html
        return (gen_html(self.wrapperHeader), gen_html(self.wrapperFooter))

    security.declarePrivate('getClients')
    def getClients(self):
        "Get the clients of this object"
        return getattr(aq_base(self), 'clients', None)

    security.declarePrivate('setClients')
    def setClients(self, clients):
        "set the clients for this object"
        self.setObject('clients', clients)

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        self.upgraderChangeUserAgentTuple()
        self.upgraderChangeTupleTreeAgent()
        self.upgraderFixAgents()
        self.removeOldVars()
        self.cleanupPythonScript()
        self.oldDTMLDefaultWrappers()
        self.correctIdOfScripts()

    security.declarePrivate('removeOldVars')
    def removeOldVars(self):
        "remove some old vars that are no longer needed"
        if 'optional' in self.__dict__:
            self.delObjects(['optional'])
        if 'required' in self.__dict__:
            self.delObjects(['required'])
    removeOldVars = utility.upgradeLimit(removeOldVars, 141)
    
    security.declarePrivate('cleanupPythonScript')
    def cleanupPythonScript(self):
        "cleanup the python script objects"
        if self.codetype == 'PythonScript':
            self.delObjects(['script', 'footerScript', 'headerScript'])
            if not self.objectIds('Script (Python)'):
                for i in ('code', 'wrapperHeader', 'wrapperFooter'):
                    self.recompileScript(i) 
    cleanupPythonScript = utility.upgradeLimit(cleanupPythonScript, 141)
            
    security.declarePrivate('correctIdOfScripts')
    def correctIdOfScripts(self):
        "Fix the id of scripts so they don't just say script"
        for name, script in self.objectItems('Script (Python)'):
            if script.id != name:
                script.id = name
    correctIdOfScripts = utility.upgradeLimit(correctIdOfScripts, 141)
    
    security.declarePrivate('oldDTMLDefaultWrappers')
    def oldDTMLDefaultWrappers(self):
        "add a dtml wrapper as default for an old dtml display filter"
        if self.codetype == 'DTML':
            wrapperHeader = self.__dict__.get('wrapperHeader', None)
            if wrapperHeader is None:
                self.setObject('wrapperHeader', self.wrapperHeaderDTML)
            wrapperFooter = self.__dict__.get('wrapperFooter', None)
            if wrapperFooter is None:
                self.setObject('wrapperFooter', self.wrapperFooterDTML)
    oldDTMLDefaultWrappers = utility.upgradeLimit(oldDTMLDefaultWrappers, 141)
    
    security.declarePrivate('upgraderChangeUserAgentTuple')
    def upgraderChangeUserAgentTuple(self, clients=None):
        "Change the user agent to the newer tuple format for detection"
        if not clients:
            clients = self.getClients()
        lookup = {
          'Konqueror/2.2':('Mozilla/5', 'Konqueror', '2', '2'),
          'Konqueror':('Mozilla/5', 'Konqueror', '', ''),
          'MSIE':('Mozilla/4', 'MSIE', '', ''),
          'MSIE 6': ('Mozilla/4', 'MSIE', '6', ''),
          'MSIE 6.0':('Mozilla/4', 'MSIE', '6', '0'),
          'MSIE 5':('Mozilla/4', 'MSIE', '5', ''),
          'MSIE 4':('Mozilla/4', 'MSIE', '4', ''),
          'MSIE 3':('Mozilla/3', 'MSIE', '3', ''),
          'MSIE 2':('Mozilla/2', 'MSIE', '2', ''),
          'MSIE 5.5':('Mozilla/4', 'MSIE', '5', '5'),
          'MSIE 5.0':('Mozilla/4', 'MSIE', '5', '0'),
          'Opera':('', 'Opera', '', ''),
          'Opera/6':('', 'Opera', '6', ''),
          'Opera/6.0':('', 'Opera', '6', '0'),
          'Opera/5':('', 'Opera', '5', ''),
          'Opera/5.0':('', 'Opera', '5', '0')}
        if operator.isSequenceType(clients):
            list = [lookup[i] for i in clients if i in lookup]
            if len(list):
                self.setClients(tuple(list))
    upgraderChangeUserAgentTuple = utility.upgradeLimit(upgraderChangeUserAgentTuple, 141)
    
    security.declarePrivate('upgraderChangeTupleTreeAgent')
    def upgraderChangeTupleTreeAgent(self):
        "Change the tuple structure to a tree"
        clients = self.getClients()
        if operator.isSequenceType(clients):
            self.setClients(utility.mergeSequenceTree(clients))
    upgraderChangeTupleTreeAgent = utility.upgradeLimit(upgraderChangeTupleTreeAgent, 141)
    
    security.declarePrivate('upgraderFixAgents')
    def upgraderFixAgents(self):
        "Fix the useragent detection vars to use the newer DisplayUserAgent object"
        if self.hasObject('clients') and self.clients is not None:
            self.gen_vars()
            mapping = self.UserAgent.clientSetMapping()
            for key, value in mapping.items():
                if key and value:
                    mapping[key] = getattr(self.UserAgent, value)()
                else:
                    del mapping[key]
            for setname, clients in mapping.items():
                if self.clients == clients:
                    self.UserAgent.setused = setname
                    self.delObjects(['clients'])
                    break
            if self.hasObject('clients') and self.clients is not None:
                self.UserAgent.setClients(self.clients)
                self.delObjects(['clients'])
    upgraderFixAgents = utility.upgradeLimit(upgraderFixAgents, 141)
     
Globals.InitializeClass(DisplayFilter)
import register
register.registerClass(DisplayFilter)
