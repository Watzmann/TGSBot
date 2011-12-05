#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from sys import stdout
import random
from test_client import Dispatch

VERBOSE = False

MESSAGES = (('shout', 'Ich bin heute mal hier!'), 
            ('shout', 'Ist Gustav da?'),
            ('shout', 'Do you have a cookie?'),
            ('shout', 'Where is Patti?'),
            ('shout', 'Spielt jemand mit mir'),
            ('tell', 'hannes Schau mal an'),
            )

def randomMessage(protocol):
    """Do a bit of random communication with the server."""
    return random.choice(MESSAGES)
    

class Commands:

    def __init__(self, command, message):
##        cmd =  {'shout': self.shout,
##                'tell': self.tell,
##                #'': self.,
##                }[command]
        cmd = eval('self.%s' % command)
        cmd(message)

    def compose(self,):
        return self.cmd, self.expected, self.wait

    def shout(self, message):
        self.cmd = ' '.join(['shout', message])
        self.expected = '17 %s' % message
        self.wait = True
    
    def tell(self, message):
        self.cmd = ' '.join(['shout', message])
        self.expected = '17 %s' % message
        self.wait = True
    
class Com(Protocol):

    wait = 3
    tackle = .1

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.teardown.cancel()
        if self.waiting_for_answer:
            self.waiting_for_answer = False
            self.test(data)
        else:
            self.waiting_for_answer = self.dispatch.parse(data)
        if VERBOSE:
            stdout.write('RETURN: ' + data)
        #print 'Waiting for answer', self.waiting_for_answer
        self.teardown = reactor.callLater(self.wait, self.dropConnection)
        
    def sendMessage(self, msg):
        print '>>', msg
        self.transport.write(msg + '\r\n')
        reactor.callLater(self.tackle, self.nextMessage)

    def nextMessage(self,):
        random = False
        try:
            if random:
                msg = randomMessage()
            elif not hasattr(self, 'messages'):
                self.messages = iter(MESSAGES)
                msg = self.messages.next()
            else:
                msg = self.messages.next()
            self.sendCommand(msg)
        except StopIteration:
            self.waiting_for_answer = self.dispatch.bye()

    def sendCommand(self, command):
        cmd, msg = command
        c = Commands(cmd, msg)
        cmd, expected, wait = c.compose()
        self.waiting_for_answer = self.dispatch.simple_command(*c.compose())

    def connectionMade(self,):
        print 'connectionMade'
        self.dispatch = Dispatch(self, 'helena', 'hallo')
        self.waiting_for_answer = False
        self.teardown = reactor.callLater(self.wait, self.dropConnection)
##        reactor.callLater(0.2, randomMessage, self)

    def dropConnection(self,):
        print 'dropConnection'
        self.transport.loseConnection()

    def test(self, data):
        if self.dispatch.expected_answer.test(data):
            if VERBOSE:
                #print 'correct answer:', data
                print '########## DATA CORRECT'
        else:
            print 'EXPECTED DATA:', self.dispatch.expected_answer.answer[1], '#'
            raise RuntimeError('Got unexpected data: %s##' % data)

class ComClientFactory(ClientFactory):

    protocol = Com

    def startedConnecting(self, connector):
        print 'Started to connect.'

##    def buildProtocol(self, addr):
##        print 'Connected.'
##        return Com()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        reactor.stop()

factory = ComClientFactory()
reactor.connectTCP('localhost', 8081, factory)
reactor.run()
