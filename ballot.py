# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo, getSecurityManager
import Globals

from listtext import ListText

import uidgenerator

class Ballot(ListText):
    "this object represents a single votable Issue"

    security = ClassSecurityInfo()
    meta_type = "Ballot"
    description = ''
    addType = 'Issue'
    voteEnabled = 0
    voteButtonString = 'Vote Now'
    voteMode = 'vote'
    uid = 'UserName'
    messageFolderPath = ''
    deleteButtonText = 'Delete Ballot Issue'
    addButtonText = 'Add Ballot Issue'
    userDefinedTestForVoting = ''
    notAllowedToVote = '<p>You are not allowed to vote</p>'

    classConfig = {}
    classConfig['uid'] = {'name':'Unique ID', 'type':'list', 'values': uidgenerator.lookup.keys()}
    classConfig['messageFolderPath'] = {'name':'Folder with customized messages:', 'type':'string'}
    classConfig['description'] = {'name':'Issue Description:', 'type':'text'}
    classConfig['voteEnabled'] = {'name':'Enable Voting:', 'type':'radio'}
    classConfig['voteButtonString'] = {'name':'Vote Button String:', 'type':'string'}
    classConfig['userDefinedTestForVoting'] = {'name':'Name of an attribute for user defined voting test:', 'type':'string'}

    drawDict = ListText.drawDict.copy()
    drawDict['vote'] = 'drawVote'
    drawDict['report'] = 'drawReport'
    
    voteTypes =  ( ('vote', 'Voting Mode (results shown when voting ends)'),
        ('poll', 'Poll Mode (results shown at any time)'),
        ('simple', '(Insecure)Results are only shown to admin as voting takes place') )

    security.declarePrivate('getMessageFolder')
    def getMessageFolder(self):
        "get the message folder if we can"
        if self.messageFolderPath:
            return self.getCompoundDocContainer().restrictedTraverse(self.messageFolderPath, None)

    security.declarePrivate('getMessage')
    def getMessage(self, messageType, lookup):
        """if we have a url for a set of messages to use on errors go ahead and use that otherwise use the default string we have
        and get variables from this lookup(dictionary) object"""
        folder = self.getMessageFolder()
        if folder is not None:
            item = getattr(folder, messageType, None)
            if item is not None:
                return item.__of__(self)(lookup)
        return getattr(self, messageType) % lookup

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = self.editSingleConfig('description')
        temp += self.editSingleConfig('voteEnabled')
        temp += self.editSingleConfig('voteButtonString')
        temp += '<p>Voting Mode:%s</p>' % self.option_select(self.voteTypes, 'voteMode', selected=[self.voteMode])
        temp += self.editSingleConfig('uid')
        return temp + ListText.edit(self)

    security.declarePrivate('configAddition')
    def configAddition(self):
        "Inline edit view"
        temp = '''<p>The customized messages folder can have any of the following named scripts (%s)
        and those scripts have access to the following variables (%s) in the dictionary handed in</p>
        ''' % (','.join(self.getMessageTypes()), ','.join(self.getLookupVars()))
        return temp

    security.declareProtected("Access contents information", "getMessageTypes")
    def getMessageTypes(self):
        'get the various allowed message types'
        return ('MustSelectOne', 'TooManyItems', 'BadItemSelected', 'NotEnoughItems', 'alreadyVotedText',
            'noVotingAllowed', 'thankYouText', 'notAllowedToVote')

    security.declareProtected("Access contents information", "getLookupVars")
    def getLookupVars(self):
        'return a list of the allowed lookup variables'
        return ('selected', 'max_selected', 'bad_choice', 'min_selected')

    security.declareProtected("Access contents information", 'getUID')
    def getUID(self):
        "get the unique id for this ballot"
        return uidgenerator.getUID(self.uid, self)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

    security.declareProtected('View', 'drawVote')
    def drawVote(self):
        "draw the voting interface"
        temp = []
        if getSecurityManager().checkPermission('CompoundDoc: Voting', self):
            if self.isOkayToVoteUserDefined():
                if not self.voteEnabled:
                    return '<p>Voting is not currently allowed. The ballot is read only.</p>'
                if len(self) and self.voteEnabled:
                    temp.append(self.gen_html(self.description))
                    drawButton = False
                    for i in self:
                        isForm,text = i.drawVoteChecked()
                        if isForm:
                            drawButton = True
                        temp.append(text)
                    if drawButton:
                        temp.append('<div>%s</div>' % self.create_button('vote', self.voteButtonString))
                    return ''.join(temp)
            return self.getMessage('notAllowedToVote',dict())
        return ''

    def isOkayToVoteUserDefined(self):
        """Check if it is okay to vote. This will normally always return 1 but you can have
        a script hooked to it which can query other items in the db to provide additional conditions
        to see if someone is allowed to vote. This method only really makes sense for username UID mode"""
        if self.userDefinedTestForVoting:
            uid = self.getUID()
            if uid is not None:
                cdoc = self.getCompoundDoc()
                script = cdoc.restrictedTraverse(self.userDefinedTestForVoting, None)
                if script is not None:
                    return cdoc.changeCallingContext(script)(uid)
            return False
        return True

    security.declareProtected('View', 'drawReport')
    def drawReport(self):
        "return the report of how the votes went"
        temp = []
        if getSecurityManager().checkPermission('CompoundDoc: Voting', self):
            if self.checkDrawReport():
                for i in self:
                    temp.append(i.drawReport())
        return ''.join(temp)

    def checkDrawReport(self):
        "check if it is okay to draw the voting report"
        if len(self):
            if self.voteMode in ('poll', 'simple'):
                return True
            if self.voteMode == 'vote' and not self.voteEnabled:
                return True
        return False

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        return None

Globals.InitializeClass(Ballot)
import register
register.registerClass(Ballot)
