
from twisted.web.client import getPage
from twisted.internet import reactor, protocol
from twisted.protocols import basic

class CachingProxyProtocol(basic.LineReceiver):

    def lineReceived(self, line):
        print '# >', line
        if not line.startswith('http://'):
            return
        try:
            data = self.factory.cache[line]
            transport.write(data)
            transport.loseConnection()
        except KeyError:
            def gotData(data):
                self.factory.cache[line] = data
                transport.write(data)
                transport.loseConnection()
            deferredData = getPage(line)
            deferredData.addCallback(gotData)

class CachingProxyFactory(protocol.ServerFactory):
    protocol = CachingProxyProtocol
    cache = {}

reactor.listenTCP(17980, CachingProxyFactory())
reactor.run()
