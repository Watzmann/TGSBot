#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A twisted proxy to sniff communication between client and TiGa server."""

import sys
from optparse import OptionParser
from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.web import http
from twisted.internet.error import ReactorNotRunning
from datetime import date
import time
import random

LISTEN=8082

# TODO: one issue is:
#       it would be nice to have a different client log in and have it
#       recorded, too. Then the sniffing protocol had to be 'signed' in order
#       to tell things apart.
#       Presently the second client 'robbs' the stream from the first.

class Com(Protocol):

    def sendMessage(self, msg):
        self.transport.write("%s" % msg)

    def connectionMade(self):
        if self.factory.side == 'client':
            print 'client connected'
            host, port = self.factory.server_data
            reactor.connectTCP(host, port, self.factory.partner)
            self.auto_cmd = {False: self.dont_keep_alive,
                             True: self.keep_alive}[self.factory.keep_alive]
        self.factory.partner.receiver = self.sendMessage
        self.factory.is_listening = True
        self.buffer = []

    def connectionLost(self, reason):
        if self.factory.side != 'client':
            return
        print 'client Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def dataReceived(self, data):
        # TODO: put in a time stamp :)
        self.factory.sniffer.write(time.strftime("%H:%M:%S"))
        self.factory.sniffer.write(self.factory.separator)
        self.factory.sniffer.write(data)
        self.factory.sniffer.flush()
        if self.factory.partner.is_listening:
            self.factory.receiver(data)
            self.keep_alive()
        else:
            self.buffer += data
            print 'WARNING: buffered data!!'

    def keep_alive(self,):
        cka = getattr(self, '_call_keep_alive', None)
        if cka is None:
            delay = self.factory.get_delay()
            self._call_keep_alive = reactor.callLater(delay, self.send_cmd)
        else:
            cka.reset()

    def dont_keep_alive(self,):
        pass

    def send_cmd(self,):
        cmd = random.choice(self.factory.cmd_repository)
        self.sendMessage(cmd)
        del self._call_keep_alive

class ComServerFactory(http.HTTPFactory):
    # TODO: have a look: is HTTPFactory precisely what you need??

    protocol = Com
    is_listening = False
    cmd_repository = ("whois sorrytigger",)
    interval = (4., 9.)
    
    def __init__(self, sniffer):
        self.side = 'client'
        self.separator = '  %s client\n' % ('>'*65,)
        self.sniffer = sniffer

    def clientConnectionFailed(self, connector, reason):
        print self.side, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def get_delay(self,):
        return self.interval[0] + (self.interval[1] -
                                   self.interval[0]) * random.random()

class ComClientFactory(ClientFactory):

    protocol = Com
    is_listening = False

    def __init__(self, sniffer):
        self.side = 'server'
        self.separator = '  %s server\n' % ('<'*65,)
        self.sniffer = sniffer

    def startedConnecting(self, connector):
        print self.side, 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print self.side, 'Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def clientConnectionFailed(self, connector, reason):
        print self.side, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

def usage(progname):
    usg = """usage: %prog [<user>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    def_name = 'proxy_%s.log' % time.strftime("%y%m%d-%H%M")
    parser.add_option("-l", "--log-file",
                  action="store", dest="sniff_file_name", default=def_name,
                  help="write sniffers log to <log-file> [%s]" % def_name)
    parser.add_option("-s", "--host",
                  action="store", dest="host", default='localhost',
                  help="use <host> as a server [localhost].")
    parser.add_option("-p", "--port",
                  action="store", dest="port", default='8081',
                  help="use <port> to connect [8081].")
    parser.add_option("-k", "--keep-alive",
                  action="store_true", dest="keep_alive", default=False,
                  help="send keep-alive commands to FIBS to avoid timeout.")
    return parser,usg

if __name__ == '__main__':
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        a = args[0].split(':')
        if len(a) == 2:
            options.host = a[0]
            options.port = a[1]
        else:
            print "Excess arguments maybe 'host:port'.\nElse they are ignored!"

    print "Writing to", options.sniff_file_name
    print "Connecting to %s:%s" % (options.host, options.port)
    print "Listening on", LISTEN

    sniff_file = open(options.sniff_file_name, 'a')
    sniff_file.write('\n\n\n%s %s\n' % ('='*75, time.asctime()))
    server = ComClientFactory(sniff_file)
    client = ComServerFactory(sniff_file)

    server_data = (options.host, int(options.port))
    server.partner = client
    client.partner = server
    client.server_data = server_data
    client.keep_alive = options.keep_alive  # signals the client to send
                                            # commands to avoid FIBS timeout
    reactor.listenTCP(LISTEN, client)
    reactor.run()
    sniff_file.close()
