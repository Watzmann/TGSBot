
from twisted.web.client import getPage
from twisted.internet import reactor, protocol
from twisted.protocols import basic

import time

def writeDataAndLoseConnection(data, url, transport, starttime):
    print 'fetched', url,
    transport.write(data)
    transport.loseConnection()
    print 'took', time.time() - starttime

class ProxyProtocol(basic.LineReceiver):

    def lineReceived(self, line):
        if not line.startswith('http://'):
            return
        start = time.time()
        print 'fetching', line
        deferredData = getPage(line)
        deferredData.addCallback(writeDataAndLoseConnection,
                                     line, self.transport, start)
        
factory = protocol.ServerFactory()
factory.protocol = ProxyProtocol

reactor.listenTCP(17980, factory)
reactor.run()
