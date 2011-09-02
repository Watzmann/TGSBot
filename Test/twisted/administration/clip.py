#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementation of the CLIP CLIent Protocol as specified by the
CLIP specification V 1.008 - 08 Mar 1997
"""

REV = '$Revision$'

import time
from twisted.internet.protocol import Protocol
import sibs_utils as utils
from tz_utils import TZ

ZONEINFO = TZ()
##from twisted.python import log                TODO: logging

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

class AdminCLIP(Echo):
    def __init__(self,):
        self.buffer = ''
        self.myDataReceived = self.established
        self.scheduled_broadcasts = []
        
    def connectionMade(self):
        Echo.connectionMade(self,)
        self.client_host = self.transport.hostname
        msg = utils.render_file('intro').splitlines()
        msg += [ZONEINFO.long_time(zone='MET'),]
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
        # TODO: this data collection stuff is most likely unneccessary
        #       deriving from LineReceiver would probably do (investigate!!)
        if self.buffer.endswith('\n'):
            d = self.buffer
            self.buffer = ''
            if hasattr(self, 'user') and not self.user is None:
                self.user.status.stamp()
            for dp in d.split('\n'):
                ds = dp.rstrip('\r\n')
                if ds:
                    self.myDataReceived(ds)
        
    def established(self, data):    # TODO: this is the proper place to
                                    #       differenciate between administrator
                                    #       Clients and telnet
                                    #       Simply use other "established"s
        self.dropConnection('no entry')
##        result = self.factory.parse(data, self.user)
##        if not result is None:
##            self.transport.write('%s\r\n' % (result,))
##            for b in self.scheduled_broadcasts:
##                self.factory.broadcast(b)
##            self.scheduled_broadcasts = []      # TODO: besser in call_later???

    def cycle_message(self, msg):
        for m in msg:
            self.transport.write('%s\r\n' % m)

##    def service(self, data):
##        """The part, where the administrator comes in."""
##        print 'admin says:', data
##        result = self.factory.service(data, self)
##        if not result is None:
##            self.transport.write('%s\r\n' % (result,))
##        self.transport.write('# ')
##
##    def authentication(self, data):
##        self.login_time = int(time.time())
##        success = False
##        try:                                    # TODO: dient nur dem logging
##            log_data = data.split()[:-1]        #       ohne passwort
##        except:                                 #       Das soll langfristig raus
##            log_data = data
##        print 'in auth with', log_data
##        if data.startswith('guest'):    # TODO: should be possible for more than
##                                        #       one to register at the same time
##            print 'in guest cycle'
##            welcome = utils.render_file('guest_intro').splitlines()
##            self.cycle_message(welcome)
##            self.transport.write('> ')
##            self.myDataReceived = self.registration
##            success = True
##        elif data.startswith('login'):
##            #login <client_name> <clip_version> <name> <password>\r\n
##            d = data.split()[1:]
##            if len(d) > 3:
##                print 'Login process with', d[:-1], '*******'
##                kw = {'client':d[0], 'clip_version':d[1], 'user':d[2],
##                      'password':d[3], 'lou':self.factory.active_users,
##                      }
##                self.user = getUser(**kw)
##                if not self.user is None:
##                    if self.user.online():
##                        self.transport.write(
##                            "** Warning: You are already logged in.\r\n")
##                        if self.user.tried_second_login():
##                            print 'disconnecting',self.user.name,'for second login'
##                            self.user.disconnect_hard()
##                            self.user = getUser(**kw)
##                            self.user.set_second_login(0)
##                        else:
##                            self.user.set_second_login(1)
##                    if not self.user.online():
##                        self.user.set_protocol(self)
##                        self.user.set_login_data(self.login_time,
##                                                 self.client_host)
##                        self.user.status.stamp()
##                        self.welcome(self.user)
##                        name = self.user.name
##                        self.user.status.logged_in = True
##                        self.myDataReceived = self.established
##                        success = True
##                        self.factory.broadcast('7 %s %s logs in' % (name, name),
##                                               exceptions=(name,))
##                        # TODO: beachte toggle notify (see CLIP who info)
##                        who = self.user.who() + '\n6\n'
##                        self.factory.broadcast(who,)
##                        # TODO: evtl. ist die letzte msg nicht korrekt;
##                        #       siehe CLIP Who Info 
##                else:
##                    print 'user not known or wrong password'
##                    # TODO: evtl. hier JavaFIBS rausschmeissen
##                    self.transport.write(
##                            "** User not known or wrong password.\r\n")
##                    del self.user
##                    self.dropConnection('user not known or wrong pw')
##            else:
##                reason = 'Login process cancelled - ' \
##                         'not enough paramaeters (%d)' % len(d)
##        elif data.startswith('administration'):
##            print 'in administration cycle'
##            self.transport.write('send key > ')
##            self.myDataReceived = self.administration
##            success = True
##        elif isUser(user=data, lou = self.factory.active_users):
##            print 'here goes telnet login'
##            success = False
##        else:
##            print 'falscher Befehl - kein login'
##        if not success:
##            self.transport.write('login: ')
##
##    def registration(self, data):
##        success = False
##        data = data.lstrip("\xff\xfe\xfd\xfb\x01")
##        print "in registration with '%s' (len:%d) (%s)" % (data, len(data), data.split())
##        d = data.split()
##        if len(d) > 0:
##            if d[0] == 'bye':
##                self.logout('guest')            # closing connection
##            elif d[0] == 'name' and len(d) > 1:
##                name = d[1]
##                print "trying '%s'" % name      # TODO: das Folgende auslagern nach lou
##                if (name in RESERVED_Users) or \
##                   (not self.factory.active_users.get_from_all(name) is None):
##                    msg = "** Please use another name. '%s' is already " \
##                            "used by someone else." % name
##                    self.transport.write('%s\r\n' % (msg,))
##                    print 'rejected: name already in use'
##                # TODO:
####                elif name is not valid:
####                    msg = "** Your name may only contain letters and " \
####                              "the underscore character _ ."
####                    self.transport.write('%s\r\n' % (msg,))
##                else:
##                    msg = ["Your name will be '%s'" % name,]
##                    msg.append("Type in no password and hit Enter/Return if " \
##                                "you want to change it now.")
##                    self.cycle_message(msg)
##                    self.transport.write("\xff\xfb\x01Please give your password: ")
##                    self.myDataReceived = self.chose_password
##                    self.name = name
##                    success = True
##        if not success:
##            self.transport.write('> ')
##
##    def chose_password(self, data):
##        self.transport.write("\r\n")
##        data = data.lstrip("\xff\xfe\xfd\xfb\x01")
##        pw_file = open('.pw_data', 'a')
##        pw_file.write('>%s< length %d\n' % (data,len(data)))
##        pw_file.close()
##        if data == '':
##            self.transport.write("\xff\xfc\x01** No password given. " \
##                                 "Please choose a new name\r\n")
##            self.transport.write('> ')
##            self.myDataReceived = self.registration
##        elif not hasattr(self,'password'):
##            d = data.split()
####            print 'caught %d (%s)' % (len(d),d)
##            # TODO:  if fucking consistent (len 4, nur blanks, ....)
##            self.password = d[0]
##            self.transport.write("Please retype your password: ")
##        else:
##            d = data.split()
##            if data == '' or len(d) == 0 or d[0] != self.password:
##                self.transport.write("** The two passwords were not " \
##                                     "identical. Please give them again. " \
##                                     "Password:")
##            elif d[0] == self.password:
##                kw = {'user': self.name, 'password': '*******',
##                      'lou': self.factory.active_users,
##                      'login': self.login_time,
##                      'host': self.client_host}
##                print 'ERFOLG', kw
##                kw['password'] = self.password
##                self.user = newUser(**kw)
##                success = True
##                self.user.set_protocol(self)
##                self.user.status.logged_in = True
##                self.myDataReceived = self.established
##                name = self.user.name
##                self.factory.broadcast('7 %s %s logs in' % (name, name),
##                                       exceptions=(name,))
##                # TODO: beachte toggle notify (see CLIP who info)
##                who = self.user.who() + '\n6\n'
##                self.factory.broadcast(who, exceptions=(name,))
##                self.transport.write("\xff\xfc\x01\nYou are registered.\n" \
##                                 "Type 'help beginner' to get started.\n> ")
##
##    def administration(self, data):
##        key = utils.render_file('admin_key').rstrip('\n')
##        if data == key:
##            print 'admitted'
##            self.transport.write('hello sir :)\r\n')
##            self.myDataReceived = self.service
##            self.transport.write('# ')
##            success = True
##        else:
##            print key + '<'
##            print data + '<'
##            print 'wrong key'
##            success = False
##
##    def logout(self, special_name=''):
##        user = getattr(self,'user',None)
##        if not user is None:
##            name = self.user.name
##        else:
##            name = special_name
##        logout = utils.render_file('extro') + utils.render_file('about')
##        self.transport.write('%s\r\n' % (logout,))
##        print 'wrote logout message'
##        self.dropConnection('orderly waving goodbye')
##
##    def wave_and_logout(self,):
##        self.factory.broadcast('%s waves goodbye again.' % \
##                                        (self.user.name,), (self.user.name,)) 
##        self.transport.write('You wave goodbye again and log out.\r\n')
##        self.logout()
##
##    def tell(self, msg):
##        self.transport.write('%s\r\n' % (msg,))
##
##    def welcome(self, user):
##        welcome = ['', user.welcome()]
##        welcome.append(user.own_info())
##        welcome.append(self.factory.command.c_version(['',], self.user))
##        welcome += utils.render_file('motd').splitlines()
##        welcome += user.deliver_messages()
##        who = self.factory.command.c_rawwho(['rawwho',], self.user)
##        welcome += [who,]
##        self.cycle_message(welcome)
##
##    def cycle_message(self, msg):
##        for m in msg:
##            self.transport.write('%s\r\n' % m)
##
##    def schedule_broadcast(self, msg):
##        self.scheduled_broadcasts.append(msg)
##
##class Simple:
##    """Protokoll für Testzwecke."""
##    def __init__(self, user_name='unknown'):
##        self.prefix = 'TELL %s:' % user_name
##        self.quiet = True
##
##    def tell(self, msg):
##        if not self.quiet:
##            print self.prefix, msg
