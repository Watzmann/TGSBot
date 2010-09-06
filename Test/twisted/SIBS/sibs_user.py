#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

REV = '$Revision$'

import time
from StringIO import StringIO
from game import getGame
from command import NYI
from persistency import Persistent, Db
from version import Version

v = Version()
v.register(__name__, REV)

DB_Users = 'db/users'
RESERVED_Users = ('guest', 'systemwart', 'administrator')
## TODO: RESERVED_Users gehören nicht in OpenSource

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}
        self.db = all_users = Db(DB_Users).db
        self.list_of_all_users = dict([(k,self.restore(all_users[k])) \
                                       for k in all_users.keys()])
        for e,k in enumerate(self.list_of_all_users.keys()):
            print e,k

    def get_active_users(self):
        return self.list_of_active_users

    def get_user(self, name, password):
        if self.list_of_active_users.has_key(name):
            return 1    # user is already logged in and get's a warning
        user = self.list_of_all_users.get(name, None)
        if (not user is None) and (user.info.passwd != password):
            print 'found user', user.name
            print 'wrong password:', password
            user = None
        return user

    def restore(self, user_data):
        user = User(user_data)
        ## TODO: auf restore() könnte man verzichten; andererseits kann man
        ##       jetzt hier spezielle Aktionen durchführen
        return user

    def add(self, user):
        self.list_of_all_users[user.name] = user

    def online(self, user):
        self.list_of_active_users[user.name] = user

    def drop(self, name):
        print 'deleting %s from list of active users' % name
        user = self.list_of_active_users[name]
        user.save()   # TODO:   muss das save hier sein??????
        del self.list_of_active_users[name]
        # TODO: Fehler, wenn name not logged in

    def get_from_all(self, name, default=None):
        return self.list_of_all_users.get(name, default)

    def get_active(self, name, default=None):
        return self.list_of_active_users.get(name, default)

    def get_all_users(self,):
        return self.list_of_active_users.values()

class Info:
    """Info soll selbst so wenig Methoden als möglich haben und lediglich
als Datencontainer dienen."""
    def __init__(self, data, toggles, settings, messages):
##        self.login = time.asctime(time.localtime(time.time()-150000))
##        self.login = int(time.time()-150000)
##        self.host = 'some.host.nyi' # % NYI
##        self.name = name
##        self.passwd = ''
        self.login, self.host, self.name, self.passwd, \
                self.rating, self.experience = data
        self.toggles = toggles
        self.settings = settings
        self.messages = messages

    def set_login_data(self, login, host):
        self.last_login = self.login
        self.login = int(login)
        self.last_host = self.host
        self.host = host

    def set_rating(self, rating, experience):
        self.rating = rating
        self.experience = experience

    def message(self, msg):
        """message() is used for persistency of messages."""
        self.messages.append(msg)
        print 'message:', msg

    def show(self,):
        out = StringIO()
        v = self
        print >>out, v.login, v.host, v.name, v.passwd, v.rating, v.experience
        print >>out,v.toggles.values()
        print >>out,v.settings
        return out.getvalue()

    def array(self, battery):
        s = self.toggles
        t = {0: ('allowpip', 'autoboard', 'autodouble', 'automove',),
             1: ('bell', 'crawford', 'double',),
             2: ('greedy', 'moreboards', 'moves', 'notify',),
             3: ('ratings', 'ready',),
             4: ('report', 'silent',),
             }
        return [s[i] for i in t[battery]]

    def __str__(self,):
        _t = {True: '1', False: '0'}
        t = [' '.join([_t[i] for i in self.array(p)]) for p in range(5)]
        ret = '%s %s %s %s %d %s %.2f %s %s %s %s' % \
            (self.name, t[0], '<away>=[0,1]', t[1], self.experience, t[2],
             self.rating, t[3], self.settings[3], t[4], self.settings[5],)
##        ret = '.'.join(t)
        return ret

class Status:
    def __init__(self, toggles):
        self.toggles = toggles
        self.away = False   # TODO: sollte in Info() aufgehen

    def get(self, fmt='int'):
        status = int(self.toggles.read('ready'))
        if fmt == 'str':
            status = ('ready', 'online', 'playing')[status]
        return status

