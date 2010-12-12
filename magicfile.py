import os

def magic(filename):
    "Process the call"
    mimetype = os.popen('file -b -i %s' % filename).read().rstrip()
    if not mimetype:
        mimetype = 'application/octet-stream'
    return mimetype

