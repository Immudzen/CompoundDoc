###########################################################################
#    Copyright (C) 2003 by kosh
#    <kosh@kosh.aesaeion.com>
#
# Copyright: See COPYING file that comes with this distribution
#
###########################################################################
class IncrementalRender:
    "This object can be used to incrementally render a string given a base dictionary"

    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, name):
        return self.mapping.get(name, "%%(%s)s" % name)
