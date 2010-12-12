#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html  kosh@aesaeion.com

#For Security control and init
from AccessControl import ClassSecurityInfo
import Acquisition
import Globals

def getAvailableClients():
    "Return a list of all available clients"
    konqueror = {'2':{'2':{}}, '3':{}}
    ie6 = {'0':{}}
    ie5 = {'0':{}, '5':{}}
    ie3 = {'3':{}}
    ie2 = {'2':{}}
    ie = {'5':ie5, '4':{}, '6':ie6}
    opera = {'5':{}, '6':{}}
    mozilla5 = {'Konqueror':konqueror}
    mozilla4 = {'MSIE': ie}
    mozilla3 = {'MSIE': ie3}
    mozilla2 = {'MSIE': ie2}
    nomozilla = {'Opera':opera, 'W3C_Validator':{}}
    agents = {'Mozilla/5':mozilla5, 'Mozilla/4':mozilla4,
      '':nomozilla, 'Mozilla/3':mozilla3, 'Mozilla/2':mozilla2}
    return agents

class UserAgent(Acquisition.Implicit):
    "This class will detect the UserAgent and provide it in a format for other objects to use"

    security = ClassSecurityInfo()
    
    security.declareObjectProtected('View')
    
    def __init__(self, REQUEST=None, agentString=None, langString=None):
        "create a UserAgent object using this REQUEST variable"
        lang = langString
        if REQUEST and not lang:
            lang = REQUEST.HTTP_ACCEPT_LANGUAGE
        if not lang:
            lang = 'en'
        self.language = lang
        if agentString is None:
            agentString = REQUEST.HTTP_USER_AGENT
        (self.agent, self.os) = self.parseAgent(agentString)

    def parseAgent(self, string):
        "Parse the agent string into a tuple of lookup values"
        generation = self.agentGeneration(string)
        agentType = self.agentType(string)
        major,minor = self.agentVersion(agentType, string)
        os = self.getOperatingSystemVersion(string)
        return ((generation, agentType, major, minor), os)

    def agentGeneration(self, string):
        "Get the generation of the client"
        begin = string.find("Mozilla")
        if begin != -1:
            return string[begin:begin+9]
        return ''

    def agentType(self, string):
        "Get the type of the agent it defaults to Netscape if nothing else can be found"
        for i in ('Opera', 'MSIE', 'Konqueror', 'W3C_Validator'):
            if i in string:
                return i
        return ''

    def getOperatingSystemVersion(self, string):
        "Get the os version of this client"
        for i in self.getAllowedOperatingSystems:
            if i in string:
                return i
        return ''

    def agentVersion(self, browser, string):
        "get the agent version"
        if browser == '' and "Mozilla" in string:
            browser = 'Mozilla'
        if browser:
            beg = string.find(browser) + len(browser) + 1
        else:
            return '',''
        splitter = ' '
        if browser in ['Konqueror', 'MSIE']:
            splitter = ';'
        end = string.find(splitter, beg)
        #Grab only the first two entries in case there are more
        result = string[beg:end].split('.')[0:2]
        if len(result) != 2:
            return result[0],''
        return result

    getAllowedLanguages = ['en', 'fr']
    getAllowedOperatingSystems = ('Mac', 'Linux', 'Windows')

    security.declareProtected('View', 'checkClientCompat')
    def checkClientCompat(self, clients, os=None):
        "Check and see if client is compatible with what useragent and operating system that we are"
        temp = clients
        wildcard=1.0
        try:
            if os and self.os not in os:
                return 0
            elif os and self.os in os:
                wildcard=wildcard+.1
            for i in self.agent:
                if i in temp:
                    temp=temp[i]
                elif '' in temp:
                    wildcard=wildcard-.1
                    temp=temp['']
                else:
                    return 0
            return wildcard
        except:
            return 0

    def checkClientLanguage(self, lang):
        "Check and see if lang is compatible with what language we are"
        return self.language.count(lang)

Globals.InitializeClass(UserAgent)    