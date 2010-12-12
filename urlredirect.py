#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

from userobject import UserObject

class UrlRedirect(UserObject):
    "redirect to this url"

    security = ClassSecurityInfo()
    meta_type = "UrlRedirect"

    data = ''

    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        "Inline edit short object"
        return self.input_text('data', self.data)

    security.declareProtected('View', 'view')
    def view(self):
        "Inline draw view"
        url = self.data
        if url.count('<dtml'):
            url = self.gen_html(url)
        container = self.getCompoundDocContainer()
        if not url.count('://'):
            try:
                url = container.restrictedTraverse(url).absolute_url()
            except KeyError:
                url = container.absolute_url()
        return self.REQUEST.RESPONSE.redirect(url)

    security.declarePrivate('PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "This is the basic search function"
        return self.data

Globals.InitializeClass(UrlRedirect)
import register
register.registerClass(UrlRedirect)