import basecatalog

#for type checking with isinstance
import types
import nestedlisturl as NestedListURL

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import com.catalog

class CatalogTraverse(basecatalog.BaseCatalog):
    "traversal capabilities for a catalog transparently and with dynamic menu and output support"

    meta_type = "CatalogTraverse"
    security = ClassSecurityInfo()
    navigationIndexes = None
    navigationOrder = None
    useCatalog = ''

    security.declarePrivate('getNavigationOrder')
    def getNavigationOrder(self):
        "get the navigationOrder list structure"
        if self.navigationOrder is not None:
            return self.navigationOrder
        return []

    security.declarePrivate('getNavigationIndexes')
    def getNavigationIndexes(self):
        "get the navigationIndexes list structure"
        if self.navigationIndexes is not None:
            return self.navigationIndexes
        return {}

    security.declarePublic('__bobo_traverse__')
    def __bobo_traverse__(self, REQUEST, name):
        "bobo method"
        if name:
            obj = getattr(self, name, None)
            if obj is not None:
                return obj
            stack = self.REQUEST.TraversalRequestNameStack
            stack.reverse()
            stack.insert(0, name)
            catalog = getattr(self.getCompoundDocContainer(), self.getRegisteredCatalog())
            list = []
            index = 0
            navigationOrder = self.getNavigationOrder()
            for i in stack:
                item = navigationOrder[index]
                if i in catalog.uniqueValuesFor(item):
                    list.append(i)
                    index = index + 1
            for i in list:
                if i in stack:
                    stack.remove(i)
            self.REQUEST.other['catalogFields'] = list
            return self.getCompoundDoc()

    security.declarePrivate('performUpdate')
    def performUpdate(self):
        "update this object"
        basecatalog.BaseCatalog.performUpdate(self)
        if not self.getRegisteredCatalog():
            self.setRegisteredCatalog(self.getDefaultCatalog())

    security.declarePrivate('getRegisteredCatalog')
    def getRegisteredCatalog(self):
        "Return the name of the current registered catalog"
        return self.useCatalog

    security.declarePrivate('setRegisteredCatalog')
    def setRegisteredCatalog(self, name):
        "set the registered catalog"
        self.setObject('useCatalog', name)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        catalog = getattr(self.getCompoundDocContainer(), self.getRegisteredCatalog())
        output = []
        fields = self.REQUEST.other.get('catalogFields', [])
        (ids, brains) = self.getCatalogResults(fields, catalog=catalog)
        fields = self.createUrlIdRecursiveList(ids, base=self.absolute_url())
        output.append(NestedListURL.drawNestedList(fields))
        if brains:
            output = [cdoc.getObject().render(mode='view') for cdoc in com.catalog.catalogIter(brains)]
        return ''.join(output)

    def createUrlIdRecursiveList(self, list, base):
        "convert the recursive list into a set of full (url, id) pairs that can be used"
        temp = []
        for i, item in enumerate(list):
            if isinstance(item, types.StringType):
                temp.append((base+'/'+item, item))
            if isinstance(item, types.ListType):
                temp.append(self.createUrlIdRecursiveList(item, base+'/'+list[i-1]))
        return temp


    def getCatalogResults(self, list, location=0, catalog=None):
        "return the items at this index recursively"
        navigationOrder = self.getNavigationOrder()
        item = navigationOrder[location]
        temp = []
        results = []
        custom = {}
        for i in xrange(location):
            local = navigationOrder[i]
            custom[local] = list[i]
        catalogOutput = catalog(custom)
        uniqueList = list(set([getattr(i, item) for i in catalogOutput]))
        for i in uniqueList:
            temp.append(i)
            if location < len(list) and list[location] == i:
                (output, catalogResults) = self.getCatalogResults(list, location+1, catalog)
                temp.append(output)
                if catalogResults:
                    results = catalogResults
        navigationIndexes = self.getNavigationIndexes()
        if location == len(list) and navigationIndexes[navigationOrder[location]]['returnResults']:
            return (temp, catalogOutput)
        return (temp, results)

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit view"
        temp = []
        temp.append("<div>Available Catalogs : %s</div>\n" % self.option_select(self.getAvailableCatalogs(),
                      'useCatalog',
                      [self.useCatalog]))
        catalog = getattr(self.getCompoundDocContainer(), self.getRegisteredCatalog())
        indexes = [i.getId() for i in catalog.index_objects() if i.meta_type == "FieldIndex"]
        typeformat = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'
        temp.append('<table>')
        temp.append(typeformat % ('ID:', 'Order:', 'Return Results'))
        navigationIndexes = self.getNavigationIndexes()
        for i in indexes:
            index = navigationIndexes.get(i, {})
            temp.append(typeformat % (i,
              self.input_float('order', index.get('order',0), containers=('navigationIndexes',i)),
              self.true_false('returnResults', index.get('returnResults',0), prefix=0, containers=('navigationIndexes',i))))
        temp.append('</table>')
        return ''.join(temp)

    def after_manage_edit(self, form):
        "create a cached copy of the items we want in the order we want them to speed up output"
        navigationIndexes = self.getNavigationIndexes()
        temp = [(j.get('order'), i) for i, j in navigationIndexes.items()]
        temp.sort()
        navigationOrder = tuple([i[1] for i in temp])
        if not len(navigationOrder):
            navigationOrder = None
        self.setObject('navigationOrder', navigationOrder)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Return what can be search which is nothing"
        return ''

Globals.InitializeClass(CatalogTraverse)
import register
register.registerClass(CatalogTraverse)
