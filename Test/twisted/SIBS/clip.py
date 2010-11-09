#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementation of the CLIP CLIent Protocol as specified by the
CLIP specification V 1.008 - 08 Mar 1997
"""

REV = '$Revision$'

import time
from twisted.internet.protocol import Protocol
##from twisted.python import log
from sibs_user import getUser, dropUser, newUser, RESERVED_Users
import sibs_utils as utils
from version import Version

v = Version()
v.register(__name__, REV)

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
        self.myDataReceived = self.authentication
        self.scheduled_broadcasts = []
        
    def connectionMade(self):
        Echo.connectionMade(self,)
        self.client_host = self.transport.hostname
##        print 'TEST HOST', self.transport.__dict__.keys(), \
##              ['%s: %s   ' % (n,getattr(self.transport, n)) for n in \
##               ('hostname','server','client','connected')] 
        msg = utils.render_file('intro').splitlines()
        # TODO:     folgender Timestamp im Format
        # Thursday, January 02 01:27:27 MET   ( Thu Jan  2 00:27:27 2003 UTC )
        msg += [time.asctime(time.localtime(time.time())) + ' ' + \
                time.asctime(time.gmtime(time.time())),]
        self.cycle_message(msg)
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
        if self.buffer.endswith('\n'):
            d = self.buffer
            self.buffer = ''
            ds = d.rstrip('\r\n')
            if hasattr(self, 'user'):
                self.user.status.stamp()
            else:
                print 'GUT ZU WISSEN, ES GIBT KEINEN USER'   #TODO  wegmachen
            self.myDataReceived(ds)
        
    def established(self, data):
        print 'heard:', data
        result = self.factory.parse(data, self.user)
        if not result is None:
            self.transport.write('%s\r\n' % (result,))
            for b in self.scheduled_broadcasts:
                self.factory.broadcast(b)
            self.scheduled_broadcasts = []      # TODO: wird hier viel garbadge erzeugt??

    def authentication(self, data):
        self.login_time = int(time.time())
        success = False
        try:                                    # TODO: dient nur dem logging
            log_data = data.split()[:-1]        #       ohne passwort
        except:                                 #       Das soll langfristig raus
            log_data = data
        print 'in auth with', log_data
        if data.startswith('guest'):
                print 'in guest cycle'
                welcome = utils.render_file('guest_intro').splitlines()
                self.cycle_message(welcome)
                self.transport.write('> ')
                self.myDataReceived = self.registration
                success = True
        elif data.startswith('login'):
            #login <client_name> <clip_version> <name> <password>\r\n
            d = data.split()[1:]
            if len(d) > 3:
                print 'Login process with', d[:-1], '*******'
                kw = {'client':d[0], 'clip_version':d[1], 'user':d[2],
                      'password':d[3], 'lou':self.factory.active_users,
                      }
                self.user = getUser(**kw)
                if self.user == 1:
                    self.transport.write(
                        "** Warning: You are already logged in.\r\n")
                    success = True
                elif not self.user is None:
                    self.user.set_protocol(self)
                    self.user.set_login_data(self.login_time,
                                             self.client_host)
                    self.user.status.stamp()
                    self.welcome(self.user)
                    name = self.user.name
                    self.user.status.logged_in = True
                    self.myDataReceived = self.established
                    success = True
                    self.factory.broadcast('7 %s %s logs in' % (name, name),
                                           exceptions=(name,))
                    who = self.factory.command.c_rawwho(['rawwho',],
                                                self.user, user=self.user)
                    self.factory.broadcast(who, exceptions=(name,))
                    # TODO: evtl. ist die letzte msg nicht korrekt; aber wie
                    #       erfahren die clients sonst vom login?
                    #       vielleicht telnet clients ausnehmen?
                    #       beachte toggle notify
                    #       siehe CLIP Who Info 
                else:
                    print 'user not known or wrong password'
            else:
                reason = 'Login process cancelled - ' \
                         'not enough paramaeters (%d)' % len(d)
        else:
            print 'falscher Befehl - kein login'
        if not success:
            self.transport.write('login: ')

    def registration(self, data):
        success = False
        data = data.lstrip("\xff\xfe\xfd\xfb\x01")
        print "in registration with '%s' (len:%d) (%s)" % (data, len(data), data.split())
        d = data.split()
        if len(d) > 0:
            if d[0] == 'bye':
                self.logout('guest')            # closing connection
            elif d[0] == 'name' and len(d) > 1:
                name = d[1]
                print "trying '%s'" % name
                if (name in RESERVED_Users) or \
                   (not self.factory.active_users.get_from_all(name) is None):
                    msg = "** Please use another name. '%s' is already " \
                            "used by someone else." % name
                    self.transport.write('%s\r\n' % (msg,))
                # TODO:
##                elif name is not valid:
##                    msg = "** Your name may only contain letters and " \
##                              "the underscore character _ ."
##                    self.transport.write('%s\r\n' % (msg,))
                else:
                    msg = ["Your name will be '%s'" % name,]
                    msg.append("Type in no password and hit Enter/Return if " \
                                "you want to change it now.")
                    self.cycle_message(msg)
                    self.transport.write("\xff\xfb\x01Please give your password: ")
                    self.myDataReceived = self.chose_password
                    self.name = name
                    success = True
        if not success:
            self.transport.write('> ')

    def chose_password(self, data):
        self.transport.write("\r\n")
        data = data.lstrip("\xff\xfe\xfd\xfb\x01")
        pw_file = open('.pw_data', 'a')
        pw_file.write('>%s< length %d\n' % (data,len(data)))
        pw_file.close()
        if data == '':
            self.transport.write("\xff\xfc\x01** No password given. " \
                                 "Please choose a new name\r\n")
            self.transport.write('> ')
            self.myDataReceived = self.registration
        elif not hasattr(self,'password'):
            d = data.split()
##            print 'caught %d (%s)' % (len(d),d)
            # TODO:  if fucking consistent (len 4, nur blanks, ....)
            self.password = d[0]
            self.transport.write("Please retype your password: ")
        else:
            d = data.split()
            if data == '' or len(d) == 0 or d[0] != self.password:
                self.transport.write("** The two passwords were not " \
                                     "identical. Please give them again. " \
                                     "Password:")
            elif d[0] == self.password:
                kw = {'user': self.name, 'password': '*******',
                      'lou': self.factory.active_users,
                      'login': self.login_time}
                print 'ERFOLG', kw
                kw['password'] = self.password
                user = newUser(**kw)
                success = True
                self.transport.write("\xff\xfc\x01\nYou are registered.\n" \
                                 "Type 'help beginner' to get started.\n> ")

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
        welcome += [user.own_info(),]
        welcome += utils.render_file('motd').splitlines()
        # TODO: hier statt fake_messages die echten messages ausgeben
        welcome += user.deliver_messages() #utils.render_file('fake_message').splitlines()
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
