#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool zum Untersuchen und Warten der Users-DB."""

import sys
from optparse import OptionParser
from persistency import Persistent, Db

def list_all(keys, db, options):
    verbose = options.verbose
    print 'Users entries'

    if verbose:
        print '   ',db.db.values()[0].toggles.keys()

    e = 1
    for k in keys:
        v = db.db[k]
        if not consider(v, options.show_test, options.hide_test):
            continue
        print e,k
        e += 1
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
            print ' ms ', v.messages
            print ' sg ', v.saved_games
            print ' bl ', v.blinded
            print ' gg ', v.gagged
            print ' sc ', v.special

def delete_users(keys, db, options):
    verbose = options.verbose
    print 'Deleting these users', keys
    for k in keys:
        print 'deleting',k
        del db.db[k]

def change_nick(keys, db, options):
    verbose = options.verbose
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

def set_test_flag(keys, db, options):
    verbose = options.verbose
    print 'Setting test flag to these users', keys
    for k in keys:
        db.db[k].special = 'test'

def consider(user, show, hide):
    test = user.special == 'test'
##    print 'consider', user.special, test, show, hide
    if show:
        return (test and show) and not (test and hide)
    else:
        return (test and show) or not (test and hide)

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
    parser.add_option("-f", "--flag-test",
                  action="store_true", dest="flag_test", default=False,
                  help="set test flag to given users")
    parser.add_option("-t", "--test",
                  action="store_true", dest="show_test", default=False,
                  help="only show test users in listing")
    parser.add_option("-T", "--hide-test-users",
                  action="store_true", dest="hide_test", default=False,
                  help="omit test users from listing")
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
    e = 1
    for k in keys:
        if consider(db.db[k], options.show_test, options.hide_test):
            print e,k
            e += 1

    if options.list_show:
        list_all(keys, db, options)
    if options.deletion:
        delete_users(keys, db, options)
    if options.change:
        change_nick(keys, db, options)
    if options.flag_test:
        set_test_flag(keys, db, options)

    db.close()
