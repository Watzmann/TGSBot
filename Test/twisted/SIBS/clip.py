#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Beispiel aus dem twisted-core.pdf Kap. 2.1.2
"""

from twisted.internet.protocol import Protocol
##from twisted.python import log
from sibs_user import User, getUser

class Echo(Protocol):
    def dataReceived(self, data):
        print 'heard:', data
        self.transport.write('echo %d: %s\r\n' % (self.id,data))
        if data.startswith('exit'):
            print 'lasse die Verbindung %d fallen' % self.id
            self.transport.loseConnection()

    def connectionMade(self):
        self.id = self.factory.incNumProtocols()
        print 'had %d connections so far :)' % self.factory.maxProtocols
        if self.factory.numProtocols > 1001:
            print 'wegen ueberfuellung geschlossen'
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()
        #msg = 'hi there %d, please login\r\n' % self.id
        msg = 'login: '
        self.transport.write(msg)

    def connectionLost(self, reason):
        self.factory.decNumProtocols()
        print 'aus die maus', self.id

class CLIP(Echo):
    def __init__(self,):
        self.buffer = ''
        self.myDataReceived = self.authentication
        
    def dataReceived(self, data):
        self.buffer += data
        if self.buffer.endswith('\r\n'):
            d = self.buffer
            self.buffer = ''
            self.myDataReceived(d)
        
    def established(self, data):
        print 'heard:', data
        if data.lower().startswith('quit'):
            print 'lasse die Verbindung %d fallen' % self.id
            self.transport.loseConnection()
        result = self.factory.parse(data, self.user)
        if not result is None:
            self.transport.write('%s\r\n' % (result,))

    def authentication(self, data):
        if data.startswith('login'):
            #login <client_name> <clip_version> <name> <password>\r\n
            d = data.split()[1:]
            print 'Login Prozess with', d
            self.user = getUser(user=d[2], password=d[3],
                                lou = self.factory.active_users)
            self.user.set_protocol(self)
            self.myDataReceived = self.established

    def tell(self, msg):
        self.transport.write('%s\r\n' % (msg,))
