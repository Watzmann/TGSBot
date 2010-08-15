#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

import time
from game import getGame
from command import NYI

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}

    def get_active_users(self):
        return self.list_of_active_users
    
    def add(self, user):
        self.list_of_active_users[user.name] = user
        # TODO: Fehler, wenn bereits logged in

    def drop(self, name):
        del self.list_of_active_users[name]
        # TODO: Fehler, wenn name not logged in

    def get(self, name, default=None):
        return self.list_of_active_users.get(name, default)

    def get_all_users(self,):
        return self.list_of_active_users.values()

class Info:
    def __init__(self,):
##        self.login = time.asctime(time.localtime(time.time()-150000))
        self.login = int(time.time()-150000)
        self.host = 'some.host.nyi' # % NYI

    def set_login_data(self, login, host):
        self.last_login = self.login
        self.login = login
        self.last_host = self.host
        self.host = host

class Status:
    def __init__(self,):
        self.status = 'ready'

class Settings:
    def __init__(self,):
        self._boardstyle = 3

    def boardstyle(self, *values):
        vals = values[0]
        print 'boardstyle', vals
        if len(vals) == 0:
            return "Value of 'boardstyle' is %d" % self._boardstyle
        elif vals[0] in ('1','2','3'):
            self._boardstyle = int(vals[0])
            return "Value of 'boardstyle' set to %d." % self._boardstyle
##            return "set boardstyle %d" % self._boardstyle
        else:
            return "set boardstyle bad_value"

class User:
    def __init__(self, name, pw):
        self.name = name
        self.password = pw
        self.info = Info()
        self.status = Status()
        self.settings = Settings()
        self.invitations = {}   # TODO: wegen der Persistenz muss ich User()
                        # vielleicht wrappen, damit der Kern - User() - deep
                        # gespeichert werden kann und dynamical stuff wie
                        # invitations oder games nicht gespeichert werden.
        self.dice = 'random'
        print 'This is USER %s with pw %s' % (name, '*'*len(pw))

    def set_protocol(self, protocol):
        self.protocol = protocol

    def set_login_data(self, login_time):
        host = self.protocol.factory.host()
        self.info.set_login_data(login_time, host)

    def tell(self, user, msg):
        user.chat('%s tells: %s' % (self.name, msg))

    def chat(self, msg):
        self.protocol.tell(msg)

    def who(self,):
        args = {}
        args['user'] = self.name
        args['opponent'] = '-'
        args['watching'] = '-'
        args['ready'] = str(1)
        args['away'] = str(0)
        args['rating'] = str(1623.54)
        args['experience'] = str(594)
        args['idle'] = str(0.2)
        args['login'] = str(int(time.time() - 10000))
        args['hostname'] = 'some.host.sibs'
        args['client'] = '-'
        args['email'] = '-'
        w = '5 %(user)s %(opponent)s %(watching)s %(ready)s ' \
            '%(away)s %(rating)s %(experience)s %(idle)s %(login)s ' \
            '%(hostname)s %(client)s %(email)s' % args
        return w
##        return "Ei, isch bin dae %s" % self.name

    def invite(self, name, ML):
        self.invitations[name] = ML
        
    def join(self, invited_and_joining, list_of_games):
        ML = self.invitations.get(invited_and_joining.name, None)
        for i in ['5 Watzmann sorrytigger - 1 0 1547.30 20 74 1280588416 88-134-122-10-dynip.superkabel.de ?NT________________! -',
                  '6',
                  '5 sorrytigger Watzmann - 1 0 1805.07 11647 4 1281040244 88-134-122-10-dynip.superkabel.de ?NT________________! -',
                  '6',
                  ]:
            self.chat(i)
            print i
        if not ML is None:
            kw = {'player1':self, 'player2':invited_and_joining}
            kw['ML'] = ML
            kw['dice'] = self.dice
            kw['list_of_games'] = list_of_games
            self.running_game,invited_and_joining.running_game = getGame(**kw)

    def welcome(self,):
        info = self.info
        return '1 %s %s %s' % (self.name, info.last_login, info.last_host)

    def own_info(self,):
        return '2 %s 1 1 0 0 0 0 1 1 2396 0 1 0 1 3457.85 0 0 0 0 0 ' \
                'Australia/Melbourne' % self.name

    def drop_connection(self,):
        self.protocol.factory.broadcast('8 %s %s drops connection' % \
                                        (self.name,self.name)) 
    
    def __str__(self,):
        return self.who()

def getUser(**kw):
    name = kw['user']
    user = User(name, kw['password'])
    # TODO: if user valid:
    kw['lou'].add(user)
    return user

def dropUser(**kw):
    kw['lou'].drop(kw['user'])
