#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Testet den Zugriff auf Zope über XML-RPC"""

import sys
from optparse import OptionParser
import xmlrpclib

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
    if len(args) < 2:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    if options.verbose:
        print 'Import-Path:', args[0]
        print '  File-Path:', args[1]

    server = xmlrpclib.ServerProxy('http://localhost:17480/test/')
    file_list = server.fileList(args[1])
    for i in file_list:
        import_path = args[0] + '/' + i[1]
        print import_path
        l = server.uploadFile(import_path,i[4],i[3])
        sip = raw_input('## press return ##')
