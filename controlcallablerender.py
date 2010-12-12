###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from controlbase import ControlBase
from AccessControl import ClassSecurityInfo
import Globals

import os.path

import utility

from BTrees.OOBTree import OOBTree

class ControlCallableRender(ControlBase):
    "Control Panel for the new rendering system"

    meta_type = "ControlCallableRender"
    security = ClassSecurityInfo()
    control_title = 'Render'

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = []
        temp.append('<div class="configDataArea">')

        cdoc = self.getCompoundDoc()
        if cdoc.displayMap is not None:
            displays = [''] + list(cdoc.displayMap.keys())
            defaultEdit = ''
            defaultView = ''
            if cdoc.defaultDisplay is not None:
                defaultEdit = cdoc.defaultDisplay.get('edit', '')
                defaultView = cdoc.defaultDisplay.get('view', '')
            temp.append('<p>Default Edit: %s</p>' % self.option_select(displays, 'defaultEdit', [defaultEdit]))
            temp.append('<p>Default View: %s</p>' % self.option_select(displays, 'defaultView', [defaultView]))

        format = '''<div class="seperateColor"><p>Name:%s</p>
        <p>Header:%s</p>
        <p>Body:%s</p>
        <p>Footer:%s</p>
        <div>%s</div></div>'''
        
        name = self.input_text('renderName', '')
        header = self.input_text('renderHeader', '')
        body = self.input_text('renderBody', '')
        footer = self.input_text('renderFooter', '')
        button = self.create_button('addRender', 'Add New Display')
        temp.append(format % (name, header, body, footer, button))


        format = '''<div class="seperateColor"><p>%s %s View:%s Edit:%s</p>
        <p>Header:%s %s</p>
        <p>Body:%s %s</p>
        <p>Footer:%s %s</p>
        <p>Delete:%s</p>
        </div>'''


        if cdoc.displayMap is not None:
            for name,(header,body,footer) in cdoc.displayMap.items():
                url = cdoc.absolute_url_path()
                viewHref = '<a href="%s">%s</a>' % (os.path.join(url, name), name)
                editHref = '<a href="%s">%s</a>' % (os.path.join(url, 'manage', name), name)
                headerEdit = self.input_text('header', header, containers=('render',name))
                headerHref = self.getHref(header)
                bodyEdit = self.input_text('body', body, containers=('render',name))
                bodyHref = self.getHref(body)
                footerEdit = self.input_text('footer', footer, containers=('render',name))
                footerHref = self.getHref(footer)
                deleteControl = self.radio_box(name, value=None, containers=('delete',))
                button = self.submitChanges()
                temp.append(format % (button, name, viewHref, editHref,
                    headerEdit, headerHref,
                    bodyEdit, bodyHref,
                    footerEdit, footerHref,deleteControl))
        temp.append('</div>')
        return ''.join(temp)

    security.declarePrivate('formAdd')
    def formAdd(self, form):
        "add a render object from the form"
        name = form.get('renderName', None)
        header = form.get('renderHeader', '')
        body = form.get('renderBody', '')
        footer = form.get('renderFooter', '')
        utility.addRender(self.getCompoundDoc(), name, header, body, footer)

    security.declarePrivate('formEditRender')
    def formEditRender(self, form):
        "edit a render object"
        for name,data in form['render'].items():
            header = data.get('header','')
            body = data.get('body','')
            footer = data.get('footer','')
            self.editRender(name, header, body, footer)

    security.declarePrivate('editRender')
    def editRender(self, name, header, body, footer):
        "edit a render object"
        cdoc = self.getCompoundDoc()
        if cdoc.displayMap is None:
            cdoc.setObject('displayMap',OOBTree()) 
        mapping = (header, body, footer)
        if cdoc.displayMap[name] != mapping:
            cdoc.displayMap[name] = mapping

    security.declarePrivate('formDeleteRenders')
    def formDeleteRenders(self, form):
        "remove rendering objects"
        cdoc = self.getCompoundDoc()
        if cdoc.displayMap is not None:
            displays = form['delete'].keys()
            self.deleteRenders(displays)

    security.declarePrivate('deleteRenders')
    def deleteRenders(self, displays):
        "remove these displays"
        cdoc = self.getCompoundDoc()
        for display in displays:
            if cdoc.displayMap.has_key(display):
                del cdoc.displayMap[display]
            modes = []
            if cdoc.defaultDisplay is not None:
                for mode, default in cdoc.defaultDisplay.items():
                    if default == display:
                        modes.append(mode)
                for mode in modes:
                    del cdoc.defaultDisplay[mode]
            if cdoc.defaultDisplay is not None and not len(cdoc.defaultDisplay):
                cdoc.delObjects(('defaultDisplay',))
        if not len(cdoc.displayMap):
            cdoc.delObjects(('displayMap',))

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form=None):
        "This item is in charge of the profile/layout manager object"
        cdoc = self.getCompoundDoc()
        if 'addRender' in form:
            self.formAdd(form)
            del form['addRender']

        if 'render' in form:
            self.formEditRender(form)
            del form['render']

        if cdoc.displayMap is not None:
            if 'defaultEdit' in form:
                utility.setDefaultEdit(cdoc, form['defaultEdit'])
                del form['defaultEdit']
            if 'defaultView' in form:
                utility.setDefaultView(cdoc, form['defaultView'])
                del form['defaultView']

        if 'delete' in form:
            self.formDeleteRenders(form)
            del form['delete']

Globals.InitializeClass(ControlCallableRender)