class Toggles:
    toggle_names = (
            'allowpip', 'autoboard', 'autodouble', 'automove', 'bell',
            'crawford', 'double', 'greedy', 'moreboards', 'moves', 'notify',
            'ratings', 'ready', 'report', 'silent', 'telnet', 'wrap',
            )
    toggle_on_msgs = (
            "** You allow the use of the server's 'pip' command.",
            "** The board will be refreshed after every move.",
            "** You agree that doublets during opening double the cube.",
            "** Forced moves will be done automatically.",
            "** Your terminal will ring the bell if someone talks to you or invites you",
            
            "** You insist on playing with the Crawford rule.",
            "** You will be asked if you want to double.",
            "** Will use automatic greedy bearoffs.",
            "** Will send rawboards after rolling.",
            "** You want a list of moves after this game.",
            
            "** You will be notified when new users log in.",
            "** You'll see how the rating changes are calculated.",
            "** You will be informed about starting and ending matches.",
            "** You will hear what other players shout.",
            "** You will be informed about starting and ending matches.",

            "** You use telnet and don't need extra 'newlines'.",
            "** The server will wrap long lines.",
            )
    toggle_off_msgs = (
            "** You don't allow the use the server's 'pip' command.",
            "** The board won't be refreshed after every move.",
            "** You don't agree that doublets during opening double the cube.",
            "** Forced moves won't be done automatically.",
            "** Your terminal won't ring the bell if someone talks to you or invites you",

            "** You would like to play without using the Crawford rule.",
            "** You won't be asked if you want to double.",
            "** Won't use automatic greedy bearoffs.",
            "** Won't send rawboards after rolling.",
            "** You won't see a list of moves after this game.",

            "** You won't be notified when new users log in.",
            "** You won't see how the rating changes are calculated.",
            "** You're now refusing to play with someone.",
            "** You won't be informed about starting and ending matches.",
            "** You won't hear what other players shout.",

            "** You use a client program and will receive extra 'newlines'.",
            "** Your terminal knows how to wrap long lines.",
            )
    toggle_msg = {
            True: dict(zip(toggle_names, toggle_on_msgs)),
            False: dict(zip(toggle_names, toggle_off_msgs))
            }
    toggle_std = (
            True, True, False, True, False, True, True, False,
            True, False, True, False, False, False, False, True, False,
            )

    def __init__(self, info):
        self._switches = info.toggles
        #dict(zip(Toggles.toggle_names, Toggles.toggle_std))

    def toggle(self, switch):
        self._switches[switch] = not self._switches[switch]
        return Toggles.toggle_msg[self._switches[switch]][switch]

    def read(self, switch):
        return self._switches[switch]

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
    def __init__(self, info):
##        self._boardstyle = 3
##        self._linelength = 0
##        self._pagelength = 0
##        self._redoubles = 'none'
##        self._sortwho = 'name'
##        self._timezone = 'UTC'
        self._settings = info.settings
        # TODO: hier sollte statt info DRINGEND nur "settings" übergeben werden.
        #       Diese Abhängigkeit von Info() ist nicht akzeptabel.
        self._boardstyle = info.settings[0]
        self._linelength = info.settings[1]
        self._pagelength = info.settings[2]
        self._redoubles = info.settings[3]
        self._sortwho = info.settings[4]
        self._timezone = info.settings[5]
    # TODO: die methoden hier kann man stark vereinfachen!!!
    #       etwas programmierarbeit

##    def settings(self,):
##        return [self._boardstyle, self._linelength, self._pagelength,
##                self._redoubles, self._sortwho, self._timezone]
##    
    def boardstyle(self, *values):
        vals = values[0]
##        print 'boardstyle', vals
        if len(vals) == 0:
            res = "Value of 'boardstyle' is %d" % self._boardstyle
        elif vals[0] in ('1','2','3'):
            self._settings[0] = self._boardstyle = int(vals[0])
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
            self._settings[1] = self._linelength = int(vals[0])
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
            self._settings[2] = self._pagelength = int(vals[0])
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
            self._settings[3] = self._redoubles = vals[0]
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
            self._settings[4] = self._sortwho = vals[0]
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
            self._settings[5] = self._timezone = int(vals[0])
            res = "Value of 'timezone' set to %s." % self._timezone
        else:
            res = "Can't find timezone '%s'. Try one of: " \
                    "Africa/Abidjan, Africa/Accra, Africa/Addis_Ababa, Africa/Algiers," \
                    "Africa/Asmera, Africa/Bamako, Africa/Bangui, Africa/Banjul, Africa/Bissau," \
                    % vals[0]
        return res

    def show(self,):    # TODO
        out = StringIO()
        print >> out, 'Settings of variables:'
        print >> out, '%-12s%d' % ('boardstyle:', self._boardstyle)
        print >> out, '%-12s%s' % ('linelength:', self._linelength)
        print >> out, '%-12s%s' % ('pagelength:', self._pagelength)
        print >> out, '%-12s%s' % ('redoubles:', self._redoubles)
        print >> out, '%-12s%s' % ('sortwho:', self._sortwho)
        print >> out, '%-12s%s' % ('timezone:', self._timezone)
        return out.getvalue()        

