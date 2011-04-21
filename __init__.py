#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

from base import Base
from baseobject import BaseObject
import compounddoc
import utility
import basewidget

from Products.PythonScripts.Utility import allow_module, allow_class
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from AccessControl.class_init import InitializeClass

allow_module('com.javascript')
allow_module('com.css')
allow_module('com.detection')
allow_module('com.html')
allow_module('com.form')
allow_module('com.catalog')


def initialize(context):
    "Initialize the CompoundDoc object."
    root = getattr(context, '_ProductContext__app')

    if root is not None and root.hasObject('CDocShared'):
        root.manage_delObjects(['CDocShared'])

    context.registerClass(
       compounddoc.CompoundDoc,
       permission='Add CompoundDoc',
       constructors=(
        compounddoc.manage_add_form,
        compounddoc.manage_addCompoundDoc,
        compounddoc.getAutoName,
        compounddoc.createNameTimeStamp,
        compounddoc.createNameCounter,
        compounddoc.CompoundDoc.gen_html,
        basewidget.option_select,
        basewidget.generateOptionSelectFormat,
        utility.getStoredProfileNames,
        utility.checkProfilesDir,
        utility.cleanRegisteredId,
        utility.drawFolderPath,
        utility.log,
        utility.isCleanFileName,
        utility.allowed_profile,
         )
    )
