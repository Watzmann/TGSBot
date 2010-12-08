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

# TODO: Logging

v = Version()
v.register(__name__, REV)

DB_Users = 'db/users'
RESERVED_Users = ('guest', 'systemwart', 'administrator',
                  'sorrytigger', 'tigger', 'Watzmann', 'TigerGammon', 'TiGa')
## TODO: RESERVED_Users gehören nicht in OpenSource

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}
        self.db = all_users = Db(DB_Users, 'users').db  # TODO: hier so an der
                            #   PersistenzKlasse vorbeizuangeln ist schon krass!
        self.list_of_all_users = dict([(k,self.restore(all_users[k])) \
                                       for k in all_users.keys()])
##        for e,k in enumerate(self.list_of_all_users.keys()):
##            print e,k

    criterion = {'away': lambda u: u.is_away(),
                 'ready': lambda u: u.is_ready(),
                 'playing': lambda u: u.is_playing()
                 }
    
    def get_active_users(self,):
        return self.list_of_active_users

    def get_sorted_keys(self, ufilter = '', sort = 'name'):
        users = self.list_of_active_users.values()
        if ufilter in ('away','ready','playing',):
            users = filter(self.criterion[ufilter],
                           self.list_of_active_users.values())
        return {'login': self.sorted_keys_login,
                'name': self.sorted_keys_name,
                'rating': self.sorted_keys_rating,
                'rrating': self.sorted_keys_rrating}[sort](users)

    def sorted_keys_login(self, users):
        keys = [u.name for u in users]
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].info.login,lau[y].info.login)
        return sorted(keys, compare)

    def sorted_keys_name(self, users):
        keys = [u.name for u in users]
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].name,lau[y].name)
        return sorted(keys, compare)

    def sorted_keys_rating(self, users):
        keys = [u.name for u in users]
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].rating(),lau[y].rating())
        return sorted(keys, compare)

    def sorted_keys_rrating(self, users):
        keys = self.sorted_keys_rating(users)
        keys.reverse()
        return keys

    def get_user(self, name, password):
        if self.list_of_active_users.has_key(name): # user is already logged in
            return self.list_of_active_users[name]  # and get's a warning
        user = self.list_of_all_users.get(name, None)
        if (not user is None) and (user.info.passwd != password):
            print 'found user', user.name, 'wrong password'
            user = None
        return user

    def restore(self, user_data):
        user = User(user_data)
        user.status.logged_in = False
        ## TODO: auf restore() könnte man verzichten; andererseits kann man
        ##       jetzt hier spezielle Aktionen durchführen
        return user

    def add(self, user):
        self.list_of_all_users[user.name] = user

    def online(self, user):
        self.list_of_active_users[user.name] = user
        # TODO: lieber hier online-flag (status.logged_in) TRUE setzen,
        #       als in clip.py

    def drop(self, name):
        print 'deleting %s from list of active users' % name
        user = self.list_of_active_users[name]
        user.set_logout_data(time.time())
        user.save()   # TODO:   muss das save hier sein??????
        user.status.logged_in = False
        del self.list_of_active_users[name]
        # TODO: Fehler, wenn name not logged in

    def get_from_all(self, name, default=None):
        return self.list_of_all_users.get(name, default)

    def get_active(self, name, default=None):
        return self.list_of_active_users.get(name, default)

    def get_all_users(self,):
        return self.list_of_active_users.values()

    def whois(self, name):
        if name in self.list_of_active_users:
            res = self.list_of_active_users[name].whois()
        elif name in self.list_of_all_users:
            res = self.list_of_all_users[name].whois()
        else:
            res = "No information found on user %s." % name
        return res

