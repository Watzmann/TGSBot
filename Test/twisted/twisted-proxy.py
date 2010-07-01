#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from protocols import Echo, QOTD
import sys
log.startLogging(sys.stdout)
 
class ProxyFactory(http.HTTPFactory):
    protocol = Echo #proxy.Proxy
    numProtocols = 0
 
reactor.listenTCP(8080, ProxyFactory())
reactor.run()
