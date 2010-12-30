#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

from twisted.web import proxy, http
from twisted.internet import pollreactor
#pollreactor.install()
from twisted.internet import reactor, defer, threads
from twisted.python import log
from protocols import Echo, QOTD, CLIP
import sys
import time
from subprocess import Popen, PIPE

log.startLogging(sys.stdout)

class Command():
    def __init__(self,):
        self.commands = {
        'show': self.c_show,
        'ip': self.c_ip,
        'sleep': self.c_sleep,
        }
        
    def c_show(self, line):
        return 'shown'

    def c_ip(self, line):
        ip = line[1]
        print 'looking up', ip
        d = threads.deferToThread(self.nslookup, ip)
        d.addCallback(self.deferred_ret)
        return d

    def c_sleep(self, line):
        sec = line[1]
        print 'falling asleep for %s seconds' % str(sec)
        d = threads.deferToThread(self.sleeping, sec)
        d.addCallback(self.deferred_ret)
        return d

    def c_unknown(self, line):
        return 'unknown command %s' % line[0]

    def command(self, cmd):
        return self.commands.get(cmd, self.c_unknown)

    def nslookup(self, ip):
        output = Popen(["nslookup", ip], stdout=PIPE).communicate()[0]
        ret = output.find('name = ')
        if ret == -1:
            ret = ''
        else:
            ret = output[ret+7:].splitlines()[0]
            if ret[-1] == '.':
                ret = ret[:-1]
        return ret

    def sleeping(self, sec):
        time.sleep(float(sec))
        return 'yaaawwwwwwnnnnn'

    def deferred_ret(self, msg):
        print 'und nu?', msg
        return msg

class ProxyFactory(http.HTTPFactory):
    protocol = CLIP #Echo #proxy.Proxy
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
        if len(a) and a[0] == 'MESSAGE':
            a = a[1:]
        cmd = c.command(a[0])
        d = defer.maybeDeferred(cmd, a)
        return d

reactor.listenTCP(8080, ProxyFactory())
reactor.run()
