import urllib2_file
import urllib2
import StringIO
import time

f = StringIO.StringIO('132>4684255,AV,4005550000000241,0109,11565,,,b,1081288879_2617742,,,,,0,,N')
f.name = '%s.csv' % repr(time.time()).replace('.', '_')
data = [('echo_id', '123>4684255'), ('merchant_pin', '27182818'),
        ('allow_duplicates', 'n'), ('batch_file', f)]

req = urllib2.Request(url='https://wwws.echo-inc.com/echonlinebatch/upload.asp', data=data)
string = urllib2.urlopen(req).read()
print string
