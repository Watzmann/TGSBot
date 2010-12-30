#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

from twisted.web import proxy, http
from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from protocols import Echo, QOTD, CLIP
import sys
log.startLogging(sys.stdout)
 
class Command():
    def __init__(self,):
        self.commands = {
        'show': self.c_show,
        }
        
    def c_show(self, line):
        return 'shown'

    def c_unknown(self, line):
        return 'unknown command %s' % line[0]

    def command(self, cmd):
        return self.commands.get(cmd, self.c_unknown)

class ProxyFactory(http.HTTPFactory):
    protocol = Echo #proxy.Proxy
    numProtocols = 0
    maxProtocols = 0
    command = Command()

    def incNumProtocols(self,):
        self.numProtocols += 1
        self.maxProtocols = max(self.numProtocols, self.maxProtocols)
        return self.numProtocols
 
    def decNumProtocols(self,):
        self.numProtocols -= 1

    def parse(self, data):
        c = self.command
        a = data.split()
        print 'parsing',a
        cmd = c.command(a[0])
        ret = cmd(a)
        print 'got', ret
        return ret
        
reactor.listenTCP(8080, ProxyFactory())
reactor.run()
