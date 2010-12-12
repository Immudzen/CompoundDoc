# -*- coding: utf-8 -*-
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
from baseobject import BaseObject
from Acquisition import aq_base
import utility

class MixConfigObject(BaseObject):
    "this is a mixin class to give objects a configuration"

    meta_type = "MixConfigObject"
    security = ClassSecurityInfo()

    security.declarePrivate('hasConfig')
    def hasConfig(self):
        "Return true if this object has a config"
        return hasattr(aq_base(self),'classConfig')

    security.declarePrivate('setConfig')
    def setConfig(self, config):
        "set the config if the item is a config object"
        if not self.configureable:
            return None
        try:
            temp = {}
            for key, value in config.items():
                try:
                    temp[key] = value['value']
                except KeyError:
                    pass
            self.setObject('objectConfig', temp)
        except AttributeError:
            self.setObject('objectConfig', config.convertToDict())


    security.declareProtected('View management screens', 'config')
    def config(self, **kw):
        """This is the object configuration form it allows you to
        modify certain aspects of the objects."""
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html; charset=%s' % self.getEncoding())
        if hasattr(aq_base(self), 'configAddition'):
            return self.drawEditConfig() + self.configAddition()
        return self.drawEditConfig()

    security.declarePrivate('drawEditConfig')
    def drawEditConfig(self):
        "draw the configs of this object in a way that they can be edited to get rid of all the config custom code"
        if self.hasConfig():
            return self.editConfig()
        else:
            return ""

    security.declarePrivate('editConfig')
    def editConfig(self, containers=None):
        "editify this config object"
        if not self.configureable:
            return ""
        temp = [self.editSingleConfig(key, containers) for key in sorted(self.classConfig)]
        return ''.join(temp)

    security.declareProtected('View management screens', 'editSingleConfig')
    def editSingleConfig(self, key, containers=None, format='<p>%(name)s %(form)s</p>\n'):
        "draw a single config entry in the standard format"
        value = getattr(self, key,None)
        name = self.classConfig[key]['name']
        configType = self.classConfig[key]['type']
        
        lookup = {'name':name}
        method = getattr(self, "render_%s" % configType, None)
        if method is not None:
            return method(name, key, value, containers, format, lookup)
        return ''

    security.declarePrivate('render_edit')
    def render_edit(self, name, key, value, containers, format, lookup):
        "draw the edit control for a named object"
        return  getattr(self, name).edit()
        
    security.declarePrivate('render_text')
    def render_text(self, name, key, value, containers, format, lookup):
        "draw the text rendering control"
        lookup['form'] = self.text_area(key, value, containers=containers)
        return format % lookup
    
    security.declarePrivate('render_string')
    def render_string(self, name, key, value, containers, format, lookup):
        "draw the text rendering control"
        lookup['form'] = self.input_text(key, value, containers=containers)
        return format % lookup         

    security.declarePrivate('render_tokens')
    def render_tokens(self, name, key, value, containers, format, lookup):
        "draw the text rendering control"
        lookup['form'] = self.input_tokens(key, value, containers=containers)
        return format % lookup

    security.declarePrivate('render_int')
    def render_int(self, name, key, value, containers, format, lookup):
        "draw the text rendering control"
        lookup['form'] = self.input_number(key, value, containers=containers)
        return format % lookup 
    
    security.declarePrivate('render_float')
    def render_float(self, name, key, value, containers, format, lookup):
        "draw the floating point input rendering control"
        lookup['form'] = self.input_float(key, value, containers=containers)
        return format % lookup
    
    security.declarePrivate('render_list')
    def render_list(self, name, key, value, containers, format, lookup):
        "draw the selection list rendering control"
        values = self.classConfig[key]['values']
        size = self.classConfig[key].get('size', None)
        lookup['form'] = self.option_select(seq = values, name = key, selected = [value], size=size, containers=containers)
        return format % lookup
    
    security.declarePrivate('render_multiple')
    def render_multiple(self, name, key, value, containers, format, lookup):
        "draw the multiple selection rendering control"
        values = self.classConfig[key]['values']
        size = self.classConfig[key].get('size', None)
        lookup['form'] = self.multiselect(seq = values, name = key, selected = value, size=size, containers=containers)   
        return format % lookup

    security.declarePrivate('render_radio')
    def render_radio(self, name, key, value, containers, format, lookup):
        "draw the radio rendering control"
        lookup['form'] = self.true_false(key, value, 0, containers=containers)
        return format % lookup
    
    security.declarePrivate('render_file')
    def render_file(self, name, key, value, containers, format, lookup):
        "draw the file rendering control"
        lookup['form'] = self.input_file(key, utility.renderNoneAsString(value), containers=containers)
        return format % lookup
    
    security.declarePrivate('render_path')
    def render_path(self, name, key, value, containers, format, lookup):
        "draw the path rendering control"
        lookup['form'] = self.input_text(key, value, containers=containers)
        href = self.getHref(value)
        if href:
            lookup['form'] = '%s %s' % (lookup['form'], href)
        return format % lookup
                
Globals.InitializeClass(MixConfigObject)
