
import Globals

class FormOutputFilter:
    "Generate the output information to create a form name"

    def __init__(self, seq):
        "Construct the output for a form"
        self.seq = self.process(seq)

    def process(self, seq):
        "Process the sequence to make the html form"
        docPath = '/'.join(seq[0])
        attributePath = '.'.join(seq[1])
        formType = seq[2]
        if formType is not None:
            return '%s%s:%s' % (docPath, attributePath, formType)
        else:
            return '%s%s' % (docPath, attributePath)

    def __str__(self):
        "Return the processed sequence"
        return self.seq

Globals.InitializeClass(FormOutputFilter)
