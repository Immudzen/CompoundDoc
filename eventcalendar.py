# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
import calendar
from DateTime import DateTime
import zExceptions

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject
import utility

class EventCalendar(UserObject):
    "Calendar object"
    security = ClassSecurityInfo()
    meta_type = "EventCalendar"

    catalogPath = ''
    cdocProfiles = None
    dateField = ''
    pathRestriction = ''
    profileMapping = None
    showNamedMonth = 0
    disableControls = 0
    startDay = calendar.day_name[0]
    showDays = None
    showControlsOnCalendar = 1
    extendedQuery = ''
    yearRange = 5
    renderScript = ''
    
    days = {}
    for dayValue, dayName in enumerate(calendar.day_name):
        days[dayName] = dayValue
    
    classConfig = {}
    classConfig['showNamedMonth'] = {'name':'Show a specified Month (If No it shows the current time)', 'type': 'radio'}
    classConfig['disableControls'] = {'name':'Disable navigation controls', 'type': 'radio'}
    classConfig['showControlsOnCalendar'] = {'name':'Show Navigation Controls on the Calendar', 'type': 'radio'}
    classConfig['startDay'] = {'name':'First Day Of Week', 'type':'list', 'values': list(calendar.day_name)}
    classConfig['catalogPath'] = {'name':'Path to the Catalog to search', 'type':'string'}
    classConfig['dateField'] = {'name':'Fieldname for the date object', 'type':'string'}
    classConfig['pathRestriction'] = {'name':'Path restriction for objects', 'type':'string'}
    classConfig['showDays'] = {'name':'Which Days to Show?', 'type':'multiple', 'values': list(calendar.day_name), 'size':7}
    classConfig['extendedQuery'] = {'name':'Name of attribute for extended query', 'type':'string'}
    classConfig['yearRange'] = {'name':'Max number of years on either side of now?', 'type':'int'}
    classConfig['renderScript'] = {'name':'Path to rendering script?', 'type':'path'}
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        temp.append(self.editSingleConfig('catalogPath'))
        temp.append(self.editSingleConfig('dateField'))
        temp.append(self.editSingleConfig('pathRestriction'))
        temp.append(self.editSingleConfig('disableControls'))
        temp.append(self.editSingleConfig('showControlsOnCalendar'))
        temp.append(self.editSingleConfig('showNamedMonth'))
        temp.append(self.editSingleConfig('startDay'))
        temp.append(self.editSingleConfig('showDays'))
        temp.append(self.editSingleConfig('extendedQuery'))
        temp.append('<p>Starting Month if set not to use the current time:%s</p>' % self.startThisMonth.edit())
        temp.append('''<p>For the string formatting version the following variables are available.
          id,title,title_or_id and the url to the object.</p>''')
        temp.append(self.drawProfileOutputs())
        available = [''] + list(self.getPhysicalRoot().CDocUpgrader.uniqueValuesFor('profile'))
        output = '<p>%s currently selected profiles.</p><p>What profiles do you want? <br> %s</p>'
        
        profiles = self.getSelectedProfiles()
        
        temp.append(output % (len(profiles),
          self.multiselect('cdocProfiles', available, profiles, size=10)))
        return ''.join(temp)

    def drawProfileOutputs(self):
        "draw the edit screens needed to specify the outputs for the profiles we have"
        temp = []
        typeformat = '<div>%s Display: %s Formatted String:%s</div>'
        profileMapping = self.getProfileMapping()
        profiles = sorted(self.getSelectedProfiles())
        for profile in profiles:
            try:
                displayValue = profileMapping[profile]['display']
                formattedStringValue = profileMapping[profile]['formattedString']
            except (IndexError,KeyError):
                formattedStringValue = ''
                displayValue = ''

            temp.append(typeformat % (profile, self.input_text('display', displayValue, containers=('profileMapping',profile)),
              self.input_text('formattedString', formattedStringValue,  containers=('profileMapping',profile))))
        return ''.join(temp)

    security.declarePrivate('getProfileMapping')
    def getProfileMapping(self):
        "get the ProfileMapping dictionary structure"
        if self.profileMapping is not None:
            return self.profileMapping
        return {}

    security.declarePrivate('getSelectedProfiles')
    def getSelectedProfiles(self):
        "get the selected profiles"
        if self.cdocProfiles is not None:
            return self.cdocProfiles
        return []

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, dict):
        "Process edits."
        cdocProfiles = dict.pop('cdocProfiles', None)
        if cdocProfiles is not None:
            if not len(cdocProfiles):
                cdocProfiles = None
            self.setObject('cdocProfiles',cdocProfiles)

        profileMapping = dict.pop('profilePopping', None)
        if profileMapping is not None:
            temp = {}
            for profile,data in profileMapping.items():
                display = data.get('display','')
                formattedString = data.get('formattedString','')
                temp[profile] = {'display':display.strip()[0:50],'formattedString':formattedString.strip()[0:100]}
            if not len(temp):
                temp = None
            self.setObject('profileMapping',temp)

    security.declarePrivate('instance')
    instance = (('startThisMonth',('create', 'Date')),)

    security.declareProtected('View', 'view')
    def view(self, catalogQuery=None):
        "Inline draw view"
        month,year = self.getSelectedMonthYear()
        calendar.setfirstweekday(self.days[self.startDay])
        try:
            cal = calendar.monthcalendar(year,month)
        except OverflowError:
            month,year = self.getCurrentMonthYear()
            cal = calendar.monthcalendar(year,month)
        monthNext,monthNextYear = self.calculateNextMonth(year,month)

        start,end = self.getStartAndEndTimes(year,month,monthNextYear, monthNext)
        events = self.getEventsBetween(start,end, catalogQuery)
        cal = self.fillCalendarWithEvents(cal,events)
        days = self.getDays()
        cal.insert(0, self.getDays())
        if len(days) == 7 and self.showControlsOnCalendar:
            c = self.getNavigationControls()
            cal.insert(0, [c['prevYear'],c['prevMonth'],c['monthName'],year,'',c['nextMonth'],c['nextYear']])
        return self.createTable(cal)

    security.declareProtected('View', 'getNavigationControls')
    def getNavigationControls(self):
        "get the navigation controls as a dictionary that can be used to create navigation for the calendar"
        month,year = self.getSelectedMonthYear()
        monthNext,monthNextYear = self.calculateNextMonth(year,month)
        monthPrevious,monthPreviousYear = self.calculatePreviousMonth(year,month)
        nextMonth = self.renderNextMonthControl(monthNext,monthNextYear)
        prevMonth = self.renderPreviousMonthControl(monthPreviousYear,monthPrevious)
        prevYear, nextYear = self.renderNextPrevYearControls(month,year)
        controls = {}
        controls['month'] = month
        controls['year'] = year
        controls['nextMonth'] = nextMonth
        controls['nextYear'] =  nextYear
        controls['prevMonth'] = prevMonth
        controls['prevYear'] = prevYear
        controls['monthName'] = calendar.month_name[month]
        return controls
        
    security.declareProtected('View', 'drawBasicNavigationControls')
    def drawBasicNavigationControls(self):
        "draw some very basic navigation controls for the calendar"
        controls = self.getNavigationControls()
        format = """<p>%(prevYear)s &nbsp; %(prevMonth)s &nbsp;
        %(monthName)s &nbsp; %(year)s &nbsp;
        %(nextMonth)s &nbsp; %(nextYear)s &nbsp;
        </p>"""
        return format % controls
    
    def getDaysOrder(self):
        "get the day names in the order we will be using them based on the start day"
        start = self.days[self.startDay]
        days = list(calendar.day_name)
        return days[start:] + days[:start]  #set the days the same as our start day    
        
    def getDays(self):
        "get the day names for this week"
        days = self.getDaysOrder()
        showDays = self.showDays
        if showDays is None or len(showDays) == 7:
            return days
        else:
            return [day for day in days if day in showDays]
        
    def getStartAndEndTimes(self,year,month,monthNextYear,monthNext):
        "return the start and end times that we will search over"
        start = DateTime('%s %s %s' % (year, month, 1)).earliestTime()
        #To find the endpoint we find the first day of the next month, go back one day and find
        #the Latest time that takes place on that day
        end = DateTime('%s %s %s' % (monthNextYear,monthNext, 1)) -1
        end = end.latestTime()
        return start,end

    def getEventsBetween(self,start,end, catalogQuery=None):
        "get all the events that fall between start and end and return them as a dict keyed by integer day"
        catalog = self.getCatalog()
        events = {}
        if catalog is not None:
            query = {}
            query['profile'] = self.getSelectedProfiles()
            query['path'] = self.pathRestriction
            if self.extendedQuery:
                extendedQuery = self.getCompoundDoc().restrictedTraverse(self.extendedQuery, None)
                if extendedQuery is not None:
                    query.update(extendedQuery())
            if catalogQuery is not None:
                query.update(catalogQuery)

            query[self.dateField] = {'query':[start,end], 'range':'minmax'}
            
            for record in catalog(query, sort_on=self.dateField):
                try:
                    cdoc = record.getObject()
                    if cdoc is not None:
                        dateField = getattr(cdoc, self.dateField)
                        try:
                            day = dateField.Date().day()
                        except AttributeError:
                            day = dateField.day()
                        if not day in events:
                            events[day] = []
                        events[day].append(cdoc)
                except (zExceptions.Unauthorized, zExceptions.NotFound, KeyError):
                    pass
            
        return events

    def getCatalog(self):
        "return the selected catalog or None if we can't get to it for some reason"
        if self.catalogPath:
            return self.restrictedTraverse(self.catalogPath,None)
        return None

    def getSelectedMonthYear(self):
        "Get the selected month and year"
        month = None
        year = None
        currentMonth, currentYear =  self.getCurrentMonthYear()
        yearRange = self.yearRange
        if self.showNamedMonth and (self.disableControls or not self.REQUEST.form):
            date = self.startThisMonth.Date()
            try:
                month,year = date.month(),date.year()
            except AttributeError:
                pass
        if self.REQUEST.form and not self.disableControls:
            month = self.REQUEST.form.get('month',None)
            if month > 12 or month < 1:
                month = None
            year = self.REQUEST.form.get('year',None)
            if year > (currentYear + yearRange) or year < (currentYear - yearRange):
                year = None
        if month is None or year is None:
            month,year = currentMonth, currentYear
        return month,year

    def getCurrentMonthYear(self):
        "get the current month and year"
        time = self.ZopeTime()
        return time.month(), time.year()

    security.declarePrivate('calculatePreviousMonth')
    def calculatePreviousMonth(self,year,month):
        "calculate the control fields needed for the calander for previous movement"
        monthPrevious = month -1
        monthPreviousYear = year
        if monthPrevious < 1:
            monthPrevious = 12
            monthPreviousYear = year -1
        return monthPrevious,monthPreviousYear

    security.declarePrivate('calculateNextMonth')
    def calculateNextMonth(self,year,month):
        "calculate the next year and month"
        monthNext = month + 1
        monthNextYear = year
        if monthNext > 12:
            monthNext = 1
            monthNextYear = year +1
        return monthNext,monthNextYear

    security.declarePrivate('renderNextMonthControl')
    def renderNextMonthControl(self, monthNext,monthNextYear):
        "render the urls needed for next and previous year and month"
        format = '<a href="%s?%s">%s</a>'
        currentUrl = self.REQUEST.URL
        queryString = self.REQUEST.environ.get('QUERY_STRING', '')
        query = utility.updateQueryString(queryString, {'year:int': monthNextYear, 'month:int':monthNext})
        return format % (currentUrl,query,'&gt;')

    security.declarePrivate('renderPreviousMonthControl')
    def renderPreviousMonthControl(self, monthPreviousYear,monthPrevious):
        "render the urls needed for next and previous year and month"
        format = '<a href="%s?%s">%s</a>'
        currentUrl = self.REQUEST.URL
        queryString = self.REQUEST.environ.get('QUERY_STRING', '')
        query = utility.updateQueryString(queryString, {'year:int': monthPreviousYear, 'month:int':monthPrevious})
        return format % (currentUrl,query,'&lt;')

    security.declarePrivate('renderNextPrevYearControls')
    def renderNextPrevYearControls(self, month,year):
        "render the urls needed for next and previous years"
        format = '<a href="%s?%s">%s</a>'
        currentUrl = self.REQUEST.URL
        queryString = self.REQUEST.environ.get('QUERY_STRING', '')
        
        query = utility.updateQueryString(queryString, {'year:int': year+1, 'month:int':month})
        nextYear = format % (currentUrl,query,'&gt;&gt;')
        
        query = utility.updateQueryString(queryString, {'year:int': year-1, 'month:int':month})
        prevYear = format % (currentUrl,query,'&lt;&lt;')
        return prevYear,nextYear

    security.declarePrivate('fillCalendarWithEvents')
    def fillCalendarWithEvents(self, cal, events):
        "fill this calendar object with the events"
        temp = []
        cal = self.trimCalendar(cal)
        for week in cal:
            temp.append([self.createCalEntry(day,events) for day in week])
        return temp

    security.declarePrivate('trimCalendar')
    def trimCalendar(self, cal):
        "trim this calendar to only have the days we are supposed to show"
        days = self.getDays()
        if len(days) == 7:
            return cal
        dayOrder = self.getDaysOrder()
        keepDays = [dayOrder.index(day) for day in days]
        
        newcal = []
        for week in cal:
            newweek = []
            for i in keepDays:
                newweek.append(week[i])
            if self.daysInWeek(newweek):
                newcal.append(newweek)
        return newcal    

    security.declarePrivate('daysInWeek')
    def daysInWeek(self, week):
        "check if there are any valid days in this week"
        for i in week:
            if i:
                return True
        return False
                
                    
    security.declarePrivate('createCalEntry')
    def createCalEntry(self, day,events):
        "make an entry"
        if day in events:
            day = '%s %s' % (day, ''.join([self.drawEvent(event) for event in events[day]]))
        if day == 0:
            day = ''
        return day

    def drawEvent(self,event):
        "Draw this event object"
        profile = event.profile
        renderProfile = self.getProfileMapping().get(profile,None)
        if renderProfile is not None:
            display = renderProfile['display']
            formattedString = renderProfile['formattedString']
            if display:
                return event.render(name=display)
            elif formattedString:
                lookup = {'url':event.absolute_url_path(), 'title_or_id':event.title_or_id(),
                  'title':event.title(),'id':event.getId()}
                return formattedString % lookup
        elif self.renderScript:
            script = self.getCompoundDocContainer().restrictedTraverse(self.renderScript, None)
            if script is not None:
                return script(event)
        return '<br><a href="%(url)s">%(title_or_id)s</a>' % {'url':event.absolute_url_path(),
            'title_or_id':event.title_or_id()}

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        #ERROR: Do no currently index this object becuse it causes changes saved to break
        return ''
    
Globals.InitializeClass(EventCalendar)
import register
register.registerClass(EventCalendar)
