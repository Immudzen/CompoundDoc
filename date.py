# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from userobject import UserObject

#Import DateTime for date and time support
import DateTime

class Date(UserObject):
    "Date Class"

    security = ClassSecurityInfo()
    meta_type = "Date"
    allowedFormats  = {}
    allowedFormats[''] = {'example':'1997/03/01 13:45:00.0 GMT-6', 'where':'DateTime'}
    allowedFormats['aCommon'] = {'example':'Mar 1, 1997 1:45 pm', 'where':'DateTime'}
    allowedFormats['pCommon'] = {'example':'Mar. 1, 1997 1:45 pm', 'where':'DateTime'}
    allowedFormats['Date'] = {'example':'1997/03/01', 'where':'DateTime'}
    allowedFormats['fCommon'] = {'example':'March 1, 1997 1:45 pm', 'where':'DateTime'}
    allowedFormats['ISO'] = {'example':'1997-03-01 13:45:00', 'where':'DateTime'}
    allowedFormats['dropDownDate'] = {'example':'1997 March 1 (DropDown)', 'where':'Local'}
    allowedFormats['dropDownTimeAMPM'] = {'example':'1997 March 1 1:45 pm (DropDown)', 'where':'Local'}
    allowedFormats['dropDownTime24H'] = {'example':'1997 March 1 13:45 (DropDown)', 'where':'Local'}
    selectedFormat = ''
    data = ''

    dropDownSelection = sorted((key, '%s [%s]' % (value['example'], key)) for key, value in allowedFormats.iteritems())
    monthNames = ('', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
                    'August', 'September', 'October', 'November', 'December')
    monthNamesAbbr = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

    yearOffSetBefore = 1
    yearOffSetAfter = 5
    attributeNameForCustomCreation = ''
    scriptPath = ""
    enableDateClearing = 1

    classConfig = {}
    classConfig['selectedFormat'] = {'name':'Edit Date Format', 'type':'list', 'values': dropDownSelection}
    classConfig['yearOffSetBefore'] = {'name':'How many years to show before now in dropdown?', 'type':'int'}
    classConfig['yearOffSetAfter'] = {'name':'How many years to show after now in dropdown?', 'type':'int'}
    classConfig['attributeNameForCustomCreation'] = {'name':'Name of attribute for custom date creation?', 'type':'string'}
    classConfig['scriptPath'] = {'name':'Path to Script', 'type':'path'}
    classConfig['enableDateClearing'] = {'name':'Enable Date Clearing?', 'type': 'radio'}

    updateReplaceList = ('selectedFormat', 'yearOffSetBefore', 'yearOffSetAfter', 'attributeNameForCustomCreation', 'scriptPath', 'enableDateClearing' )

    configurable = ('enableDateClearing', 'scriptPath', 'attributeNameForCustomCreation', 'selectedFormat', 'yearOffSetBefore', 'yearOffSetAfter')

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        return '<p>%s</p>' % self.create_button('clear', 'Clear This Date', title='Clear This Date')

    def dateClearButton(self):
        "return a button to clear the date object"
        if self.getConfig('enableDateClearing'):
            return self.create_button('clear', 'Cl', title='Clear This Date')
        return ''
    
    def getDateParts(self):
        "return the parts of the date and blank strings if we don't have a date"
        date = self.Date()
        if date:
            return date.parts()
        return ('', 0, 0, 0, 0, 0, '')
    
    def dropDownDate(self, yearOffSetBefore, yearOffSetAfter):
        "generate a drop down format for this date format"
        year , month, day = self.getDateParts()[:3]
        currentYear = self.ZopeTime().parts()[0]
        yearMin = currentYear - yearOffSetBefore
        if year and year < yearMin:
            yearMin = year
        yearMax = currentYear + yearOffSetAfter
        if year and year > yearMax:
            yearMax = year

        month = self.monthNames[month]
        monthDrop = self.option_select(self.monthNames, 'month', [month], containers=['date'])
        dayDrop = self.option_select(xrange(0,32), 'day', [day], containers=['date'])
        yearDrop = self.option_select([''] + range(yearMin, yearMax+1), 'year', [year], containers=['date'])
        return yearDrop + monthDrop + dayDrop

    def dropDownTimeAMPM(self, yearOffSetBefore, yearOffSetAfter):
        "generate a drop down control for this date with a time component"
        hour, minute = self.getDateParts()[3:5]
        halfOfDay, hour = divmod(hour, 12)
        ampm = ['am', 'pm'][halfOfDay]
        hourDrop = self.option_select(xrange(0,13), 'hour', [hour], containers=['date'])
        minute1, minute2 = divmod(minute, 10)
        minuteDrop1 = self.option_select(xrange(0,6), 'minute1', [minute1], containers=['date'])
        minuteDrop2 = self.option_select(xrange(0,10), 'minute2', [minute2], containers=['date'])
        ampmDrop = self.option_select(['am', 'pm'], 'ampm', [ampm], containers=['date'])
        temp = '&nbsp; %s:%s%s %s' % (hourDrop, minuteDrop1, minuteDrop2, ampmDrop)
        return self.dropDownDate(yearOffSetBefore, yearOffSetAfter) + temp

    def dropDownTime24H(self, yearOffSetBefore, yearOffSetAfter):
        "generate a drop down control for this date with a 24 hour time component"
        hour, minute = self.getDateParts()[3:5]
        hourDrop = self.option_select(xrange(0,25), 'hour', [hour], containers=['date'])
        minute1, minute2 = divmod(minute, 10)
        minuteDrop1 = self.option_select(xrange(0,6), 'minute1', [minute1], containers=['date'])
        minuteDrop2 = self.option_select(xrange(0,10), 'minute2', [minute2], containers=['date'])
        temp = '&nbsp; %s:%s%s' % (hourDrop, minuteDrop1, minuteDrop2)
        return self.dropDownDate(yearOffSetBefore, yearOffSetAfter) + temp
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, format=None, yearsBefore=None, yearsAfter=None, *args, **kw):
        "Inline edit short object"
        selectedFormat = format or self.getConfig('selectedFormat')
        where = self.allowedFormats[selectedFormat]['where']
        if where == 'Local':
            return self.dateClearButton() + self.editFormattedDate(selectedFormat,yearsBefore, yearsAfter)
        return self.input_date('data', self.editFormattedDate(selectedFormat,yearsBefore, yearsAfter))

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        if 'clear' in dict:
            self.clearDateTime()
            return
        dateString = ''
        
        date = dict.pop('date', None)
        if date is not None:
            dateString = self.getDateString(date)
        
        data = dict.pop('data', None)
        if data is not None:
            dateString = data
        if dateString:
            self.setDate(dateString)

    security.declareProtected('Change CompoundDoc', 'clearDateTime')
    def clearDateTime(self):
        "clear the DateTime object"
        if self.getConfig('enableDateClearing'):
            self.setObject('data', "")

    security.declareProtected('Change CompoundDoc', 'setDate')
    def setDate(self, date):
        "set the DateTime object"
        try:
            data = DateTime.DateTime(date)
        except:
            data =  ""
        self.setObject('data', data)
            
    security.declareProtected('Change CompoundDoc', 'store')        
    store = setDate

    security.declareProtected('Change CompoundDoc', 'resetDate')
    def resetDate(self):
        "reset the DateTime object if possible"
        date = self.getInitialDate()
        self.setObject('data',date)

    security.declarePrivate('getDateString')
    def getDateString(self, dropDownDict):
        "from the dropdownDict we have on editing turn it into a date string"
        year = dropDownDict.get('year', '')
        month = dropDownDict.get('month', '')
        day = dropDownDict.get('day', '')
        hour = dropDownDict.get('hour', '')
        minute1 = dropDownDict.get('minute1', '')
        minute2 = dropDownDict.get('minute2', '')
        ampm = dropDownDict.get('ampm', '')
        date = '%s %s %s' % (year, month, day)
        time = ''
        if hour and minute1 and minute2:
            time = ' %s:%s%s %s ' % (hour, minute1, minute2, ampm)

        if year and month and day:
            return date + time

    security.declarePrivate('instance')
    instance = (('data',('call', 'getInitialDate')),)

    security.declareProtected('Access contents information', 'getInitialDate')
    def getInitialDate(self):
        "get the initial start date for this object"
        scriptPath = self.getConfig('scriptPath')
        if scriptPath:
            script = self.getCompoundDocContainer().restrictedTraverse(scriptPath, None)
            if script is not None:
                return self.changeCallingContext(script)()
        attributeNameForCustomCreation = self.getConfig('attributeNameForCustomCreation')
        if attributeNameForCustomCreation:
            result = getattr(self, attributeNameForCustomCreation)()
            if result:
                return DateTime.DateTime(result)
        return DateTime.DateTime()

    security.declareProtected('Access contents information', 'Date')
    def Date(self):
        "return the date object for this object"
        object = self.data
        if hasattr(object, 'Date'):
            return object
        
    security.declarePrivate('editFormattedDate')
    def editFormattedDate(self, selectedFormat = None, yearOffSetBefore=None, yearOffSetAfter=None):
        "get the date formatted the way we are going to edit it"
        date = self.Date()
        where = self.allowedFormats[selectedFormat]['where']
        if selectedFormat:
            if date and where == 'DateTime':
                date = getattr(date, selectedFormat)()
            elif where == 'Local':
                yearOffSetBefore = yearOffSetBefore or self.getConfig('yearOffSetBefore')
                yearOffSetAfter = yearOffSetAfter or self.getConfig('yearOffSetAfter')
                date = getattr(self, selectedFormat)(yearOffSetBefore, yearOffSetAfter)
        elif date is None:
            date = ''
        else:
            date = str(date)
        return date

    security.declarePrivate('getDate')
    def getDate(self):
        "Return the date object if possible as a string"
        date = self.Date()
        if date:
            return str(date)
        return ""

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return self.Date()

    security.declarePrivate('populatorInformation')
    def populatorInformation(self):
        "return a string that this metods pair can read back to load data in this object"
        return self.getDate()

    security.declarePrivate('populatorLoader')
    def populatorLoader(self, string):
        "load the data into this object if it matches me"
        try:
            if string:
                self.setObject('data',DateTime.DateTime(string))
        except ValueError:
            pass

Globals.InitializeClass(Date)
import register
register.registerClass(Date)
