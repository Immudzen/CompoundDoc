
import Globals

class FormInputFilter:
    "process the returned form information into a dict"

    def __init__(self, form):
        "Construct the output for a form"
        self.form = self.process(form)

    def process(self, form):
        "Process the form into a dict"
        temp = {}
        for key,value in form.items():
            self.newParseString(temp, key, value)
        return temp

    def newParseString(self, temp,key,value):
        "parse the string passed in into dict embedded in the dict also passed in with value"
        if key.startswith('/'):
            elements = key.split('.')
            for element in elements[:-1]:
                if not element in temp:
                    temp[element] = {}
                temp = temp[element]
            temp[elements[-1]] = value
        else:
            temp[key] = value

    def __call__(self):
        "Return the processed form"
        return self.form

Globals.InitializeClass(FormInputFilter)
