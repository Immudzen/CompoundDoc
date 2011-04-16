#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase
from AccessControl import ClassSecurityInfo
import Globals
from Acquisition import aq_base
import utility
import zExceptions

class ControlProfileManager(ControlBase):
    "Input text class"

    meta_type = "ControlProfileManager"
    security = ClassSecurityInfo()
    control_title = 'Profile'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        temp.append('<div class="">')
        temp.append(self.saveCurrentProfileControl())  
        temp.append(self.quickProfForm())
        temp.append('<div>')
        if self.profile:
            temp.append(self.clearProfile())
        if self.masterLocation is None or self.masterLocation and self.masterLocation != self.getCompoundDoc().getPath():
            temp.append('<p>')
            temp.append(self.create_button('master', 'Master Profile Set'))
            temp.append('</p>')
        if self.masterLocation is not None:
            temp.append('<p>')
            temp.append(self.create_button('unsetMaster', 'Unset the master'))
            temp.append('</p>')
        temp.append('</div>')
        temp.append('<p>Make this document into a profile: </p>')
        temp.append('<p>This name can only have numbers and letters in it.</p>')
        temp.append(self.input_text('profileName', ''))
        temp.append(self.submitChanges())
        temp.append('<p>Path: %s</p>' % self.input_text('path', ''))
        temp.append('<p>Profile: %s</p>' % self.drawProfilesAvailable())
        temp.append('<p>Profile to change to: %s</p>' % self.draw_profiles('profileTypeChange'))
        temp.append(self.create_button('multiple_change', 'Multiple Change'))
        temp.append(self.create_button('multiple_change', 'Multiple Change Rendering'))
        cdoc = self.getCompoundDoc()
        temp.append('<p>Select the types of objects that you want this profile to keep when it is changed.</p>')
        temp.append('<p>There are %s currently selected items.</p>' % len(cdoc.getProfileTypeKeep()))
        available =[''] + cdoc.availableObjects()
        temp.append('<p>%s</p>' % cdoc.multiselect('profileTypeKeep', available, cdoc.getProfileTypeKeep(), size=10))
        temp.append(self.submitChanges())
        if self.REQUEST.other.get('results', ''):
            temp += ["<p>%s</p>" % i for i in self.REQUEST.other['results']]
        temp.append('</div>')
        return ''.join(temp)

    security.declarePrivate('saveCurrentProfileControl')
    def saveCurrentProfileControl(self):
        "Draw a control to save the current profile"
        if self.profile and self.profile != 'None':
            button = self.create_button('profileSave', self.profile)
            return '<p>Save this Profile %s</p>' % button
        return ''

    security.declarePrivate('quickProfForm')
    def quickProfForm(self):
        "This is an inline quick selecter for layouts and profiles."
        return self.profSelector()

    security.declarePrivate('clearProfile')
    def clearProfile(self):
        "This is an inline quick selecter for layouts and profiles."
        return self.create_button('profileUnset', 'Unset Profile')

    security.declarePrivate('profSelector')
    def profSelector(self):
        "This is the simple layout and profile selector."
        changeProfile = self.create_button("profile_action", "Change Profile")
        changeRendering = self.create_button("profile_action", "Change Rendering Code")
        return self.draw_profiles() + changeProfile + changeRendering

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form=None):
        "This item is in charge of the profile/layout manager object"
        cdoc = self.getCompoundDoc()
        if 'master' in form:
            self.resetMaster()
            cdoc.setObject('masterLocation', cdoc.getPath())
        if 'profileUnset' in form:
            cdoc.profile = ''
            self.resetMaster()
            cdoc.delObjects(['masterLocation'])
        if 'unsetMaster' in form:
            self.resetMaster()
            cdoc.delObjects(['masterLocation'])    
        if 'profile_action' in form:
            if form['profile_action'] == "Change Profile":
                self.changeProfile(form['profile'])
            elif form['profile_action'] == "Change Rendering Code":
                self.changeDisplay(form['profile'])
        if 'profileName' in form and form['profileName']:
            utility.objectStoreFile(aq_base(cdoc), form['profileName'])
        if 'profileSave' in form and form['profileSave']:
            utility.objectStoreFile(aq_base(cdoc), form['profileSave'])
        if 'path' in form and form['path'] and 'multiple_change' in form:
            renderOnly = 0
            if form['multiple_change'] == 'Multiple Change Rendering':
                renderOnly = 1
            results = self.profileChanger(form['path'], form['profileTypeLimit'], form['profileTypeChange'], renderOnly)
            self.REQUEST.other['results'] = results

    security.declareProtected('CompoundDoc: Test', 'changeAllProfiles')
    def changeAllProfiles(self):
        "change to all profiles that this compounddoc has in sequence"
        for i in utility.getStoredProfileNames():
            self.changeProfile(i)
        return 'KAPLAA!'

    security.declarePrivate('profileChanger')
    def profileChanger(self, path, profileLimit, profileSet, renderOnly = 0):
        "change all the profiles from path on down"
        catalog = self.getPhysicalRoot().CDocUpgrader
        records = catalog(path=path, profile=profileLimit)
        temp = []
        self.REQUEST.other['okayToRunNotification'] = 0
        for record in utility.subTrans(records,  100):
            try:
                cdoc = record.getObject()
                if cdoc is not None:
                    if renderOnly:
                        cdoc.changeDisplay(profileSet)
                    else:
                        cdoc.changeProfile(profileSet)
                    temp.append(cdoc.absolute_url_path())
                else:
                    utility.removeRecordFromCatalog(catalog, record)
            except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                pass
        return temp

    security.declarePrivate('draw_profiles')
    def draw_profiles(self, varname='profile'):
        "Draw the profiles"
        temp = [''] + utility.getStoredProfileNames()
        return self.option_select(temp, varname, [utility.renderNoneAsString(self.profile,'None')])

    security.declarePrivate('drawProfilesAvailable')
    def drawProfilesAvailable(self):
        "Draw the profiles"
        temp = [''] + list(self.getPhysicalRoot().CDocUpgrader.uniqueValuesFor('profile'))
        return self.option_select(temp, 'profileTypeLimit', [getattr(self, 'profile', '')])

Globals.InitializeClass(ControlProfileManager)
