import seperatordatafilter

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class CSVDataFilter(seperatordatafilter.SeperatorDataFilter):
    "CSVDataFilter apply this to an a list of dicts to make it output a csv file for mac/unix/windows"

    meta_type = "CSVDataFilter"
    security = ClassSecurityInfo()

    security.declarePrivate('customEdit')
    def customEdit(self):
        "This is an edit piece that can be overridden by various custom editing features needed by other filters"
        return ""

Globals.InitializeClass(CSVDataFilter)
import register
register.registerClass(CSVDataFilter)