class User(Persistent):
    def __init__(self, data):
        Persistent.__init__(self, DB_Users)
        self.info = data
        self.name = self.info.name
        self.settings = Settings(self.info)
        self.toggles = Toggles(self.info)
        self.status = Status(self.toggles)
        self._waves = 0
        self.invitations = {}   # TODO: wegen der Persistenz muss ich User()
                        # vielleicht wrappen, damit der Kern - User() - deep
                        # gespeichert werden kann und dynamical stuff wie
                        # invitations oder games nicht gespeichert werden.
        self.dice = 'random'
        self.db_key = self.name
        self.db_load = self.info

    def set_protocol(self, protocol):
        self.protocol = protocol

    def check_password(self, password):
        return self.info.passwd == password

    def set_password(self, password):
        self.info.passwd = password
        self.save()

    def change_password(self, passwords):
        passwords = passwords.split(':')
        if len(passwords) < 3:
            res = 1
        elif not self.check_password(passwords[0]):
            res = 2
        elif passwords[1] != passwords[2]:
            res = 3
        else:
            self.set_password(passwords[2])
            res = 0
        return res

    def set_login_data(self, login_time, host):
        self.info.set_login_data(login_time, host)
        self.save()

    def tell(self, user, msg):
        user.chat('12 %s %s' % (self.name, msg))
        self.chat('16 %s %s' % (user.name, msg))

    def deliver_messages(self,):
        """Delivers messages when user logs in"""
        msgs = self.info.messages
        self.info.messages = []
        self.save()
        return msgs

    def send_message(self, user, msg):
        """Use send_message() to send a message to another player."""
        user.message(self.name, int(time.time()), msg)

    def message(self, user, at_time, msg):
        """message() will receive a message from another player."""
        # 9 from time message
        self.info.messages.append('9 %s %d %s' % (user, at_time, msg))
        self.save()
        # TODO: if logged in trigger receive_message()

    def chat(self, msg):
        self.protocol.tell(msg)

    def who(self,):
        args = {}
        args['user'] = self.name
        args['opponent'] = '-'          # TODO: richtige Werte verwenden
        args['watching'] = '-'          # TODO: richtige Werte verwenden
        args['ready'] = self.status.get()
        args['away'] = int(self.status.away)
        args['rating'] = str(1623.54)   # TODO: richtige Werte verwenden
        args['experience'] = str(594)   # TODO: richtige Werte verwenden
        args['idle'] = str(0.2)         # TODO: richtige Werte verwenden
        args['login'] = str(int(time.time() - 10000))  # TODO: richtige Werte verwenden
        args['hostname'] = 'some.host.sibs'  # TODO: richtige Werte verwenden
        args['client'] = '-'            # TODO: richtige Werte verwenden
        args['email'] = '-'             # TODO: richtige Werte verwenden
        w = '5 %(user)s %(opponent)s %(watching)s %(ready)s ' \
            '%(away)s %(rating)s %(experience)s %(idle)s %(login)s ' \
            '%(hostname)s %(client)s %(email)s' % args
        return w

    def whois(self,):
        # TODO: richtige Werte verwenden
        args = {}
        args['name'] = self.name
        args['date'] = "Tuesday, January 14 20:27 EST"
        args['last_login_details'] = "Still logged in. 4:48 minutes idle"
        args['play_status'] = "%s is not ready to play, not watching, not playing." % self.name
        if self.status.away:
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
        # TODO: richtige Werte verwenden
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
        return '2 %s' % str(self.info)

    def drop_connection(self,):
        self.protocol.factory.broadcast('8 %s %s drops connection' % \
                                        (self.name,self.name), (self.name,)) 

    def wave(self,):
        if self._waves == 0:
            self._waves += 1
            self.protocol.factory.broadcast('%s waves goodbye.' % \
                                        (self.name,), (self.name,)) 
            return 'You wave goodbye.'
        else:
            self.protocol.wave_and_logout()

    def __str__(self,):
        return self.who()

def newUser(**kw):
    data = (kw['login'],'',kw['user'],kw['password'],1500.,0)
    toggles = dict(zip(Toggles.toggle_names, Toggles.toggle_std))
    settings = [3, 0, 0, 'none', 'name', 'UTC']
    messages = []
    info = Info(data, toggles, settings, messages)
    user = User(info)
    user.save()
    kw['lou'].add(user)
    return user

def getUser(**kw):
    lou = kw['lou']
    user = lou.get_user(kw['user'], kw['password'])
    if not user is None and not user == 1:
        lou.online(user)
    return user

def dropUser(**kw):
    kw['lou'].drop(kw['user'])
