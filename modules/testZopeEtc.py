#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liest die Ports aus <zope>/etc/zope.conf aus"""

import sys
from HTMLParser import HTMLParser
from optparse import OptionParser
import re

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
    def __init__(self,txt):
        self.h = MyHTMLParser()
        h = self.h
        h.feed(txt)
        h.close()
        self.Text = h.Text
        return

class ZopeConf:
    
    def __init__(self,name):
        f = open(name)
        self.text = f.read()
        f.close()
        self.config = {}
        self.port_base()

    def port_base(self,):
        m = re.findall('^port-base.*$',self.text,re.M)
        # regexp noch verbessern!! (blanks am Zeilenanfang)
        #                           base direkt als gruppe 'port-base.*([0-9].*)'
        result = {}
        if m:
            result['multiple'] = len(m) > 1
            result['base'] = m[0].split()[-1]
        else:
            result = None
        self.config['port-base'] = result

    def get_port_base(self,):
        result = self.config['port-base']
        if result:
            result = int(result['base'])
        else:
            result = 0
        return result

    def versuch(self,):
        #print 'lese', source
        g = HtmlFile(self.text)
        ports = {}
        base = self.get_port_base()
        for k in g.Text.keys():
            #print (k+' + ')*8
            #print g.Text[k]
            lines = g.Text[k].split('\n')
            for line in lines:
                if line.lstrip().startswith('#'):
                    #print 'iss so',line.lstrip()
                    continue
                if 'address' in line:
                    a = line.split()
                    #print '##########',k,a[1]
                    try:
                        ports[k] = str(int(a[1]) + base)
                    except ValueError:
                        pass
        #print g.Text
        return ports
    
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
##    def_format = 'MB'
##    parser.add_option("-f", "--format",
##                  dest="format", default=def_format,
##                  help="""set output format to one of 'B,kB,MB,GB';
##                default is %s.""" % def_format)
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
##    if len(args) < 2:
##        print usg
##        print "!! Zu wenige Argumente angegeben"
##        sys.exit(1)
    #fn = '/var/opt/zope/ste-devel/etc/zope.conf'
    fn = '/var/opt/zope/demo/etc/zope.conf'
    if len(args):
        fn = args[0]
    ports = ZopeConf(fn).versuch()
    for p in ports.keys():
        print p, ports[p]
