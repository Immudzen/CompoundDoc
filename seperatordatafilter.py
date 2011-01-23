# -*- coding: utf-8 -*-
import datafilter

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import StringIO
import csv
import urllib

class SeperatorDataFilter(datafilter.DataFilter):
    "HTMLDataFilter apply this to an a list of dicts to make it output a table"

    meta_type = "SeperatorDataFilter"
    security = ClassSecurityInfo()
    seperator = ','
    security.declareObjectProtected('View management screens')

    security.declarePrivate('customEdit')
    def customEdit(self):
        "This is an edit piece that can be overridden by various custom editing features needed by other filters"
        temp = []
        #format = '<label>%(name)s %(form)s</label><br>\n'
        format = '<p>%(name)s %(form)s</p>\n'
        temp.append(format  % {'name':'Seperator', 'form':self.input_text('seperator', self.seperator)})
        return ''.join(temp)

    security.declareProtected('View', 'view')
    def view(self, header=1):
        "Give links to the different formats for csv"
        seq = []
        format = '''<tr><td>%(os)s File format version</td>
                        <td><a href="%(url)s/%(record)s?%(query)s">%(record)s</a></td>
                        <td><a href="%(url)s/%(archive)s?%(query)s">%(archive)s</a></td></tr>'''
        query = urllib.urlencode({'header:int':header})
        url = self.absolute_url_path()
        seq.append('<table>')
        seq.append(format % {'os':'Unix', 'record':'unix', 'archive':'unixArchive', 'query':query, 'url':url})
        seq.append(format % {'os':'Windows', 'record':'windows', 'archive':'windowsArchive', 'query':query, 'url':url})
        seq.append(format % {'os':'Mac', 'record':'mac', 'archive':'macArchive', 'query':query, 'url':url})
        seq.append('</table>')
        return ''.join(seq)

    security.declareProtected('View management screens', 'windows')
    def windows(self, order=None, start=None, stop=None, header=1, query=None, filename="windows.csv"):
        "windows version of csv format"
        return self.render(eol='\r\n', order=order, start=start, stop=stop, header=header, query=query, filename=filename)

    security.declareProtected('View management screens', 'mac')
    def mac(self, order=None, start=None, stop=None, header=1, query=None, filename="mac.csv"):
        "mac version of csv format"
        return self.render(eol='\r', order=order, start=start, stop=stop, header=header, query=query, filename=filename)

    security.declareProtected('View management screens', 'unix')
    def unix(self, order=None, start=None, stop=None, header=1, query=None, filename="unix.csv"):
        "unix version of csv format"
        return self.render(order=order, start=start, stop=stop, header=header, query=query, filename=filename)

    security.declareProtected('View management screens', 'windowsArchive')
    def windowsArchive(self, order=None, start=None, stop=None, header=1, query=None, filename="windowsArchive.csv"):
        "windows version of csv format"
        return self.render(eol='\r\n', archive=1, order=order, start=start, stop=stop, header=header, query=query, filename=filename)

    security.declareProtected('View management screens', 'macArchive')
    def macArchive(self, order=None, start=None, stop=None, header=1, query=None, filename="macArchive.csv"):
        "mac version of csv format"
        return self.render(eol='\r', archive=1, order=order, start=start, stop=stop, header=header, query=query, filename=filename)

    security.declareProtected('View management screens', 'unixArchive')
    def unixArchive(self, order=None, start=None, stop=None, header=1, query=None, filename="unixArchive.csv"):
        "unix version of csv format"
        return self.render(archive=1, order=order, start=start, stop=stop, header=header, query=query, filename=filename)
        
    security.declareProtected('View management screens', 'windowsMerge')
    def windowsMerge(self, order=None, start=None, stop=None, header=1, query=None, filename="windowsMerge.csv"):
        "windows version of csv format"
        return self.render(eol='\r\n', order=order, start=start, stop=stop, header=header, query=query, filename=filename, merge=1)

    security.declareProtected('View management screens', 'macMerge')
    def macMerge(self, order=None, start=None, stop=None, header=1, query=None, filename="macMerge.csv"):
        "mac version of csv format"
        return self.render(eol='\r', order=order, start=start, stop=stop, header=header, query=query, filename=filename, merge=1)

    security.declareProtected('View management screens', 'unixMerge')
    def unixMerge(self, order=None, start=None, stop=None, header=1, query=None, filename="unixMerge.csv"):
        "unix version of csv format"
        return self.render(order=order, start=start, stop=stop, header=header, query=query, filename=filename, merge=1)

    security.declarePrivate('render')
    def render(self, order=None, eol="\n", archive=None, start=None, stop=None, header=None, query=None, merge=None, filename=''):
        "Inline draw view"
        self.REQUEST.RESPONSE.setHeader('Content-Disposition' , 'attachment; filename="%s"' % filename)
        self.REQUEST.RESPONSE.setHeader('Content-Type',"text/x-csv")

        sep = self.seperator
        
        if order is None:
            order = self.getFieldOrder()
            
        records = self.getDataRecords(order, archive=archive, start=start, stop=stop, header=header, query=query, merge=merge)
        writer = csv.writer(self.REQUEST.RESPONSE, lineterminator=eol, delimiter=sep)
        writer.writerows(records)

        if not self.REQUEST.RESPONSE._wrote:
            self.REQUEST.RESPONSE.write('No Drawable Data Found' + eol)

Globals.InitializeClass(SeperatorDataFilter)
import register
register.registerClass(SeperatorDataFilter)