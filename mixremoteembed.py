import base
import utility

#For Security control and init
from AccessControl import ClassSecurityInfo
import Globals

class MixRemoteEmbed:
    "Base for all items that embed remote items"

    meta_type = "MixRemoteEmbed"
    security = ClassSecurityInfo()
    modes = ('view', 'edit', 'config', 'debug')

    security.declarePrivate('embedRemoteObject')
    def embedRemoteObject(self, item, path, mode, view, profile, showid=1):
        "return this item with this subpath mode and view"
        if mode not in self.modes:
            return ''
        if profile:
            if getattr(item,'profile',None) == profile:
                return self.commonEmbedRemoteObject(item,path,mode,view, showid)
        else:
            return self.commonEmbedRemoteObject(item,path,mode,view, showid)
        return ''

    security.declarePrivate('commonEmbedRemoteObject')
    def commonEmbedRemoteObject(self, item, path, mode, view, showid):
        "common part of embedRemoteObject for profile and non profile mode"
        formatid = '<p>%s</p>%s'
        if path:
            if path[0] == '/':
                path = path[1:]
            item = item.restrictedTraverse(path)
            if utility.isinstance(item, base.Base):
                if showid:
                    return formatid % (item.getCompoundDoc().getId(), item(mode=mode))
                else:
                    return item(mode=mode)
        elif utility.isinstance(item, base.Base):
            self.setDrawMode(mode)
            string = item.render(name=view, mode=mode)
            if showid:
                return formatid % (item.getId(), string)
            else:
                return string
        return ''

Globals.InitializeClass(MixRemoteEmbed)
