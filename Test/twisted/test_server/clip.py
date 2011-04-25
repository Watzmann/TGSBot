#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementation of the CLIP CLIent Protocol as specified by the
CLIP specification V 1.008 - 08 Mar 1997
"""

from twisted.internet.protocol import Protocol
from twisted.python import log

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
        # TODO:  wenn die connection lost ist (z.B. disconnect in client),
        #        dann sollte aber der user auch aus der liste gedroppt werden.
        print 'aus die maus', self.id

class CLIP(Echo):
    def __init__(self,):
        self.buffer = ''
        self.myDataReceived = self.established
        self.scheduled_broadcasts = []
        
    def connectionMade(self):
        Echo.connectionMade(self,)
        self.client_host = self.transport.hostname
        self.transport.write('login: ')

    def dropConnection(self, reason):
        user = getattr(self, 'user', None)
        if not user is None:
            print 'dropping user', user.name
            self.user.drop_connection()
            dropUser(user=user.name, lou = self.factory.active_users)
            del self.user
        Echo.dropConnection(self, reason)

    def connectionLost(self, reason):
        user = getattr(self, 'user', None)
        if not user is None:
            print 'dropping lost user', user.name
            self.user.drop_connection()
            dropUser(user=user.name, lou = self.factory.active_users)
        Echo.connectionLost(self, reason)

    def dataReceived(self, data):
        self.buffer += data
        # TODO: this data collection stuff is most likely unneccessary
        #       deriving from LineReceiver would probably do (investigate!!)
        print 'raw:  ', tuple(data)
        if self.buffer.endswith('\n'):
            d = self.buffer
            self.buffer = ''
            ds = d.rstrip('\r\n')
            print ds
        
    def established(self, data):    # TODO: this is the proper place to
                                    #       differenciate between administrator
                                    #       Clients and telnet
                                    #       Simply use other "established"s
        print 'heard:', data
        result = self.factory.parse(data, self.user)
        if not result is None:
            self.transport.write('%s\r\n' % (result,))
            for b in self.scheduled_broadcasts:
                self.factory.broadcast(b)
            self.scheduled_broadcasts = []      # TODO: wird hier viel garbage erzeugt??

    def logout(self, special_name=''):
        user = getattr(self,'user',None)
        if not user is None:
            name = self.user.name
        else:
            name = special_name
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

    def welcome(self, user):
        welcome = ['', user.welcome()]
        welcome.append(user.own_info())
        welcome.append(self.factory.command.c_version(['',], self.user))
        welcome += utils.render_file('motd').splitlines()
        welcome += user.deliver_messages()
        who = self.factory.command.c_rawwho(['rawwho',], self.user)
        welcome += [who,]
        self.cycle_message(welcome)

    def cycle_message(self, msg):
        for m in msg:
            self.transport.write('%s\r\n' % m)

    def schedule_broadcast(self, msg):
        self.scheduled_broadcasts.append(msg)

class Simple:
    """Protokoll für Testzwecke."""
    def __init__(self, user_name='unknown'):
        self.prefix = 'TELL %s:' % user_name
        self.quiet = True

    def tell(self, msg):
        if not self.quiet:
            print self.prefix, msg