class Info:
    """Info soll selbst so wenig Methoden als möglich haben und lediglich
als Datencontainer dienen."""
    def __init__(self, data, toggles, settings, messages):
        self.login, self.last_logout, self.host, self.name, self.passwd, \
                self.rating, self.experience, self.address = data
        self.toggles = toggles
        self.settings = settings
        self.messages = messages
        self.away = 0
        print 'initializing INFO', self.show()

    def set_login_data(self, login, host):
        self.last_login = self.login
        self.login = int(login)
        self.last_host = self.host
        self.host = host

    def set_logout_data(self, logout,):
        self.last_logout = int(logout)

    def set_rating(self, rating, experience):
        self.rating = rating
        self.experience = experience

    def advance_rating(self, rating, experience):
        self.rating += rating
        self.experience += experience

    def message(self, msg):
        """message() is used for persistency of messages."""
        self.messages.append(msg)
        print 'message:', msg

    def show(self,):
        out = StringIO()
        v = self
        print >>out, v.login, v.last_logout, v.host, v.name, '*****', \
                          v.rating, v.experience, v.address
        print >>out,v.toggles.values()
        print >>out,v.settings
        return out.getvalue()

    def array(self, battery):
        s = self.toggles            # array() wird wohl nicht benutzt
        t = {0: ('allowpip', 'autoboard', 'autodouble', 'automove',),
             1: ('bell', 'crawford', 'double',),            # 'autoroll', ???
             2: ('greedy', 'moreboards', 'moves', 'notify',),
             3: ('ratings', 'ready',),
             4: ('report', 'silent',),
             }
        return [s[i] for i in t[battery]]

    def __str__(self,):
        _t = {True: '1', False: '0'}
        t = [' '.join([_t[i] for i in self.array(p)]) for p in range(5)]
        ret = '%s %s %d %s %d %s %.2f %s %s %s %s' % \
            (self.name, t[0], getattr(self, 'away', 0), t[1], self.experience,
             t[2], self.rating, t[3], self.settings[3], t[4], self.settings[5],)
        return ret

class Status:                       # TODO:  dringend überprüfen, ob der
                                    #        IMMER aktuell ist.
                                    #   x für self.logged_in sieht es gut aus
    def __init__(self, toggles, user):
##        self.timestamp = time.time()
        self.toggles = toggles
        self.away = False
        self.away_msg = ''
        # status: online ready playing / watching
        self.states = (('', 'offline',),
                       ('', 'online', 'ready', 'playing'),
                       ('', 'watching',))
        self.active_state = [1, 0, 0]
        self.opponent = None
        self.opponent_name = '-'
        self.watchee = None
        self.watchee_name = '-'
        self.user = user
        self.ready_fmt = {True: '', False: 'not '}

##    def get_state(self,):
##        if self.toggles.read('ready'):
##            self.active_state = [0, 2, 0]
##        if fmt == 'str':
##            status = ('ready', 'online', 'playing')[status]
##        return status

    def playing(self, opponent, ON=True):
        if ON:
            self.active_state[1] = 2
            self.opponent = opponent
            self.opponent_name = opponent.name
        else:
            self.active_state[1] = 1
            self.opponent = None
            self.opponent_name = '-'

    def set_watching(self, watchee, ON=True):
        if ON:
            self.active_state[2] = 1
            self.watchee = watchee
            self.watchee_name = watchee.name
        else:
            self.active_state[2] = 0
            self.watchee = watchee
            self.watchee_name = '-'

    def get_readyflag(self,):
        return int(self.toggles.read('ready'))

    def get_watchflag(self,):
        return self.active_state[2] == 1

    def get_awayflag(self,):
        return int(self.away)

    def get_away_messge(self,):
        return int(self.away_msg)

    def get_playingflag(self,):
        return int(self.active_state[1] == 2)

    def is_online(self,):
        return hasattr('self','logged_in') and self.logged_in

    def set_away(self, msg):
        self.away = True
        self.away_msg = msg
        self.user.info.away = 1

    def set_back(self,):
        self.away = False
        self.away_msg = ''
        self.user.info.away = 0

    def stamp(self,):
        self.timestamp = time.time()

    def idle(self, formatted=False):
        ret = time.time() - self.timestamp
        if formatted:
            if ret < 60.:
                ret = "%02d seconds" % int(ret)
            else:
                ret = "%s minutes" % time.strftime("%M:%S", time.gmtime(ret))
        return ret

    def play_status(self, name):
        ready = self.ready_fmt[self.get_readyflag()]
        if self.get_playingflag():
            ret = "%s is playing with %s" % (name, self.opponent_name)
        elif self.get_watchflag():
            ret = "%s is %sready to play, watching %s, not playing." % \
                                              (name, ready, self.watchee.name)
        else:
            ret = "%s is %sready to play, not watching, not playing." % \
                                              (name, ready,)
        return ret

