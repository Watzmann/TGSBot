#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""An administration bot for script based administration tasks."""

import sys

from twisted.internet import reactor, defer
from optparse import OptionParser
from client.tgsClient import Com, ComClientFactory
from tgsBot import start_logging
from operation.admin import Dispatch

def client_run(options, admin_key):
    start_logging('admin')
    factory = ComClientFactory()
    factory.options = options
    factory.dispatcher = Dispatch('administration', admin_key)
    if hasattr(options, 'command_file'):
        factory.command_file = open(options.command_file, 'r')
    reactor.connectTCP(options.host, int(options.port), factory)
    reactor.run()

def get_admin_key(options, args):
    if hasattr(options, 'admin_key') and options.admin_key:
        return options.admin_key
    elif len(args) > 0 and args[0] != '-':
        return args[0]
    elif len(args) > 0 and args[0] == '-':
        return sys.stdin.readlines()[0].rstrip('\n')
    else:
        return 'not found'

def usage():
    usg = """usage: %prog [<admin-key>]
  %prog """ + __doc__ + """

  Example:
    cat <path to key-file> | ./adminBot.py - -f <path to command-file>"""
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print full entries to stdout")
    parser.add_option("-k", "--admin-key",
                  action="store", dest="admin_key",
                  help="admin key for access as administrator.\n" \
                        "This key may also be given as argument of via stdin.")
    parser.add_option("-H", "--host", default='localhost',
                  action="store", dest="host",
                  help="host. (localhost)")
    parser.add_option("-P", "--port", default='8081',
                  action="store", dest="port",
                  help="server port. (8081)")
    parser.add_option("-f", "--file",
                  action="store", dest="command_file",
                  help="file with admin commands for bulk-scripting")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    admin_key = get_admin_key(options, args)

    client_run(options, admin_key)
