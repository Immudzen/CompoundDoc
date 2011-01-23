# -*- coding: utf-8 -*-
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from formoutputfilter import FormOutputFilter

import basewidget
import utility

class Widgets:
    "This is the widget class"

    security = ClassSecurityInfo()

    security.declarePrivate('getClasses')
    def getClasses(self, name, meta_type):
        "get the classes that should be used for this form element"
        return set([self.getId(), meta_type, name])

    security.declarePrivate('input_text')
    def input_text(self, name, var="", containers=None,  cssClass=''):
        "Create input text fields"
        return self.input_line(name, 'string', var, containers, cssClass=cssClass)

    security.declarePrivate('input_hidden')
    def input_hidden(self, name, var="", containers=None):
        "Create hidden input field"
        return self.input_line(name, 'string', var, containers, "hidden")

    security.declarePrivate('input_number')
    def input_number(self, name, var="", containers=None):
        "Create a number input field"
        return self.input_line(name, 'int', str(var), containers)

    security.declarePrivate('input_float')
    def input_float(self, name, var="", containers=None):
        "Create a number input field"
        return self.input_line(name, 'float', str(var), containers)

    security.declarePrivate('input_date')
    def input_date(self, name, var="", containers=None, pageId=None):
        "Create a Date input field"
        return self.input_line(name, 'string', var, containers, pageId=pageId)

    security.declarePrivate('input_tokens')
    def input_tokens(self, name, var=None, containers=None):
        "Create a Tokens input field"
        if var is None:
            var = []
        var = ' '.join(var)
        return self.input_line(name, 'tokens', var, containers)

    security.declarePrivate('input_line')
    def input_line(self, name, type, var="", containers=None, formType="text",  cssClass='', pageId=None):
        "Input a single line of type"
        pageId = 'id="%s"' % pageId if pageId is not None else ''
        format = '<input type="%s" name="%s" value="%s" class="%s %s" %s>'
        formName = self.formName(name, type, containers)
        meta_type = getattr(self, 'meta_type', '')
        cleanData = self.convertForEdit(var)
        classes = ' '.join(self.getClasses(name, meta_type))
        return format % (formType, formName, cleanData, classes,  cssClass, pageId)

    security.declarePrivate('option_select')
    def option_select(self, seq, name, selected=None, multiple=None, size=None, containers=None, dataType='string', events = ''):
        "Create option select box fields"
        try:
            formName = self.formName(name, dataType, containers=containers)
        except AttributeError:
            formName = "%s:%s"  % (name, dataType)
        
        return basewidget.option_select(seq, formName, selected, multiple, size, None, events)

    security.declarePrivate('true_false')
    def true_false(self, name, var, prefix=1, containers=None):
        "True false checkbox"
        if name[-2:] == "_p":
            title = name[0:-2]
        else:
            title = name

        if not prefix:
            title = ""
        else:
            title = "%s : " % title

        formVar =  self.formName(name, 'int', containers=containers)
        classes = ' '.join(self.getClasses(name, 'radio'))
        cssClass = 'class="%s"' % classes
        temp = '''%s<input type="radio" %s name="%s" value="1" %s>Y<input type="radio"  %s name="%s" value="0" %s>N\n'''
        if var == 1:
            return temp % (title, 'checked="checked"', formVar, cssClass, "", formVar, cssClass)
        else:
            return temp % (title, '', formVar, cssClass, 'checked="checked"', formVar, cssClass)

    security.declarePrivate('text_area')
    def text_area(self, name, var="", containers=None, formType="text"):
        "TextArea field base widget type"
        format = '<textarea name="%s" rows="10" cols="40" class="%s">%s</textarea>'
        return format % (self.formName(name, formType, containers=containers),
          self.getId(),self.convertForEdit(var))

    security.declarePrivate('radio_box')
    def radio_box(self, name, value, containers=None, enableDefault=0):
        "Radio box"
        classes = ' '.join(self.getClasses(name, 'radio'))
        cssClass = 'class="%s"' % classes
        format = '<input type="%s" %s name="%s" value="%s" %s>'
        formname = str(self.formName(name, 'int', containers=containers))
        checkbox = 'checkbox'
        hidden = 'hidden'
        if value:
            temp = format % (checkbox, 'checked="checked"', formname, '1', cssClass)
            if enableDefault:
                return temp + format % (hidden, '', formname+':default', '0', cssClass)
            return temp
        else:
            return format % (checkbox, '', formname, '1', cssClass)

    security.declarePrivate('combo_box')
    def combo_box(self, seq, name, selected, containers=None):
        "Radio box"
        classes = ' '.join(self.getClasses(name, 'radio'))
        cssClass = 'class="%s"' % classes
        format = '<input type="checkbox" %s name="%s" value="%s" %s>'
        formname = self.formName(name, 'list:string', containers=containers)
        temp = []
        for i in seq:
            if i in selected:
                temp.append(format % ('checked="checked"', formname, i, cssClass))
            else:
                temp.append(format % ('', formname, i, cssClass))
        temp.append('<input type="hidden" name="%s:default" value="" >' % (formname))
        return ''.join(temp)

    security.declarePrivate('checkbox_inline')
    def checkbox_inline(self, seq, name, selected, containers=None):
        "checkbox"
        format = '<label><input type="checkbox" %s name="%s" value="%s" %s>%s</label>'
        formType = 'checkbox'
        return self.selection_box(seq, name, selected, format, formType, containers)

    security.declarePrivate('checkbox_block')
    def checkbox_block(self, seq, name, selected, containers=None):
        "checkbox"
        format = '<div><label><input type="checkbox" %s name="%s" value="%s" %s>%s</label></div>'
        formType = 'checkbox'
        return self.selection_box(seq, name, selected, format, formType, containers)

    security.declarePrivate('radio_box_inline')
    def radio_box_inline(self, seq, name, selected, containers=None):
        "Radio box"
        format = '<label><input type="radio" %s name="%s" value="%s" %s>%s</label>'
        formType = 'radio'
        return self.selection_box(seq, name, selected, format, formType, containers)

    security.declarePrivate('radio_box_block')
    def radio_box_block(self, seq, name, selected, containers=None):
        "Radio box"
        format = '<div><label><input type="radio" %s name="%s" value="%s" %s>%s</label></div>'
        formType = 'radio'
        return self.selection_box(seq, name, selected, format, formType, containers)

    security.declarePrivate('selection_box')
    def selection_box(self, seq, name, selected, format, formType, containers=None):
        "create a selection box"
        classes = ' '.join(self.getClasses(name, formType))
        cssClass = 'class="%s"' % classes
        formname = self.formName(name, 'list', containers=containers)
        temp = ['<input type="hidden" name="%s:default" value="xXxDefaultxXx">' % formname]
        for name,printableName in basewidget.generateOptionSelectFormat(seq, list(selected)):
            if name in selected:
                temp.append(format % ('checked="checked"', formname, name, cssClass, printableName))
            else:
                temp.append(format % ('', formname, name, cssClass, printableName))
        return ''.join(temp)

    security.declarePrivate('convert')
    def convert(self, st):
        "Convert a string"
        st = str(st)
        temp = st.replace('"', '&quot;')
        temp = temp.replace('<', '&lt;')
        return temp.replace('>', '&gt;')

    security.declarePrivate('convertForEdit')
    def convertForEdit(self, st):
        "Convert a string"
        st = str(st)
        temp = st.replace('&', '&amp;')
        temp = temp.replace('"', '&quot;')
        temp = temp.replace('<', '&lt;')
        return temp.replace('>', '&gt;')

    security.declarePrivate('input_file')
    def input_file(self, name, value="", containers=None):
        "Input file object"
        meta_type = getattr(self, 'meta_type','')
        format = '<input type="file" name="%s" class="%s" value="%s">'
        classes = ' '.join(self.getClasses(name, meta_type))
        return  format % (self.formName(name, None, containers=containers), classes, value)

    security.declarePrivate('check_box')
    def check_box(self, name, value, containers=None, formType = 'string'):
        "General checkbox object"
        classes = ' '.join(self.getClasses(name, 'checkbox'))
        cssClass = 'class="%s"' % classes
        return '<input type="checkbox" name="%s" value="%s" %s>' % (self.formName(name, formType, containers=containers), value, cssClass)

    security.declarePrivate('begin_manage')
    def begin_manage(self):
        "Begin the basic manage init"
        self.noCacheHeader()
        return ''.join([self.manage_page_header(), self.manage_tabs(), self.begin_form(), '<div>'])

    security.declarePrivate('begin_form')
    def begin_form(self):
        "begin the form statement for doing cdoc changes"
        return '<form action="" enctype="multipart/form-data" method="post">'

    security.declarePrivate('create_buttons')
    def create_buttons(self, name, seq, containers=None):
        "Create a button set in one line"
        return [self.create_button(name, i, containers=containers) for i in seq]

    security.declarePrivate('create_button')
    def create_button(self, name, value, containers=None, title=''):
        "Create a single button"
        formName = self.formName(name, 'string', containers=containers)
        if title:
            title = 'title="%s"' % title
        return '<input type="submit" name="%s" value="%s" class="%s submit" %s >\n' % (formName, self.convertForEdit(value), self.getId(), title)

    security.declarePrivate('radio_list')
    def radio_list(self, name, tuple, selected=None, containers=None):
        "This makes a radio set"
        "The tuple this object takes is of the form (value, display)"
        temp = []
        classes = ' '.join(self.getClasses(name, 'radio'))
        cssClass = 'class="%s"' % classes
        format = '<input type="radio" name="%s" value="%s" %s %s>%s'
        for value, string in tuple:
            if selected and selected==value:
                temp.append(format % (self.formName(name, 'string', containers=containers), value, 'checked="checked"', cssClass, string))
            else:
                temp.append(format % (self.formName(name, 'string', containers=containers), value, '', cssClass, string))
        return temp

    security.declarePrivate('multiselect')
    def multiselect(self, name, seq, selected=None, size=None, containers=None):
        "Generate a multiple select list"
        if isinstance(selected, basestring):
            selected = [selected,]
        return self.option_select(seq, name=name, selected=selected, multiple=1, size=size, containers=containers)

    security.declarePrivate('formName')
    def formName(self, name, type, containers=None):
        "generate the name of the form"
        temp = self.getDictName()
        objectPath = temp[1]
        objectPath.insert(0, '')
        if containers:
            objectPath.extend(containers)
        objectPath.append(name)
        temp.append(type)
        return  FormOutputFilter(temp)

    security.declarePrivate('unorderedList')
    def unorderedList(self, seq):
        "Return the xhtml for an unordered list"
        format = '<li>%s</li>'
        temp = ['<ul>'] + [format % i for i in seq] + ['</ul>']
        return ''.join(temp)

    security.declareProtected("Access contents information", 'createTable')
    def createTable(self, rows):
        "create a table from this list it must be a balanced list within a list"
        temp = ['<table class="%s %s">' % (self.getId(), getattr(self, 'meta_type', ''))]
        format = '<td>%s</td>'
        for row in rows:
            temp.append('<tr>')
            temp.extend([format % cell for cell in row])
            temp.append('</tr>')
        temp.append('</table>')
        return ''.join(temp)

    security.declareProtected("Access contents information", 'formatListForTable')
    def formatListForTable(self, seq, columns, filler=''):
        "return a list that is formated for this many columns and fill it with the value in filler for extra"
        return utility.formatListForTable(seq, columns, filler)

    security.declarePrivate('createMultiListDict')
    def createMultiListDict(self, dict1, dict2, name, containers=None, size=10):
        "Create a multiple column js based list element"
        list1, list2, list3, list4 = self.listFromDict(dict1)
        list5, list6, list7, list8 = self.listFromDict(dict2, 1)

        return ''.join([self.multiselect(name, list1, list5, size=size, containers=containers),
          self.multiselect(name, list2, list6, size=size, containers=containers),
          self.multiselect(name, list3, list7, size=size, containers=containers),
          self.multiselect(name, list4, list8, size=size, containers=containers)])

    def listFromDict(self, dict, removeParentBlank=0):
        "Create a list structure from this dict"
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        if hasattr(dict, 'keys'):
            for i in dict:
                list1.append(i)
                for j in dict[i]:
                    list2.append(' '.join([i, j]))
                    for k in dict[i][j]:
                        list3.append(' '.join([i, j, k]))
                        for l in dict[i][j][k]:
                            list4.append(' '.join([i, j, k, l]))
                        if removeParentBlank:
                            if '' not in dict[i][j][k]:
                                list3.remove(' '.join([i, j, k]))
                    if removeParentBlank:
                        if '' not in dict[i][j]:
                            list2.remove(' '.join([i, j]))
                if removeParentBlank:
                    if '' not in dict[i]:
                        list1.remove(i)
        return list1, list2, list3, list4

Globals.InitializeClass(Widgets)
