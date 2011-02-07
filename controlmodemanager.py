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

import utility

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
            mode = self.getModeFromREQUEST(obj.drawDict)
            modes = sorted(obj.drawDict.keys())
            
            selectedIndex = self.REQUEST.form.get('selected', None)
            if selectedIndex is None:
                try:
                    selectedIndex = modes.index(mode)
                except ValueError:
                    selectedIndex = 0
            
            
            path = obj.absolute_url_path()

            temp = ['<div class="%s">' % self.cssClass]
            temp.append('''<script type="text/javascript">
            $(function() {
            $( "#tabsMode" ).tabs( { cache: true, selected: %s,
            
            show: function(event, ui) {$('#selected').val(ui.index);
            var queryLoc = '#query_'+ui.index;
            var query = $(queryLoc).attr('value');
            $('.configLeftBar li a').each(function(){
            var url = this.href.split('?')[0]+ '?' + query;
            this.href = url;
            })
            },
            load: function(event, ui) {$("a[rel^='lightbox']").colorbox({maxWidth:'85%%', maxHeight:'85%%', photo:true});
            $.fn.jPicker.defaults.images.clientPath='http://c2219172.cdn.cloudfiles.rackspacecloud.com/images/';
            $('.color_picker').jPicker();}
            } );
            });
            </script>
            ''' % selectedIndex)
            temp.append('<div id="tabsMode"><ul>')
            
            modes = [(mode,utility.updateQueryString(queryString, {'renderType':mode})) for mode in modes]
            
            for mode, query in modes:
                temp.append('<li><a href="%s/draw?%s">%s</a></li>' % (path, query, mode))
            temp.append('</ul></div>')
            
            for idx,(mode,query) in enumerate(modes):
                temp.append('<input type="hidden" id="query_%s" name="query" value="%s">' % (idx, query))
            
            temp.append('<input type="hidden" id="selected" name="selected" value="0">')
            temp.append('<p>%s</p></div>' % self.submitChanges())
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
