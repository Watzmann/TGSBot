#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liest die URL http://www.hannovermesse.de/suche_ap?x=1 und ..."""

from HTMLParser import HTMLParser
import sys,os
import urllib
from optparse import OptionParser

class HtmlFile:
    def __init__(self,name):
        self.h = MyHTMLParser()
        h = self.h
        f = urllib.urlopen(name)
        h.feed(f.read())
        h.close()
        self.Text = h.getText()
        return

def convert(source,dest):
##    g = HtmlFile(source)
##    text = g.Text
####    print '---------'*5
    f = file(dest,'w')
    u = urllib.urlopen(source)
##    for t in text:
    f.write(u.read())
##    u.close()
    f.close()
    print source,'::',dest
    return

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
    if False and len(args) < 2:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    default = 'http://www.hannovermesse.de/suche/popup/trefferliste.html?vst_jahr=2006&vst_nummer=001&sprache=1&session=3&aussteller=1'
    convert(default,'test.txt')
