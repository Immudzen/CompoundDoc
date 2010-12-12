###########################################################################
#    Copyright (C) 2003 by William Heymann
#    <kosh@aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from AccessControl import ClassSecurityInfo
import Globals

from autocreatorgetter import AutoCreatorGetter

class AutoPopulatorGetter(AutoCreatorGetter):
    """auto populator getter objbect which creates the data format needed for an auto populator to work.
    This feature will enable the use of a text file to auto create and then set data in many compounddocs at the
    same time which is good for importing large ammounts of data."""

    security = ClassSecurityInfo()
    meta_type = "AutoPopulatorGetter"

    security.declarePrivate('createDataSourceFromTree')
    def createDataSourceFromTree(self):
        "create an appropriate data source to be used to create another cdoc structure based on what is below folder"
        try:
            return ['%s %s\n%s\n\n' % (path, profile, object.getPopulatorInformation()) for path, profile, object in self.getCdocList()]
        except AttributeError:
            return ['Bad folder Location Given']

Globals.InitializeClass(AutoPopulatorGetter)
import register
register.registerClass(AutoPopulatorGetter)