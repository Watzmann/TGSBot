#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}

    def add(self, user):
        self.list_of_active_users[user.name] = user
        # TODO: Fehler, wenn bereits logged in

    def get(self, name, default=None):
        return self.list_of_active_users.get(name, default)

class User:
    def __init__(self, name, pw):
        self.name = name
        self.password = pw
        print 'This is USER %s with pw %s' % (name, '*'*len(pw))

    def set_protocol(self, protocol):
        self.protocol = protocol

    def tell(self, user, msg):
        user.chat('%s tells: %s' % (self.name, msg))

    def chat(self, msg):
        self.protocol.tell(msg)
        
def getUser(**kw):
    name = kw['user']
    user = User(name, kw['password'])
    # TODO: if user valid:
    kw['lou'].add(user)
    return user
