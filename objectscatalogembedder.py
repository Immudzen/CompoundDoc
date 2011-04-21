# -*- coding: utf-8 -*-
import basecatalog

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import com.catalog

class ObjectsCatalogEmbedder(basecatalog.BaseCatalog):
    "Uses the Catalogs to give access to a view of many compounddocs"

    meta_type = "ObjectsCatalogEmbedder"
    security = ClassSecurityInfo()

    inuse = None
    limit = 0
    
    classConfig = {}
    classConfig['limit'] = {'name':'Embed Limit:', 'type':'int'}
    
    security.declarePrivate('getRegisteredCatalog')
    def getRegisteredCatalog(self):
        "Return the name of the current registered catalog"
        return getattr(self,'useCatalog',None)

    security.declarePrivate('setRegisteredCatalog')
    def setRegisteredCatalog(self, name):
        "set the registered catalog"
        self.setObject('useCatalog', name)

    security.declarePrivate('after_manage_edit')
    def after_manage_edit(self, form):
        "Call this function after the editing has been processed so that additional things can be done like caching"
        if 'use' in form:
            formUse = form['use'].keys()
            if not len(formUse):
                formUse = None
            self.setObject('inuse', formUse)
        if 'clear' in form:
            self.delObjects(('inuse',))

    security.declarePrivate('configAddition')
    def configAddition(self):
        "addendum to the default config screen"
        return "<div>Available Catalogs : %s</div>\n" % self.option_select(self.getAvailableCatalogs(),
               'useCatalog', [self.useCatalog])

    security.declarePrivate('getRealCatalog')
    def getRealCatalog(self):
        "get the catalog object"
        catalogName = self.getRegisteredCatalog()
        return getattr(self, catalogName, None)

    security.declareProtected('View','getUseObjects')
    def getUseObjects(self):
        "Get the correct objects from the catalog based on the inuse object"
        catalog = self.getRealCatalog()
        if catalog is None or self.inuse is None or (self.limit and len(self.inuse) > self.limit):
            return None
        return [cdoc for cdoc in com.catalog.catalogIter(catalog(id=self.inuse))]

    security.declarePrivate('limitOkay')
    def limitOkay(self):
        'return 1 if we are within our allowed limits'
        if not self.limit or (self.limit and len(self.inuse) <= self.limit):
            return 1
        return 0


    security.declarePrivate('getUseNames')
    def getUseNames(self):
        "Get the correct objects from the catalog based on the inuse object"
        if self.inuse is not None:
            return self.inuse
        return []

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "edit this object embedder"
        format = '<tr><td>%s</td><td>%s</td><td>%s</td><td><a href="%s/manage">%s</a></td></tr>\n'
        inuse = self.getUseNames()
        catalog = self.getRealCatalog()
        temp = []
        if not catalog:
            return ''
        if self.limit:
            temp.append('<p>A limit on the number of objects that can be selected is currently enabled.</p>')
            temp.append('<p>If more then %s objects are selected this item will no longer draw to prevent problems.</p>' % self.limit)
            temp.append('<p>You can only select %s objects</p>' % self.limit)
        temp.append('<div>%s</div>' % self.create_button("clear", "Clear"))
        table = []
        table.append('<table>')
        table.append('<thead><tr><th>Use</th><th>Id</th><th>Title</th><th>Location</th></tr></thead>\n')
        catalogResults = [(i.getPath(),i) for i in catalog()]
        catalogResults.sort()
        table.append('<tbody>')
        selected  = []
        notselected = []
        for path, i in catalogResults:
            id = i.id
            if id in inuse:
                selected.append(format % (self.radio_box(id,1, ['use']), id, i.title, path, path))
            else:
                notselected.append(format % (self.radio_box(id,0, ['use']), id, i.title, path, path))
        table.extend(selected)
        if self.limit and len(inuse) > self.limit:
            temp.append('<p>You have too many objects currently selected you need to remove current ones before selecting more.<p>')
        elif self.limit and len(inuse) == self.limit:
            temp.append('<p>You are at the current limit of selected objects to select more you have to unselect one of the current ones.</p>')
        else:
            table.extend(notselected)
        table.append('<tbody></table>')
        temp.append('<p>You have %s items currently selected</p>' % len(inuse))
        temp.extend(table)
        return ''.join(temp)

Globals.InitializeClass(ObjectsCatalogEmbedder)
import register
register.registerClass(ObjectsCatalogEmbedder)