###########################################################################
#    Copyright (C) 2005 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################

registeredClasses = {}

def registerClass(klass):
    registeredClasses[klass.meta_type] = klass

def classDict(self):
    "return a dictionary of all addable items backwards compat interface only"
    return registeredClasses