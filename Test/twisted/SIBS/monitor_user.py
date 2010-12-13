#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool zum Untersuchen und Warten der Users-DB."""

import sys
from optparse import OptionParser
from persistency import Persistent, Db

def list_all(keys, db, verbose=False):
    print 'Users entries'

    if verbose:
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
        if verbose:
            print
            print '   ',v.toggles.values()
        print '   ',v.settings
        if verbose:
            print '   ', v.messages
            print '   ', v.saved_games

def delete_users(keys, db, verbose=False):
    print 'Deleting these users', keys
    for k in keys:
        print 'deleting',k
        del db.db[k]

def change_nick(keys, db, verbose=False):
    if not len(keys) == 2:
        print 'Have exactly 2 names to change nicks'
        return
    k1, k2 = keys
    print 'Changing user', k1, 'to', k2
    if k1 == k2:
        print keys, 'are identical'
        return
    db.db[k2] = db.db[k1]
    del db.db[k1]
    return

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
    parser.add_option("-d", "--delete",
                  action="store_true", dest="deletion", default=False,
                  help="delete given users")
    parser.add_option("-c", "--change",
                  action="store_true", dest="change", default=False,
                  help="change nick of given users")
    parser.add_option("-l", "--list",
                  action="store_true", dest="list_show", default=False,
                  help="show a full list of users")
    return parser,usg

if __name__ == '__main__':
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        users = args
    else:
        users = ''

    db = Db('db/users')
    if not users:
        keys = db.db.keys()
        keys.sort()
    else:
        keys = users
    print 'Registered users'
    for e,k in enumerate(keys):
        print e,k

    if options.list_show:
        list_all(keys, db, verbose = options.verbose)
    if options.deletion:
        delete_users(keys, db, verbose = options.verbose)
    if options.change:
        change_nick(keys, db, verbose = options.verbose)

    db.close()
