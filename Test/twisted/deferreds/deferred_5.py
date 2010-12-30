#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted.deferred'.
Beispiel aus dem twisted-core.pdf Kap. 3.8.2
"""

import time
from twisted.internet import reactor, threads

def aSillyBlockingMethod(x):
    time.sleep(2)
    print x

def doLongCalculation():
    # .... do long calculation here ...
    time.sleep(3.5)
    return 3

def printResult(x):
    print x
##    print 'stopping'
##    reactor.stop()

# run method in thread
reactor.callInThread(aSillyBlockingMethod, "2 seconds have passed")

# run method in thread and get result as defer.Deferred
d = threads.deferToThread(doLongCalculation)
d.addCallback(printResult)

reactor.run()
time.sleep(4)
reactor.callFromThread(reactor.stop)
