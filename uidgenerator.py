###########################################################################
#    Copyright (C) 2004 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
#This software is released under GNU public license. See details in the URL:
#http://www.gnu.org/copyleft/gpl.html

import time
from AccessControl import getSecurityManager

def usernameUID(self):
    "return the current username"
    return getSecurityManager().getUser().getUserName()

def browserInfoUID(self):
    "return some unique string based on the browser name, ip address etc"
    browserName = self.REQUEST.environ['HTTP_USER_AGENT']
    ipAddress = self.REQUEST.environ['REMOTE_ADDR']
    if ipAddress == "127.0.0.1":
        ipAddress = self.REQUEST.environ.get('HTTP_X_FORWARDED_FOR', "127.0.0.1").split(',')[0]
    return browserName + ipAddress

def timestampUID(self):
    "return a timestamp based UID"
    return time.time()

def urlUID(self):
    "return the uid from the url"
    return self.REQUEST.form.get('uid', None)

lookup = {'UserName': usernameUID, 'Browser Information':browserInfoUID, 'TimeStamp':timestampUID, 'url':urlUID}

def getUID(format, self):
    "run the renderer that matches this format"
    return lookup[format](self)
