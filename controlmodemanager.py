# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2008 by kosh                                      
#    <kosh@kosh.aesaeion.com>                                                             
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
from basecontrolmanager import BaseControlManager

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals
import com.javascript

import utility
import nestedlisturl as NestedListUrl

class ControlModeManager(BaseControlManager):
    "different mode views of objects"

    meta_type = "ControlModeManager"
    security = ClassSecurityInfo()
    control_title = 'Mode'
    drawMode = 'config'
    drawBlankPath = 1
    
    security.declareProtected('View management screens', 'edit')
    def edit(self, *args, **kw):
        """This draws the inline forms for the objects present."""
        origin = self.getOrigin()
        path = self.getFixedUpPath()
        if path or (not path and self.drawBlankPath) and origin is not None:
            obj = origin.unrestrictedTraverse(path, None)
        else:
            obj = None
        if obj is not None:
            queryString = self.REQUEST.environ.get('QUERY_STRING', '')
            draw_mode = self.getModeFromREQUEST(obj.drawDict)
            modes = sorted(obj.drawDict.keys())
            
            path = obj.absolute_url_path()

            temp = ['<div class="%s">' % self.cssClass]
                     
            menu = []
            otherAttributes = ''
            cssClasses = ''
            queryDict = utility.getQueryDict(queryString)
            for mode in modes:
                selected = draw_mode == mode                
                queryDict['renderType'] = mode
                menu.append((self.REQUEST.URL,mode,selected,cssClasses,queryDict.copy(),otherAttributes))
            
            temp.append(NestedListUrl.listRenderer('Themeroller Tabs',menu, None))
            
            tab_format = '<div id="%s">%s<div>%s</div></div>'
            config_object = obj.getConfigObject()
            if config_object is not None and config_object is not self:
                mode_url = obj.drawDict[draw_mode]
                tabs = ((obj.absolute_url_path() + '/' + mode_url,'Local'), 
                    (config_object.absolute_url_path() + '/' + mode_url,'Config'))
                temp.append('<div>%s</div>' % self.submitChanges())
                temp.append(com.javascript.tabs_html('control_tabs', tabs))
            else:
                temp.append(obj.draw(draw_mode))
                temp.append('<div>%s</div>' % self.submitChanges())
            return ''.join(temp)
        return ""

    security.declarePrivate('getModeFromREQUEST')
    def getModeFromREQUEST(self, allowed):
        "get the current mode from the REQUEST object"
        mode = self.REQUEST.form.get('renderType', self.drawMode)
        
        if mode in allowed:
            return mode
        else:
            return 'edit'

Globals.InitializeClass(ControlModeManager)
