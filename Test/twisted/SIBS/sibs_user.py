#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

from game import getGame

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}

    def get_active_users(self):
        return self.list_of_active_users
    
    def add(self, user):
        self.list_of_active_users[user.name] = user
        # TODO: Fehler, wenn bereits logged in

    def get(self, name, default=None):
        return self.list_of_active_users.get(name, default)

class User:
    def __init__(self, name, pw):
        self.name = name
        self.password = pw
        self.invitations = {}   # TODO: wegen der Persistenz muss ich User()
                        # vielleicht wrappen, damit der Kern - User() - deep
                        # gespeichert werden kann und dynamical stuff wie
                        # invitations oder games nicht gespeichert werden.
        print 'This is USER %s with pw %s' % (name, '*'*len(pw))

    def set_protocol(self, protocol):
        self.protocol = protocol

    def tell(self, user, msg):
        user.chat('%s tells: %s' % (self.name, msg))

    def chat(self, msg):
        self.protocol.tell(msg)

    def who(self,):
        return "Ei, isch bin dae %s" % self.name

    def invite(self, name, ML):
        self.invitations[name] = ML
        
    def join(self, invited_and_joining, list_of_games):
        ML = self.invitations.get(invited_and_joining.name, None)
        if not ML is None:
            kw = {'player1':self, 'player2':invited_and_joining}
            kw['ML'] = ML
            kw['list_of_games'] = list_of_games
            self.running_game,invited_and_joining.running_game = getGame(**kw)
            # wenn ich Info brauch, ob player1 oder player2, mach ich 2 IDs auf
            # dasselbe game

    def __str__(self,):
        return self.who()

def getUser(**kw):
    name = kw['user']
    user = User(name, kw['password'])
    # TODO: if user valid:
    kw['lou'].add(user)
    return user
