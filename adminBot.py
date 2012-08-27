#!/usr/bin/python
# -*- coding: utf-8 -*-
"""An administration bot for script based administration tasks."""

from twisted.internet import reactor, defer
from optparse import OptionParser
from client.sibsClient import Com, ComClientFactory
from sibsBot import start_logging

# einloggen als admin
# schleife
#   user anlegen
#     newUser aufrufen
#     eventuelle daten direkt setzen
#     user ausloggen

def client_run(options):
    start_logging('admin')
    factory = ComClientFactory()
    factory.options = options
    reactor.connectTCP(options.host, int(options.port), factory)
    reactor.run()

def get_admin_key(options, args):
    if hasattr(options, 'admin_key') and options.admin_key:
        return options.admin_key
    elif len(args) > 0 and args[0] != '-':
        return args[0]
    elif len(args) > 0 and args[0] == '-':
        return 'hallo'
    else:
        return 'not found'

def usage():
    usg = """usage: %prog [<admin-key>]
  %prog """ + __doc__
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
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
#sys.argv[0]
    admin_key = get_admin_key(options, args)

    client_run(options)
