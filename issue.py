# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

#For Security control and init
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized, getSecurityManager
import Globals

from listtext import ListText
from BTrees.OOBTree import OOBTree

class Issue(ListText):
    "this object represents a single votable Issue"

    security = ClassSecurityInfo()
    meta_type = "Issue"
    storage = None
    votes = None
    description = ''
    addType = 'IssueChoice'
    selectionType = "radio"
    selectionLimit = 1
    selectionLimitMin = 0
    format = '<div>%s</div>'
    MustSelectOne = '<strong>At least one choice must be made.</strong>'
    TooManyItems = '<strong>Too many items where selected.</strong>'
    NotEnoughItems = '<strong>Not Enough items where selected.</strong>'
    BadItemSelected = '''<strong>An item was selected that does not exist.
    You should never see this message please email the webmaster.</strong>'''
    voteText = '''%(error)s<div class="issue"><div class="issueDescription">%(description)s</div>
      <div class="issueChoices">%(issues)s</div></div>
    '''
    alreadyVotedText = '<p>You have already voted</p>'
    noVotingAllowed = '<p>Voting is not currently allowed</p>'
    thankYouText = '<p>Thank you for voting</p>'
    deleteButtonText = 'Delete Issue Choice'
    addButtonText = 'Add Issue Choice'


    selectionAllowedTypes = ( ('radio', 'Single Selection'), ('checkbox', 'Multiple Selection') )

    classConfig = {}
    classConfig['selectionLimit'] = {'name':'If you have selected multiple selection mode how many choices can people make (MAX)?', 'type':'int'}
    classConfig['selectionLimitMin'] = {'name':'If you have selected multiple selection mode how many choices do people have to make? (MIN)', 'type':'int'}
    classConfig['selectionType'] = {'name':'Allowed Selections', 'type':'list', 'values': selectionAllowedTypes}
    classConfig['description'] = {'name':'Issue Description', 'type':'text'}
    
    drawDict = ListText.drawDict.copy()
    drawDict['vote'] = 'drawVote'
    drawDict['voteChecked'] = 'drawVoteChecked'
    drawDict['report'] = 'drawReport'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = self.editSingleConfig('description')
        temp += self.editSingleConfig('selectionType')
        temp += self.editSingleConfig('selectionLimit')
        temp += self.editSingleConfig('selectionLimitMin')
        return temp + ListText.edit(self)

    security.declareProtected('CompoundDoc: Voting', 'alternate_security_edit')
    def alternate_security_edit(self, dict):
        "save the voting information if it is okay to do so"
        choices = None
        if 'choices' in dict:
            choices = dict.get('choices').values()
            del dict['choices']
        if choices:
            choices = [choice for choice in choices if choice]
            uid = self.getUID()
            if self.isOkayToVote(uid):
                self.vote(uid,choices)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

    security.declareProtected('CompoundDoc: Voting', 'drawVote')
    def drawVote(self):
        "draw the voting interface"
        return self.drawVoteChecked()[1]

    security.declareProtected('CompoundDoc: Voting', 'drawVoteChecked')
    def drawVoteChecked(self):
        "draw the voting interface"
        structure = self.voteStructure()
        structure['error'],messageType = self.drawError()
        uid = self.getUID()
        if messageType == 'thankYouText':
            return (False, self.getMessage('thankYouText', structure))
        if self.voteEnabled:
            if self.isOkayToVote(uid):
                return (True, self.getMessage('voteText',structure))
            elif self.alreadyVoted(uid):
                return (False, self.getMessage('alreadyVotedText',structure))
            else:
                return (False, self.getMessage('notAllowedToVote',structure))
        else:
            return (False, self.getMessage('noVotingAllowed',structure))

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

    security.declarePrivate('drawError')
    def drawError(self):
        "draw any needed any message"
        return self.getErrorMessage()

    def hasErrorMessage(self):
        "do we have an error message to draw?"
        messages = self.REQUEST.other.get('messages', {})
        return self.getPhysicalPath() in messages

    def getErrorMessage(self):
        "get the current Error Message"
        messages = self.REQUEST.other.get('messages', {})
        return messages.get(self.getPhysicalPath(), ('',''))

    def writeErrorMessage(self, message, messageType):
        "write the current error message so we can get it later"
        messages = self.REQUEST.other.get('messages', {})
        messages[self.getPhysicalPath()] = (message,messageType)
        self.REQUEST.other['messages'] = messages

    security.declarePrivate('voteStructure')
    def voteStructure(self):
        "get the voting data structure"
        lookup = {}
        lookup['description'] = self.description

        temp = []
        if len(self):
            if self.selectionType == 'radio':
                choices = [(choice.view(),choice.view()) for choice in self]
                temp = self.radio_list('radio', choices,  containers=('choices',) )
                formName = self.formName('radio','string', ('choices',))
                temp.append('<input type="hidden" name="%s:default" value="">' % formName)
            elif self.selectionType == 'checkbox':
                formName = self.formName('default','string', ('choices',))
                temp.append('<input type="hidden" name="%s:default" value="">' % formName)
                for choice in self:
                    temp.append(self.check_box(choice.getId(),choice.view(), ('choices',) )+ choice.view())
            if temp:
                temp = [self.format % i for i in temp]

        lookup['issues'] = ''.join(temp)
        return lookup

    security.declarePrivate('isOkayToVote')
    def isOkayToVote(self, uid):
        "is it okay to vote"
        try:
            if getSecurityManager().validate(None, self, 'drawVote',self.drawVote) and self.voteEnabled and not self.alreadyVoted(uid) and self.isOkayToVoteUserDefined():
                return True
        except Unauthorized:
            pass

    security.declarePrivate('alreadyVoted')
    def alreadyVoted(self, uid):
        "is it okay to vote"
        return self.getStorage().has_key(uid)

    security.declarePrivate('drawReport')
    def drawReport(self):
        "draw a basic report of the voting results"
        results = self.report()
        results = [(votes, issueName) for issueName,votes in results]
        results.sort(reverse=True)
        results.insert(0, ('Number of Votes', 'Choice'))
        results.append( ('Total Number of Votes', len(self.getStorage())) )
        temp = '<p>%s</p>' % self.description
        temp += self.createTable(results)
        return temp

    security.declarePrivate('report')
    def report(self):
        "return the report of how the votes went"
        return self.getVotes().items()

    security.declareProtected('CompoundDoc: Voting Stats', 'getVotes')
    def getVotes(self):
        "get the current vote information"
        if self.votes is not None:
            return self.votes
        return OOBTree()

    security.declareProtected('CompoundDoc: Voting Stats', 'getStorage')
    def getStorage(self):
        "get the current storage information which is a mapping of who has voted"
        if self.storage is not None:
            return self.storage
        return OOBTree()

    security.declareProtected('View', 'vote')
    def vote(self, uid, choices):
        "increase the count for this choice in votes if this uid is not already recorded"
        if self.isValidChoices(choices) and not self.getStorage().has_key(uid):
            self.uidVoted(uid)
            self.choiceSelected(choices)

    security.declarePrivate('isValidChoices')
    def isValidChoices(self, choices):
        "return true if all of the choices given are valid given the state of this object"
        allowedLength = 1
        allowedLengthMin = 0
        lookup = {}
        if self.selectionType == "checkbox":
            allowedLength = self.selectionLimit
            allowedLengthMin = self.selectionLimitMin
        lookup['selected'] = len(choices)
        lookup['max_selected'] = allowedLength
        lookup['min_selected'] = allowedLengthMin
        lookup['bad_choice'] = ''
        if not len(choices):
            self.writeErrorMessage(self.getMessage('MustSelectOne',lookup), 'MustSelectOne')
            return 0
        if len(choices) > allowedLength:
            self.writeErrorMessage(self.getMessage('TooManyItems',lookup),'TooManyItems')
            return 0
        if len(choices) < allowedLengthMin:
            self.writeErrorMessage(self.getMessage('NotEnoughItems',lookup),'NotEnoughItems')
            return 0
        allowedChoices = [i.view() for i in self]
        for choice in choices:
            if choice not in allowedChoices:
                lookup['bad_choice'] = choice
                self.writeErrorMessage(self.getMessage('BadItemSelected', lookup),'BadItemSelected')
                return 0
        return 1

    security.declarePrivate('uidVoted')
    def uidVoted(self, uid):
        "record that this uid has voted for this issue"
        if self.storage is None:
            self.storage = OOBTree()
        if not self.storage.has_key(uid):
            self.storage[uid] = True

    security.declarePrivate('choiceSelected')
    def choiceSelected(self, choices):
        "increment the counter for this choice"
        if self.votes is None:
            self.votes = OOBTree()
        lookup = {}
        lookup['choices'] = choices
        self.writeErrorMessage(self.getMessage('thankYouText', lookup),'thankYouText')
        for choice in choices:
            count = self.votes.get(choice, 0)
            count += 1
            self.votes[choice] = count

    security.declarePrivate('classUpgrader')
    def classUpgrader(self):
        "upgrade this class"
        return None

Globals.InitializeClass(Issue)
import register
register.registerClass(Issue)
