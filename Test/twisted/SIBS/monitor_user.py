#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool zum Untersuchen und Warten der Users-DB."""

import sys
from optparse import OptionParser
from persistency import Persistent, Db

def usage(progname):
    usg = """usage: %prog [<user>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print full entries to stdout")
    parser.add_option("-p", "--password",
                  action="store_true", dest="passwd", default=False,
                  help="print passwords to stdout")
    return parser,usg

if __name__ == '__main__':
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        user = args[0]
    else:
        user = ''

    db = Db('db/users')
    if user:
        keys = [user,]
    else:
        keys = db.db.keys()
        keys.sort()
        print 'Registered users'
        for e,k in enumerate(keys):
            print e,k
        print 'Users entries'

    if options.verbose:
        print '   ',db.db.values()[0].toggles.keys()

    for e,k in enumerate(keys):
        print e,k
        v = db.db[k]
        address = getattr(v, 'address', '-')
        if options.passwd:
            passwd = v.passwd
        else:
            passwd = '*****'
        print '   ', v.login, v.last_logout, v.host, v.name, passwd, \
                     v.rating, v.experience, address
        if options.verbose:
            print
            print '   ',v.toggles.values()
        print '   ',v.settings
        if options.verbose:
            print '   ',v.messages
    db.close()
