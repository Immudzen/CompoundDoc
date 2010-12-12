# -*- coding: utf-8 -*-
from zope.structuredtext import stng, document, html
import cgi

class NoCodeStructured(html.HTMLWithImages):
    "Create a structured text item with no ability to render <code></code>"

    def literal(self, doc, level, output):
        output("'")
        for c in doc.getChildNodes():
            output(cgi.escape(c.getNodeValue()))
        output("'")

def HTML(aStructuredString, level=1, header=1):
    st = stng.structurize(aStructuredString)
    doc = document.DocumentWithImages()(st)
    return NoCodeStructured()(doc, header=header, level=level)