###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#For Security control and init

def option_select(seq, name, selected=None, multiple=None, size=None, dataType='string', events = ''):
    "Create option select box fields"
    if not seq and selected is None:
        return ''

    if selected is not None:
        selected = set(selected)
    else:
        selected = set()

    formMultiple = ''
    if multiple:
        dataType="list"
        formMultiple = 'multiple="multiple"'

    if dataType is None:
        formName = name
    else:
        formName = "%s:%s"  % (name, dataType)
    
    formSize = ''
    if size:
        formSize = 'size="%s"' % size
    temp = ['<select name="%s" %s %s %s>' % (formName, formMultiple, formSize, events)]

    format = '<option value="%s" %s>%s</option>'
    options = []
    for name,printableName in generateOptionSelectFormat(seq, selected.copy()):
        if name in selected:
            options.append(format % (name, 'selected="selected"', printableName))
        else:
            options.append(format % (name, '', printableName))
    if not options:
        return ''
    temp.extend(options)
    temp.append('</select>')
    return ''.join(temp)

def generateOptionSelectFormat(seq, selected):
    "generate the format needed by the option_select renderer from this sequence"
    #all items in the sequence must have the same number of elements
    #we need to merge in the currently selected items also if they are in in the sequence and mark them someway
    #we also throw away duplicates of stuff we have already processed if two items would end up with the same
    #form name the ones after the first are thrown away. This also preserves order
    seen = []
    for i in seq:
        if isinstance(i, basestring):
            first = second = i
        else:
            try:
                first,second = i
            except (TypeError, ValueError):
                first = second = i
        if first in selected:
            selected.remove(first)
        if first not in seen:
            seen.append(first)
            yield first,second
    if selected:
        for i in selected:
            if i is not None:
                first = second = i
                second = '%s NOT FOUND' % second
                yield first,second