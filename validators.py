###########################################################################
#    Copyright (C) 2006 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
checkers = {}


def checkString(value):
    "turn this item into a string or return None"
    try:
        return str(value)
    except ValueError:
        return None
checkers['string'] = checkString

def checkInt(value):
    "turn this item into an int or return None"
    try:
        return int(value)
    except ValueError:
        return None
checkers['int'] = checkInt

def checkFloat(value):
    "turn this item into a float or return None"
    try:
        return float(value)
    except ValueError:
        return None
checkers['float'] = checkFloat


def getChecker(checkerType):
    "return the checker for this checkerType"
    return checkers.get(checkerType, None)