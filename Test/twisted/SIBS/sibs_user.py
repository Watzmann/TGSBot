#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

import time
from StringIO import StringIO
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

class Toggles:
    toggle_names = (
            'allowpip', 'autoboard', 'autodouble', 'automove', 'bell',
            'crawford', 'double', 'greedy', 'moreboards', 'moves', 'notify',
            'ratings', 'ready', 'report', 'silent', 'telnet', 'wrap',
            )
    toggle_on_msgs = (
            "** You allow the use the server's 'pip' command.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            
            "** You want to see a correct message here.",
            "** You want to see a correct message here.",
            )
    toggle_off_msgs = (
            "** You don't allow the use the server's 'pip' command.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",

            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",

            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",

            "** You don't want to see an incorrect message here.",
            "** You don't want to see an incorrect message here.",
            )
    toggle_msg = {
            True: dict(zip(toggle_names, toggle_on_msgs)),
            False: dict(zip(toggle_names, toggle_off_msgs))
            }

    def __init__(self,):
        self._std = (
            True, True, False, True, False, True, True, False,
            True, False, True, False, False, False, False, True, False,
            )
        self._switches = dict(zip(Toggles.toggle_names, self._std))

    def toggle(self, switch):
        self._switches[switch] = not self._switches[switch]
        return Toggles.toggle_msg[self._switches[switch]][switch]

    def has(self, switch, default=None):
        return {True: switch, False: default}[switch in self._switches]

    def show(self,):
        out = StringIO()
        print >>out, 'The current settings are:'
        keys = self._switches.keys()
        keys.sort()
        for k in keys:
            print >> out, '%-16s%s' % \
                  (k, {True: 'YES', False: 'NO'}[self._switches[k]])
        return out.getvalue()        

class Settings:
    def __init__(self,):
        self._boardstyle = 3
        self._linelength = 0
        self._pagelength = 0
        self._redoubles = 'none'
        self._sortwho = 'name'
        self._timezone = 'UTC'

    # TODO: die methoden hier kann man stark vereinfachen!!!
    #       etwas programmierarbeit

    def boardstyle(self, *values):
        vals = values[0]
##        print 'boardstyle', vals
        if len(vals) == 0:
            res = "Value of 'boardstyle' is %d" % self._boardstyle
        elif vals[0] in ('1','2','3'):
            self._boardstyle = int(vals[0])
            # TODO: hier und in den xxxxlength() muss int() getrapped werden
            res = "Value of 'boardstyle' set to %d." % self._boardstyle
        else:
            res = "** Valid arguments are the numbers 1 to 3."
        return res

    def linelength(self, *values):
        vals = values[0]
##        print 'linelength', vals
        if len(vals) == 0:
            res = "Value of 'linelength' is %d" % self._linelength
        elif int(vals[0]) >= 0 and int(vals[0]) < 1000:
            self._linelength = int(vals[0])
            res = "Value of 'linelength' set to %d." % self._linelength
        else:
            res = "** Valid arguments are the numbers 0 to 999. " \
                  "Use 0 for no linelength."
        return res

    def pagelength(self, *values):
        vals = values[0]
##        print 'pagelength', vals
        if len(vals) == 0:
            res = "Value of 'pagelength' is %d" % self._pagelength
        elif int(vals[0]) >= 0 and int(vals[0]) < 1000:
            self._pagelength = int(vals[0])
            res = "Value of 'pagelength' set to %d." % self._pagelength
        else:
            res = "** Valid arguments are the numbers 0 to 999. " \
                  "Use 0 for no pagelength."
        return res

    def redoubles(self, *values):
        vals = values[0]
##        print 'redoubles', vals
        if len(vals) == 0:
            res = "Value of 'redoubles' is %s" % self._redoubles
        elif (vals[0] in ('none', 'unlimited')) or \
                (int(vals[0]) >= 0 and int(vals[0]) < 100):
            self._redoubles = vals[0]
            res = "Value of 'redoubles' set to %s." % self._redoubles
        else:
            res = "** Valid arguments are 'none', 'unlimited' and" \
                  "the numbers 0 to 99."
        return res

    def sortwho(self, *values):
        vals = values[0]
##        print 'sortwho', vals
        if len(vals) == 0:
            res = "Value of 'sortwho' is %s" % self._sortwho
        elif vals[0] in ('login', 'name', 'rating', 'rrating'):
            self._sortwho = vals[0]
            res = "Value of 'sortwho' set to %s." % self._sortwho
        else:
            res = "** Unknown value '%s'. Try 'login', 'name', " \
                  "'rating' or 'rrating'." % vals[0]
        return res

    def timezone(self, *values):
        vals = values[0]
##        print 'timezone', vals
        if len(vals) == 0:
            res = "Value of 'timezone' is %s" % self._timezone
        elif vals[0] in ('UTC', ):
            self._timezone = int(vals[0])
            res = "Value of 'timezone' set to %s." % self._timezone
        else:
            res = "Can't find timezone '%s'. Try one of: " \
                    "Africa/Abidjan, Africa/Accra, Africa/Addis_Ababa, Africa/Algiers," \
                    "Africa/Asmera, Africa/Bamako, Africa/Bangui, Africa/Banjul, Africa/Bissau," \
                    % vals[0]
        return res

    def show(self,):    # TODO
        return "UND HIER MAL WAS GANZ ANDERES"

class User:
    def __init__(self, name, pw):
        self.name = name
        self.password = pw
        self.info = Info()
        self.status = Status()
        self.settings = Settings()
        self.toggles = Toggles()
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

    def whois(self,):
        args = {}
        args['name'] = self.name
        args['date'] = "Tuesday, January 14 20:27 EST"
        args['last_login_details'] = "Still logged in. 4:48 minutes idle"
        args['play_status'] = "%s is not ready to play, not watching, not playing." % self.name
        args['away_status'] = "user is away:"
        args['rating_exp'] = "Rating: 1300.45 Experience: 1000"
        args['email'] = "mail-adress"
        
        return """Information about %(name)s:
  Last login:  %(date)s from p987987.dip.t-dialin.net
  %(last_login_details)s
  %(play_status)s
  %(rating_exp)s
  Email address: %(email)s""" % args

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
