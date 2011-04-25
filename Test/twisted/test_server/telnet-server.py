#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

import sys
import os
import time

from twisted.web import proxy, http
#from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from clip import CLIP

log.startLogging(sys.stdout)

if '.production' in os.listdir('.'):
    PORT = 4321
else:
    PORT = 8082

class Command:
    def __init__(self,):
        self.answer = 'hallo - ich bin der server'

class ProxyFactory(http.HTTPFactory):
    protocol = CLIP   #Echo #proxy.Proxy
    numProtocols = 0
    maxProtocols = 0
    command = Command()

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
##            print 'parsing',a
            time_before = time.time()
            cmd = c.command(a[0])
            ret = cmd(a, me)
            time_after = time.time()
            print 'got', ret
            print 'time used for %s: %f sec (%d users)' % \
              (a[0], time_after - time_before, self.active_users.nr_logged_in())
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

    ## TODO:  Application Object lesen - Twisted core.pdf, Seite 163

reactor.listenTCP(PORT, ProxyFactory())
reactor.run()
