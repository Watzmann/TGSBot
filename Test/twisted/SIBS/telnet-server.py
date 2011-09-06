#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

REV = '$Revision$'

import sys
import os
import time

from twisted.web import proxy, http
#from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from clip import CLIP
import sibs_utils as utils
from command import Command
from administration import Service
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
    administration = Service(active_users, active_games)
    IPs = {}

    def __del__(self,):
        print 'ProxyFactory.__del__: shutting down users database'
        self.active_users.db.close()
        print 'ProxyFactory.__del__: shutting down games database'
        self.active_games.db.close()

    def incNumProtocols(self,):
        self.numProtocols += 1
        self.maxProtocols = max(self.numProtocols, self.maxProtocols)
        return self.numProtocols
 
    def decNumProtocols(self,):
        self.numProtocols -= 1

    def denyIP(self, IP):
        ips = utils.render_file('blockedIPs').splitlines()
        if IP in ips:
            return True
        if IP in self.IPs:
            self.IPs[IP] += 1
            return self.IPs[IP] > 10
        else:
            self.IPs[IP] = 1
            return False

    def reduceIP(self, IP):
        if IP in self.IPs:
            if self.IPs[IP] > 0:
                self.IPs[IP] -= 1

    def service(self, data, protocol):
        a = data.split()
        ret = ''
        if len(a) > 0:
            time_before = time.time()
            cmd = self.administration.command(a[0])
            ret = cmd(a, protocol)
            time_after = time.time()
            print 'got', ret
            print 'time used for administration %s: %f sec (%d users)' % \
              (a[0], time_after - time_before, self.active_users.nr_logged_in())
        return ret
        
    def parse(self, data, me):
        a = data.split()
        ret = ''
        if len(a) > 0:
            time_before = time.time()
            cmd = self.command.command(a[0])
            me.send_away_message()
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