class Toggles:
    toggle_names = (
            'allowpip', 'autoboard', 'autodouble', 'autoroll', 'automove',
            'bell', 'crawford', 'double', 'greedy', 'moreboards', 'moves',
            'notify', 'ratings', 'ready', 'report', 'silent',
            'telnet', 'wrap',
            )
    toggle_on_msgs = (
            "** You allow the use of the server's 'pip' command.",
            "** The board will be refreshed after every move.",
            "** You agree that doublets during opening double the cube.",
            "** You won't be asked if you want to double.",
            "** Forced moves will be done automatically.",

            "** Your terminal will ring the bell if someone talks to you or invites you",
            "** You insist on playing with the Crawford rule.",
            "** You will be asked if you want to double.",
            "** Will use automatic greedy bearoffs.",
            "** Will send rawboards after rolling.",

            "** You want a list of moves after this game.",            
            "** You will be notified when new users log in.",
            "** You'll see how the rating changes are calculated.",
            "** You're now ready to invite or join someone.",
            "** You will be informed about starting and ending matches.",

            "** You won't hear what other players shout.",
            "** You use telnet and don't need extra 'newlines'.",
            "** The server will wrap long lines.",
            )
    toggle_off_msgs = (
            "** You don't allow the use the server's 'pip' command.",
            "** The board won't be refreshed after every move.",
            "** You don't agree that doublets during opening double the cube.",
            "** You will be asked if you want to double.",
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

            "** You will hear what other players shout.",
            "** You use a client program and will receive extra 'newlines'.",
            "** Your terminal knows how to wrap long lines.",
            )
    toggle_msg = {
            True: dict(zip(toggle_names, toggle_on_msgs)),
            False: dict(zip(toggle_names, toggle_off_msgs))
            }
    toggle_std = (
            True, True, False, False, True, False, True, True, False,
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

    def set_switch(self, switch, value):
        if value in (True, False) and self.has(switch):
            self._switches[switch] = value

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
        elif vals[0] in ('1','2','3','4'):
            self._boardstyle = int(vals[0])
            # TODO: hier und in den xxxxlength() muss int() getrapped werden
            res = "Value of 'boardstyle' set to %d." % self._boardstyle
        else:
            res = "** Valid arguments are the numbers 1 to 3."
        return res

    def get_boardstyle(self,):
        return self._boardstyle

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

    def get_sortwho(self,):
        return self._sortwho

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
        out = StringIO()
        print >> out, 'Settings of variables:'
        print >> out, '%-12s%d' % ('boardstyle:', self._boardstyle)
        print >> out, '%-12s%s' % ('linelength:', self._linelength)
        print >> out, '%-12s%s' % ('pagelength:', self._pagelength)
        print >> out, '%-12s%s' % ('redoubles:', self._redoubles)
        print >> out, '%-12s%s' % ('sortwho:', self._sortwho)
        print >> out, '%-12s%s' % ('timezone:', self._timezone)
        return out.getvalue()

    def save(self,):
        self._settings[0] = self._boardstyle
        self._settings[1] = self._linelength
        self._settings[2] = self._pagelength
        self._settings[3] = self._redoubles
        self._settings[4] = self._sortwho
        self._settings[5] = self._timezone

class User(Persistent):
    def __init__(self, data):
        Persistent.__init__(self, DB_Users, 'users')
        self.info = data
        self.name = self.info.name
        self.settings = Settings(self.info)
        self.toggles = Toggles(self.info)
        self.status = Status(self.toggles, self)
##        self.info.is_away = self.is_away
        self._waves = 0
        self.invitations = {}   # TODO: wegen der Persistenz muss ich User()
                        # vielleicht wrappen, damit der Kern - User() - deep
                        # gespeichert werden kann und dynamical stuff wie
                        # invitations oder games nicht gespeichert werden.
        self.dice = 'random'
        self.db_key = self.name
        self.db_load = self.info
        self.watchers = {}

    def set_protocol(self, protocol):
        self.protocol = protocol

    def check_password(self, password):
        return self.info.passwd == password

    def set_password(self, password):
        # TODO:  warum hab ich hier neben change_password() ne extra funktion?
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

    def set_address(self, address):
        self.info.address = address
        self.save()

    def save_settings(self,):
        self.settings.save()
        self.save()

    def set_login_data(self, login_time, host):
        self.info.set_login_data(login_time, host)
        self.save()

    def set_logout_data(self, logout_time,):
        self.info.set_logout_data(logout_time)
        self.save()

    def advance_rating(self, rating, experience):
        self.info.advance_rating(rating, experience)
        self.save()

    def tell(self, user, msg):
        user.chat('12 %s %s' % (self.name, msg))
        self.chat('16 %s %s' % (user.name, msg))

    def shout(self, msg):
        self.protocol.factory.broadcast('13 %s %s' % (self.name, msg),
                                                    exceptions=(self.name,))
        self.chat('17 %s' % (msg))

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
        args['opponent'] = self.status.opponent_name
        args['watching'] = self.status.watchee_name
        args['ready'] = self.status.get_readyflag()
        args['away'] = self.status.get_awayflag()
        args['rating'] = self.info.rating
        args['experience'] = self.info.experience
        args['idle'] = int(self.status.idle())
        args['login'] = self.info.login
        args['hostname'] = self.info.host
        args['client'] = '-'            # TODO: richtige Werte verwenden
        address = getattr(self.info, 'address', '')
        if address:
            args['email'] = address
        else:
            args['email'] = '-'
        w = '5 %(user)s %(opponent)s %(watching)s %(ready)s ' \
            '%(away)s %(rating)s %(experience)s %(idle)d %(login)s ' \
            '%(hostname)s %(client)s %(email)s' % args
        return w

    def whois(self,):
        # TODO: speed up: wenn formatiert, dann als attribut ablegen
        #       detect, wenn sich was geändert hat
        args = {}
        args['name'] = self.name
        login = time.localtime(self.info.login) # TODO: speedup; save this date
                                                #       in ascii-format right away
        args['date'] = time.strftime("%A, %B %d %H:%M %Z", login)
        if self.status.logged_in:
            login_details = "Still logged in. %s idle" % self.status.idle(True)
            args['last_login_details'] = login_details
            args['play_status'] = self.status.play_status(self.name)
        else:
            logout = time.localtime(self.info.last_logout) # TODO: speedup; save this date
                                                #       in ascii-format right away
            logout_date = time.strftime("%A, %B %d %H:%M %Z", logout)
            args['last_login_details'] = "Last logout: %s" % logout_date
            args['play_status'] = "Not logged in right now."
        if self.status.away:
            args['away_status'] = "user is away:"       # TODO: richtige Werte verwenden
        args['rating_exp'] = "Rating: %.2f Experience: %d" % (self.info.rating,self.info.experience)
        address = getattr(self.info, 'address', '')
        if address:
            args['email'] = "Email address: %s" % address
        else:
            args['email'] = "No email address."
        
        return """Information about %(name)s:
  Last login:  %(date)s from p987987.dip.t-dialin.net
  %(last_login_details)s
  %(play_status)s
  %(rating_exp)s
  %(email)s""" % args

    def invite(self, name, ML):
        self.invitations[name] = ML
        
    def join(self, invited_and_joining, list_of_games):
        ML = self.invitations.get(invited_and_joining.name, None)
        if not ML is None:
            self.status.playing(invited_and_joining)
            self.chat('** Player %s has joined you for a %s point ' \
                                    'match' % (invited_and_joining.name, ML))
            invited_and_joining.status.playing(self)
            invited_and_joining.chat('** You are now playing a %s point ' \
                                            'match with %s.' % (ML, self.name))
            kw = {'player1':self, 'player2':invited_and_joining}
            kw['ML'] = ML
            kw['dice'] = self.dice
            kw['list_of_games'] = list_of_games
            self.running_game,invited_and_joining.running_game = getGame(**kw)
            self.getGame = list_of_games.get
            invited_and_joining.getGame = list_of_games.get
            del self.invitations[invited_and_joining.name]

    def teardown_game(self,):
            self.status.playing('-', ON=False)
            self.update_who(self)
            if hasattr(self, 'running_game'):
                del self.running_game

    def leave_game(self,):
        running_game = getattr(self, 'running_game', False)
        if running_game:
            game, player = self.getGame(running_game)
            game.stop()

    def watch(self, user):
        # TODO: blind mechanism
        # TODO: user logs out
        self.watchers[user.name] = user
        user.set_watching(self)
        self.chat('%s is watching you.' % user.name)
        self.status.opponent.chat('%s starts watching %s.' % \
                                              (user.name, self.name))

    def unwatch(self, user):
        del self.watchers[user.name]
        self.chat('%s stops watching you.' % user.name)
        self.status.opponent.chat('%s stops watching %s.' % \
                                              (user.name, self.name))

    def set_watching(self, user):
        self.status.set_watching(user, ON=True)
        self.update_who(self)
        
    def unset_watching(self,):      # TODO: wieso geh ich nicht auch über
                                    #       unwatch() rein?
                                    #       Das scheint inkonsequent        
        if self.status.get_watchflag():
            self.status.watchee.unwatch(self)
            self.status.set_watching(None, ON=False)
            self.update_who(self)
        
##    def set_watching(self, watchee, ON=True):
##        if ON:
##            self.active_state[2] = 1
##            self.watchee = watchee
##        else:
##            self.active_state[2] = 0
##            self.watchee = None
        
        

    def welcome(self,):
        info = self.info
        return '1 %s %s %s' % (self.name, info.last_login, info.last_host)

    def own_info(self,):
        return '2 %s' % str(self.info)

    def drop_connection(self,):
        self.leave_game()
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

    def update_who(self, user):   # TODO: das sollte zentrale Funktion sein,
                                  #       nicht eine Methode (oder ohne 
                                  #       parameter 'user')
        factory = self.protocol.factory
        who = user.who() + '\n6'
        factory.broadcast(who,)

    def greedy_bearoff(self,):
        return self.toggles.read('greedy')

    def rating(self,):
        return self.info.rating

    def experience(self,):
        return self.info.experience

    def ready(self,):
        return self.toggles.read('ready')   # TODO: tell me the difference to is_ready()

    def is_playing(self,):
        return self.status.get_playingflag()

    def is_watching(self,):
        if self.status.watchee is None:
            return ''
        else:
            return self.status.watchee.name

    def is_away(self,):
        return self.status.get_awayflag()

    def is_ready(self,):
        return self.ready()     # TODO - noch zu unsicher: status.get_readyflag()

    def online(self,):
        return self.status.is_online()

    def __str__(self,):
        return self.who()

def newUser(**kw):
    data = (kw['login'], 0, '', kw['user'], kw['password'], 1500., 0, '-')
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
    if not user is None and not user.online():
        lou.online(user)
    return user

def dropUser(**kw):
    kw['lou'].drop(kw['user'])      # TODO: muss dieser Umweg sein? besser direkt?
