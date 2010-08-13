#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Beispiel aus dem twisted-core.pdf Kap. 2.1.2
"""

from time import time
from twisted.internet.protocol import Protocol
##from twisted.python import log
from sibs_user import User, getUser, dropUser
import sibs_utils as utils

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
        
    def connectionLost(self, reason):
        user = self.user
        print 'dropping user', user.name
        self.user.drop_connection()
        dropUser(user=user.name, lou = self.factory.active_users)
        Echo.connectionLost(self, reason)

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
            login_time = time()
            d = data.split()[1:]
            print 'Login Prozess with', d[:-1], '*******'
            self.user = getUser(user=d[2], password=d[3],
                                lou = self.factory.active_users)
            self.user.set_protocol(self)
            self.user.set_login_data(time)
            welcome = ['', self.user.welcome()]
            welcome += [self.user.own_info(),]
            welcome += utils.render_file('motd').splitlines()
            welcome += utils.render_file('intro').splitlines()
            for m in welcome:
                print 'welcome',m
                self.transport.write('%s\r\n' % m)
            self.myDataReceived = self.established

    def tell(self, msg):
        self.transport.write('%s\r\n' % (msg,))

class Simple:
    """Protokoll für Testzwecke."""
    def __init__(self, user_name='unknown'):
        self.prefix = 'TELL %s:' % user_name
    def tell(self, msg):
        print self.prefix, msg
