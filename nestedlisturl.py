# -*- coding: utf-8 -*-
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import types
import base
import urllib

import utility

def createQuery(queryDict):
    "create a query from this queryDict"
    query = '' 
    if queryDict:
        query = urllib.urlencode(queryDict)
    if query:
        query = '?' + query
    return query

def drawNestedList(seq, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>', 
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    length = len(seq)
    if not length:
        return ''
    position = 1
    for index,item in enumerate(seq):
        if isinstance(item, types.TupleType):
            temp.append('<li>')
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.append(format[selected] % (url,query, position, cssClasses, otherAttributes, link))
            position += 1
        elif isinstance(item, types.StringType):
            temp.append('<li>')
            temp.append(item)
            position += 1
        else:
            temp.append(drawNestedList(item, containerClasses))
        if index < (length-1) and isinstance(seq[index+1], (types.TupleType, types.StringType)):
            temp.append('</li>')

    if temp[len(temp)-1] != '</li>' and temp[0] == '<li>':
        temp.append('</li>')
    temp = ''.join(temp)
    if temp:
        return '<ul class="%s">%s</ul>\n' % (containerClasses, temp)
    return ''

def drawNestedListHorizontal(seq, level=1, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>', 
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    end = []
    if not len(seq):
        return ''
    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.append(format[selected] % (url,query, position, cssClasses, otherAttributes, link))
            position += 1
        elif isinstance(item, types.StringType):
            temp.append(item)
            position += 1
        else:
            end.append(drawNestedListHorizontal(item, level+1, containerClasses))

    temp = '\n'.join(temp)
    if temp:
        temp = '<div class="level%s %s">%s</div>\n' % (level, containerClasses, temp)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def drawNestedListHorizontalSpan(seq, level=1, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    spanBegin = '<span>'
    spanEnd = '</span>'
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>', 
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    end = []
    if not len(seq):
        return ''
    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.extend([spanBegin, format[selected] % (url,query, position, cssClasses, otherAttributes, link), spanEnd])
            position += 1
        elif isinstance(item, types.StringType):
            temp.extend([spanBegin, item, spanEnd])
            position += 1
        else:
            end.append(drawNestedListHorizontalSpan(item, level+1, containerClasses))

    temp = '\n'.join(temp)
    if temp:
        temp = '<div class="level%s %s">%s</div>\n' % (level, containerClasses, temp)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def roundedCorners(seq, level=1, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    divBegin = '<div class="item%s"><div class="head"><div class="c"></div></div><div class="body"><div class="c">'
    divEnd = '</div></div><div class="foot"><div class="c"></div></div></div>'
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>',
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    end = []
    if not len(seq):
        return ''
    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.extend([divBegin % position, format[selected] % (url,query, position, cssClasses, otherAttributes, link), divEnd])
            position += 1
        elif isinstance(item, types.StringType):
            temp.extend([divBegin % position, item, divEnd])
            position += 1
        else:
            end.append(roundedCorners(item, level+1, containerClasses))

    temp = '\n'.join(temp)
    if temp:
        temp = '<div class="level%s %s">%s</div>\n' % (level, containerClasses, temp)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def roundedCornersTable(seq, level=1, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    tableBegin = '''<table class="item%s"><tr><td class="topLeft">&nbsp;</td><td class="topCenter">&nbsp;</td><td class="topRight">&nbsp;</td></tr>
    <tr><td class="middleLeft">&nbsp;</td><td class="middleContent">'''
    tableEnd = '''</td><td class="middleRight">&nbsp;</td></tr>
    <tr><td class="bottomLeft">&nbsp;</td><td class="bottomCenter">&nbsp;</td><td class="bottomRight">&nbsp;</td></tr></table>'''
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>',
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']

    temp = []
    end = []
    if not len(seq):
        return ''
    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.extend([tableBegin % position, format[selected] % (url,query, position, cssClasses, otherAttributes, link), tableEnd])
            position += 1
        elif isinstance(item, types.StringType):
            temp.extend([tableBegin % position, item, tableEnd])
            position += 1
        else:
            end.append(roundedCornersTable(item, level+1, containerClasses))

    temp = '\n'.join(temp)
    if temp:
        temp = '<div class="level%s %s">%s</div>\n' % (level, containerClasses, temp)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def drawNestedListTable(seq, level=1, columns=None, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>', 
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    end = []
    if columns == 0:
        columns = 3
    if not len(seq):
        return ''
    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.append(format[selected] % (url,query,position, cssClasses, otherAttributes, link))
            position += 1
        elif isinstance(item, types.StringType):
            temp.append(item)
            position += 1
        else:
            end.append(drawNestedListTable(item, level+1, columns, containerClasses))

    if temp:
        temp = utility.formatListForTable(temp, columns, '')
        output = ['<table class="level%s %s">' % (level, containerClasses)]
        for row in temp:
            output.append('<tr>')
            output.extend(['<td>%s</td>' % item for item in row])
            output.append('</tr>')
        output.append('</table>\n')
        temp = ''.join(output)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def drawRoundedTableGrid(seq, level=1, columns=None, containerClasses='', **kw):
    "draw the nested list object and render it to a string"
    topRow = '<td class="topLeft">&nbsp;</td><td class="topCenter">&nbsp;</td><td class="topRight">&nbsp;</td>'
    middleRow = '<td class="middleLeft">&nbsp;</td><td class="middleContent">%s</td><td class="middleRight">&nbsp;</td>'
    bottomRow = '<td class="bottomLeft">&nbsp;</td><td class="bottomCenter">&nbsp;</td><td class="bottomRight">&nbsp;</td>'
    
    format = ['<a href="%s%s" class="item%s %s" %s>%s</a>', 
              '<a href="%s%s" class="highLight item%s %s" %s>%s</a>']
    temp = []
    end = []
    if columns == 0:
        columns = 3
    
    topRow = '<tr>' + topRow * columns + '</tr>'
    middleRow ='<tr>' +  middleRow * columns + '</tr>'
    bottomRow = '<tr>' + bottomRow * columns + '</tr>'
        
    if not len(seq):
        return ''

    position = 1
    for item in seq:
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.append(format[selected] % (url,query,position, cssClasses, otherAttributes, link))
            position += 1
        elif isinstance(item, types.StringType):
            temp.append(item)
            position += 1
        else:
            end.append(drawRoundedTableGrid(item, level+1, columns, containerClasses))

    if temp:
        temp = utility.formatListForTable(temp, columns, '')
        output = ['<table class="level%s %s">' % (level, containerClasses)]
        for row in temp:
            output.append(topRow)
            output.extend(middleRow % row)
            output.append(bottomRow)
        output.append('</table>\n')
        temp = ''.join(output)
        if end:
            temp += '\n'.join(end)
        return temp
    return ''

def drawDropDown(seq, **kw):
    "draw the nested list object and render it to a string"
    format = ['<option value="%s%s" class="item%s %s" %s>%s</option>', 
              '<option value="%s%s" selected="selected" class="item%s %s" %s>%s</option>']
    temp = []
    
    if not len(seq):
        return ''
    for index,item in enumerate(seq):
        if isinstance(item, types.TupleType):
            url,link,selected,cssClasses,queryDict,otherAttributes = item
                
            query = createQuery(queryDict)
            temp.append(format[selected] % (url, query, index, cssClasses, otherAttributes, link))
    
    temp = ''.join(temp)
    if temp:
        return '<div><select onchange="window.location = this.value;">%s</select></div>\n' % temp
    return ''

def doNothing(self):
    "do nothing at all"
    return ''

def editTableRenderer(self):
    'edit the table renderer'
    return '<p>Number of Columns: %s</p>' % self.input_number('columns', self.columns)

lookup = {'Vertical': drawNestedList, 'Horizontal':drawNestedListHorizontal, 'Table':drawNestedListTable,
    'DropDown':drawDropDown, 'Horizontal Span':drawNestedListHorizontalSpan, 'Rounded':roundedCorners, 
    'Rounded Table':roundedCornersTable, 'Rounded Table Grid':drawRoundedTableGrid}
editLookup = {'Vertical': doNothing, 'Horizontal':doNothing, 'Table':editTableRenderer, 'DropDown':doNothing, 
    'Horizontal Span':doNothing, 'Rounded':doNothing, 'Rounded Table':doNothing, 'Rounded Table Grid':editTableRenderer}

additionalVars = {'columns': 0}

def listRenderer(format,seq, columns, containerClasses=''):
    "run the renderer that matches this format"
    return lookup[format](seq,columns=columns, containerClasses=containerClasses)

def editRenderer(format, self):
    "return something to edit this renderer if needed"
    return editLookup[format](self)

class NestedListURL(base.Base):
    "this is a nested url object based on a list construct"
    meta_type = "NestedListURL"
