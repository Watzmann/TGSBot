#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

import sys

from twisted.web import proxy, http
#from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from clip import CLIP
from command import Command
from sibs_user import UsersList
from game import GamesList

log.startLogging(sys.stdout)
 
class ProxyFactory(http.HTTPFactory):
    protocol = CLIP   #Echo #proxy.Proxy
    numProtocols = 0
    maxProtocols = 0
    active_users = UsersList()
    active_games = GamesList()
    command = Command(active_users, active_games)

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

    def host(self,):
        """soll den host des einloggenden spielers ermitteln."""
        from command import NYI
        return 'unknown host   %s' % NYI
        
reactor.listenTCP(8080, ProxyFactory())
reactor.run()
