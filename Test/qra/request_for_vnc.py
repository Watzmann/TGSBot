# -*- coding: utf-8 -*-
"""request_for_vnc ermittelt die IP-Adresse über den Dienstleister
'www.wie-ist-meine-ip.net' und setzt ein Request an eine feste IP-Adresse ab.
Dort kann die IP aus 
"""
key = None

import urllib
from htmllib import HTMLParser
import formatter

f = urllib.urlopen('http://www.wie-ist-meine-ip.net/ipdisplay/?o=1')
response = f.read()

##print response

fmt = formatter.NullFormatter()

class MyHTML(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self, fmt)
        self.listen = False
        self.result = []

    def start_b(self,attrs):
##        print 'started b with %s' % attrs
        self.listen = True

    def end_b(self,):
##        print 'ended b'
        self.listen = False

    def handle_data(self, data):
##        print '##', data
        if self.listen:
            self.result.append(data)

h = MyHTML()
h.feed(response)
res = h.result
if key is None:
    key = 'intermediate_key_sovie'

f = urllib.urlopen('http://212.43.71.34/remote_request?o=%s&key=%s' % (res[0],key))
