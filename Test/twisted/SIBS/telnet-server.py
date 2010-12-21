#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

REV = '$Revision$'

import sys
import os

from twisted.web import proxy, http
#from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from clip import CLIP
from command import Command
from sibs_user import UsersList
from game import GamesList
from version import Version

v = Version()
_module__ = __name__
if __name__ == '__main__':
    _module__ = __file__
v.register(_module__, REV)

print 'registered modules:'
for m in v.registered_modules():
    print ' ', v.version(m)
print v.version()

log.startLogging(sys.stdout)

if '.production' in os.listdir('.'):
    PORT = 4321
else:
    PORT = 8081

class ProxyFactory(http.HTTPFactory):
    protocol = CLIP   #Echo #proxy.Proxy
    numProtocols = 0
    maxProtocols = 0
    active_users = UsersList()
    active_games = GamesList()
    command = Command(active_users, active_games)

    def __del__(self,):
        ## TODO:  hier kommt er wohl gar nicht rein
        print 'shutting down users database'
        self.active_users.db.close()
        print 'shutting down games database'
        self.active_games.db.close()

    def incNumProtocols(self,):
        self.numProtocols += 1
        self.maxProtocols = max(self.numProtocols, self.maxProtocols)
        return self.numProtocols
 
    def decNumProtocols(self,):
        self.numProtocols -= 1

    def parse(self, data, me):
        c = self.command
        a = data.split()
        ret = ''
        if len(a) > 0:
            print 'parsing',a
            cmd = c.command(a[0])
            ret = cmd(a, me)
            print 'got', ret
        return ret

    def broadcast(self, msg, exceptions=()):
        """Sends msg as a broadcast to all logged clients."""
        users = self.active_users.get_all_users()
        print 'broadcast:', msg
        for u in users:
            if u.name in exceptions:
                continue
            u.chat(msg)

    def __str__(self,):
        return """TGS TigerGammon Server: %s""" % v.version()

    ## TODO:  es muss für einen user "systemwart" eine eigene command-Klasse
    ##        geben. Darin Commands wie "stop", "flush", vielleich logginglevel
    ##        delete(user) und so weiter

reactor.listenTCP(PORT, ProxyFactory())
reactor.run()
