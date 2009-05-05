#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Testet den XML-Parser Komplex SAX"""

import sys
from xml.sax.xmlreader import XMLReader
from xml.sax.handler import ContentHandler
from optparse import OptionParser
from xml.sax import parse

class myHandler(ContentHandler):
    def __init__(self,):
        self.semaphore = ''

    def startElement(self, name, attrs):
        if not self.semaphore:
            print name, self.dump(attrs.__dict__)
            self.semaphore = name
        else:
            pass #rint name

    def endElement(self, name):
        if name == self.semaphore:
            print name, 'ended'
            self.semaphore = ''

    def characters(self, content):
        print content,

    def dump(self, attrs):
        print ',)', attrs,
        return
        for k in attrs:
            print '.)',k,attrs[k],

class Element:
    def __init__(self, filename):
        handler = myHandler()
        parse(filename, handler)
        
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
    if len(args) < 1:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    filename = args[0]
    if options.verbose:
        print 'XML-File:', filename

    element = Element(filename)
