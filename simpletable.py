#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#base object that this inherits from
from userobject import UserObject

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class SimpleTable(UserObject):
    "presentation only simple table creation interface"

    meta_type = "SimpleTable"
    security = ClassSecurityInfo()

    table = None
    cols = 0

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        temp = [self.create_button("Add", "Add New Row")]
        deletionNames = [""] + range(1,len(self.getRows())+1)
        temp.append(self.option_select(deletionNames, 'editDelName'))
        temp.append(self.create_button("Del", "Delete Row"))
        temp.append(self.editSingleConfig('cols'))
        temp.append(self.createTable(self.formatListForEditing(self.getRows())))
        return ''.join(temp)

    security.declarePrivate('formatListForEditing')
    def formatListForEditing(self, rows):
        "fill this calendar object with the events"
        temp = []
        for row in rows:
            temp.append([self.input_text('data', cell) for cell in row])
        return temp

    security.declarePrivate('before_manage_edit')
    def before_manage_edit(self, form=None):
        "Process edits."
        #broken this should only be done when the number of columns changes not on every edit
        #it should also not create any columns
        data = form.pop('data', None)
        if data is not None:
            self.setRows(self.formatListForTable(data, self.cols))
        
        cols = form.pop('cols', None)
        if cols is not None:
            self.setObject('cols', cols)
            self.setColumn()
        
        if form.pop('Add',None):
            self.addRow()
        
        editDelName = form.pop('editDelName', None)
        if form.pop('Del', None) in form and editDelName is not None:
            self.removeRow(editDelName)

    security.declarePrivate('removeRow')
    def removeRow(self, name):
        "remove a row"
        try:
            position = int(name)-1
            del self.table[position]
            if not len(self.table):
                self.table=None
            self._p_changed=1
        except (ValueError,IndexError):
            pass

    security.declarePrivate('addRow')
    def addRow(self):
        "Add a row to this object"
        seq = self.getRows()
        newrow = ('',) * self.cols
        seq.append(newrow)
        self.setRows(seq)

    security.declarePrivate('setColumn')
    def setColumn(self):
        "Set the columns of the table object to conform with the value in config"
        cols = self.cols
        seq = self.getRows()
        if seq:
            temp = []
            for i in seq:
                if len(i) > cols:
                    temp.append(i[:cols])
                elif len(i) < cols:
                    i += (('',) * (cols-len(i)))
                    temp.append(i)
                else:
                    temp.append(i)
            self.setRows(temp)

    security.declarePrivate('setRows')
    def setRows(self, table):
        "set the table to be this list of lists"
        self.setObject('table', table)

    security.declarePrivate('getRows')
    def getRows(self):
        "get all the rows of this document"
        if self.table is not None:
            return self.table
        return [[]]

    security.declareProtected('View', 'view')
    def view(self):
        "Render page"
        return self.createTable(self.getRows())

    classConfig = {}
    classConfig['cols'] = {'name':'How many columns?', 'type':'int'}

    security.declarePrivate("PrincipiaSearchSource")
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return ''

Globals.InitializeClass(SimpleTable)
import register
register.registerClass(SimpleTable)