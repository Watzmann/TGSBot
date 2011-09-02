#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Administrative commands."""

REV = '$Revision$'

import inspect
from version import Version

VERSION = Version()
VERSION.register(__name__, REV)

class Service():
    def __init__(self, lou, log):
        self.commands = dict(self.sample_commands())
        self.list_of_implemented_commands = self.list_implemented()
        self.list_of_users = lou
        self.list_of_games = log   # TODO: was besseres als log (log ist logging)
        print 'implemented administrative commands:', self.list_of_implemented_commands
        #self.help = Help(self.list_of_implemented_commands)

# ----------------------------------------  Other Commands

    def a_kick(self, line, protocol):
        arglen = len(line)
        if arglen == 1:
            res = "** please give a name as an argument."
        else:
            user = self.list_of_users.get_active(line[1])
            if user is None:
                res = '** there is noone called %s' % line[1]
            else:
                user.disconnect_hard()
                res = 'kicked %s' % line[1]
        return res

    def a_bye(self, line, protocol):
        protocol.logout()

    a_end = a_quit = a_bye

# ----------------------------------------  ====================

    def unknown(self, line):
        return "** Unknown administrative command: '%s'" % line[0]

    def command(self, cmd):
        return self.commands.get(cmd, self.unknown)

    def sample_commands(self,):
        # TODO: falls man mal commands in den laufenden server injizieren will:
        #       als Plugin realisieren
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0][2:],f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('a_')]
        return lofc

    def list_implemented(self, verbose=False):
        imp = self.commands.keys()[:]
        imp.sort()
        for c in imp[:]:
            try:
                ret = self.commands[c]([c,'list',],None)
##                print c
##                print ret
                if ret.endswith(NYI):
##                    print 'removed', c
                    imp.remove(c)
            except:
                pass
        return imp

if __name__ == "__main__":
    c = Command(None, None)
    print c.c_version(1,2)
    for i in c.list_implemented():
        print i
