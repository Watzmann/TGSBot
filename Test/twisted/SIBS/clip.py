#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementation of the CLIP CLIent Protocol as specified by the
CLIP specification V 1.008 - 08 Mar 1997
"""

from time import time
from twisted.internet.protocol import Protocol
##from twisted.python import log
from sibs_user import getUser, dropUser
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
        # TODO    banner
        msg = 'login: '
        self.transport.write(msg)

    def dropConnection(self, reason):
        # TODO: macht das Sinn hier?
        #       die Unterscheidung zwischen versehentlichem und absichtlichem
        #       drop muss klar werden. (NACHARBEITEN)
        #       z.B.: wenn JavaFIBS auf disconnect klickt, wird nix broadcasted
        print 'dropping for:', reason
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.decNumProtocols()
        print 'connection lost'
        print reason
        print 'aus die maus', self.id

class CLIP(Echo):
    def __init__(self,):
        self.buffer = ''
        self.myDataReceived = self.authentication
        
    def dropConnection(self, reason):
        user = getattr(self,'user',None)
        if not user is None:
            print 'dropping user', user.name
            self.user.drop_connection()
            dropUser(user=user.name, lou = self.factory.active_users)
        Echo.dropConnection(self, reason)

    def dataReceived(self, data):
        self.buffer += data
        if self.buffer.endswith('\r\n'):
            d = self.buffer
            self.buffer = ''
            self.myDataReceived(d)
        
    def established(self, data):
        print 'heard:', data
        result = self.factory.parse(data, self.user)
        if not result is None:
            self.transport.write('%s\r\n' % (result,))

    def authentication(self, data):
        if data.startswith('login'):
            #login <client_name> <clip_version> <name> <password>\r\n
            login_time = time()
            d = data.split()[1:]
            if len(d) > 3:
                print 'Login process with', d[:-1], '*******'
                self.user = getUser(client=d[0], clip_version=d[1],
                                    user=d[2], password=d[3],
                                    lou = self.factory.active_users)
                if not self.user is None:
                    self.user.set_protocol(self)
                    self.user.set_login_data(login_time, self.factory.host())
                    welcome = ['', self.user.welcome()]
                    welcome += [self.user.own_info(),]
                    welcome += utils.render_file('motd').splitlines()
                    welcome += utils.render_file('fake_message').splitlines()
                    # TODO: hier statt intro die messages ausgeben
                    who = self.factory.command.c_rawwho(['rawwho',], self.user)
                    welcome += [who,]
                    for m in welcome:
                        print 'welcome',m
                        self.transport.write('%s\r\n' % m)
                    self.myDataReceived = self.established
                    name = self.user.name
                    self.factory.broadcast('7 %s %s logs in' % (name, name),
                                           exceptions=(name,))
                else:
                    print 'user not known or wrong password'
            else:
                reason = 'Login process cancelled - ' \
                         'not enough paramaeters (%d)' % len(d)
                self.dropConnection(reason)

    def logout(self,):
        name = self.user.name
        logout = utils.render_file('extro') + utils.render_file('about')
        self.transport.write('%s\r\n' % (logout,))
        print 'wrote logout message'
        self.dropConnection('orderly waving goodbye')

    def wave_and_logout(self,):
        self.factory.broadcast('%s waves goodbye again.' % \
                                        (self.user.name,), (self.user.name,)) 
        self.transport.write('You wave goodbye again and log out.\r\n')
        self.logout()

    def tell(self, msg):
        self.transport.write('%s\r\n' % (msg,))

class Simple:
    """Protokoll für Testzwecke."""
    def __init__(self, user_name='unknown'):
        self.prefix = 'TELL %s:' % user_name
    def tell(self, msg):
        print self.prefix, msg
