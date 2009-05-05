#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liest die Ports aus <zope>/etc/zope.conf aus"""

import sys
from HTMLParser import HTMLParser
from optparse import OptionParser

class MyHTMLParser(HTMLParser):
    trailer = '-server'
    record = False
    Text={}
    def handle_starttag(self, tag, attrs):
        #print tag
        if not self.record and self.trailer in tag:
            #print tag
            self.record = True
            self.tag = tag[:tag.find(self.trailer)]
    def handle_endtag(self, tag):
        if self.record and '-server' in tag:
            self.record = False
    def handle_data(self, data):
        if self.record:
            d = data.strip()
            if not d:
                return
            self.Text[self.tag] = d

class HtmlFile:
    def __init__(self,name):
        self.h = MyHTMLParser()
        h = self.h
        f = open(name)
        h.feed(f.read())
        h.close()
        self.Text = h.Text
        return

def versuch(source):
    #print 'lese', source
    g = HtmlFile(source)
    ports = {}
    for k in g.Text.keys():
        print (k+' + ')*8
        print g.Text[k]
        lines = g.Text[k].split('\n')
        for line in lines:
            if line.lstrip().startswith('#'):
                #print 'iss so',line.lstrip()
                continue
            if 'address' in line:
                a = line.split()
                #print '##########',k,a[1]
                ports[k] = a[1]
    return ports
    
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    fn = '/var/opt/zope/ste-devel/etc/zope.conf'
    if len(args):
        fn = args[0]
    ports = versuch(fn)
    for p in ports.keys():
        continue
        print p, ports[p]
