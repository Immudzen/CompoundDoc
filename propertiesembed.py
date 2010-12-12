###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class PropertiesEmbed(UserObject):
    "Embed the properties from a standard zope object"

    security = ClassSecurityInfo()
    meta_type = "PropertiesEmbed"

    propertiesPath = ''
    propertiesAllowed = tuple()
    
    classConfig = {}
    classConfig['propertiesPath'] = {'name':'Path to Object:', 'type':'string'}
    classConfig['propertiesAllowed'] = {'name':'Names of allowed properties:', 'type':'tokens'}
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, container=None, properties=None, *args, **kw):
        "Inline edit short object"
        propertiesAllowed = properties or self.propertiesAllowed
        if container is not None:
            embed = container
        else:
            embed = self.restrictedTraverse(self.propertiesPath, None)
        if embed is not None:
            path = '/'.join(embed.getPhysicalPath())
            format = '<p>%s %s</p>'
            lookup = {'float':'input_float', 'string':'input_text', 'int':'input_number'}
            temp = []
            for property in embed.propertyMap():
                name = property['id']
                propertyType = property['type']
                value = embed.getProperty(name)
                if name in propertiesAllowed and propertyType in ('float','string', 'int'):
                    edit = getattr(self, lookup[propertyType])(name,value,containers=['embedded',path])
                    temp.append(format % (name, edit))
            return ''.join(temp)
        else:
            return '<p>Object could not be found</p>'

    security.declareProtected("Access contents information",'embedOne')
    def embedOne(self, name, container=None):
        "embed the edit interface for one property that is named"
        if container is not None:
            embed = container
        else:
            embed = self.restrictedTraverse(self.propertiesPath, None)
        if name in self.propertiesAllowed and embed is not None:
            lookup = {'float':'input_float', 'string':'input_text', 'int':'input_number'}
            value = embed.getProperty(name,None)
            if property is not None:
                propertyType = embed.getPropertyType(name)
                if propertyType in ('float','string', 'int'):
                    return getattr(self, lookup[propertyType])(name,value,containers=['embedded','/'.join(embed.getPhysicalPath())])
        return ''


    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        if 'embedded' in form:
            for path, value in form['embedded'].iteritems():
                embed = self.restrictedTraverse(path, None)
                if embed is not None:
                    embed.manage_changeProperties(**value)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        return ''

Globals.InitializeClass(PropertiesEmbed)
import register
register.registerClass(PropertiesEmbed)