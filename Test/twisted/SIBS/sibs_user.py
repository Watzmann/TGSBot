#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

REV = '$Revision$'

import time
from StringIO import StringIO
import logging
from twisted.python import log as tw_log
from game import getGame
from command import NYI, ZONEINFO
from persistency import Persistent, Db
from version import Version

v = Version()
v.register(__name__, REV)

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('users')

DB_Users = 'db/users'
RESERVED_Users = ('guest', 'systemwart', 'administrator',
                  'sorrytigger', 'tigger', 'watzmann', 'tigergammon', 'tiga',
		  'vegas_vic',)
## TODO: RESERVED_Users gehören nicht in OpenSource

class UsersList:        # TODO: als Singleton ausführen
    def __init__(self,):
        self.list_of_active_users = {}
        self.db = all_users = Db(DB_Users, 'users').db  # TODO: hier so an der
                            #   PersistenzKlasse vorbeizuangeln ist schon krass!
        alle_leute = all_users.keys()
        #self.list_of_all_users = dict([(k,self.restore(all_users[k])) for k in alle_leute])
        volle_liste = []
        for k in alle_leute:
            try:
                d = self.restore(all_users[k])
                volle_liste.append((k,d))
            except:
                logger.error('could not load %s' % k)
        self.list_of_all_users = dict(volle_liste)
##        for e,k in enumerate(all_users.keys()):
##            print e,k
##            print all_users[k]

    criterion = {'away': lambda u: u.is_away(),
                 'ready': lambda u: u.is_ready(),
                 'playing': lambda u: u.is_playing()
                 }
    
    def get_active_users(self,):
        return self.list_of_active_users

    def get_active_toggled_users(self, toggle, value):
        return [u for u in self.list_of_active_users.values() \
                                if u.toggles.read(toggle) == value]

    def get_sorted_keys(self, ufilter = '', sort = 'name'):
        users = self.list_of_active_users.values()
        if ufilter in ('away','ready','playing',):
            users = filter(self.criterion[ufilter],
                           self.list_of_active_users.values())
        return {'login': self.sorted_keys_login,
                'name': self.sorted_keys_name,
                'rating': self.sorted_keys_rating,
                'rrating': self.sorted_keys_rrating}[sort](users)

    def sorted_keys_login(self, users):     # TODO: die drei sorted_keys hier
        keys = [u.name.lower() for u in users] # können zusammengefasst werden??
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].info.login,lau[y].info.login)
        return sorted(keys, compare)

    def sorted_keys_name(self, users):
        keys = [u.name.lower() for u in users]
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].name,lau[y].name)
        return sorted(keys, compare)

    def sorted_keys_rating(self, users):
        keys = [u.name.lower() for u in users]
        lau = self.list_of_active_users
        compare = lambda x,y: cmp(lau[x].rating(),lau[y].rating())
        return sorted(keys, compare)

    def sorted_keys_rrating(self, users):
        keys = self.sorted_keys_rating(users)
        keys.reverse()
        return keys

    def get_user(self, name, password):
        name = name.lower()
        if self.list_of_active_users.has_key(name): # user is already logged in
            return self.list_of_active_users[name]  # and get's a warning
        user = self.list_of_all_users.get(name, None)
        if (not user is None) and (user.info.passwd != password):
            logger.debug('found user %s; wrong password' % user.name)
            user = None
        return user

    def restore(self, user_data):
        user = User(user_data)
        user.status.logged_in = False
        user.getUser = self.get_from_all
        user.gameReports = self.game_reports
        user.shouts = self.shouts
        ## TODO: auf restore() könnte man verzichten; andererseits kann man
        ##       jetzt hier spezielle Aktionen durchführen
        return user

    def add(self, user):
        self.list_of_all_users[user.name.lower()] = user

    def online(self, user):
        self.list_of_active_users[user.name.lower()] = user
        # lieber hier online-flag (status.logged_in) TRUE setzen,
        # als in clip.py ......NEIN, GEHT NICHT WEIL danach erst geprüft wird,
        # ob er BEREITS online ist.

    def drop(self, name):
        logger.debug('deleting %s from list of active users' % name)
        name = name.lower()
        user = self.list_of_active_users.get(name)
        if not user is None:
            user.set_logout_data(time.time())   # TODO: rather formated string?
            user.save('usersList.drop')   # is this save neccessary?
                                          # no, but it doesn't hurt either!
            user.status.logged_in = False
            del self.list_of_active_users[name]

    def get_from_all(self, name, default=None):
        return self.list_of_all_users.get(name.lower(), default)

    def get_active(self, name, default=None):
##        print self.list_of_active_users.keys()
        return self.list_of_active_users.get(name.lower(), default)

    def get_all_users(self,):
        return self.list_of_active_users.values()

    def get_watchers(self,):
        return [u for u in self.list_of_active_users.values() \
                                if not u.status.watchee is None]

    def nr_logged_in(self,):
        return len(self.list_of_active_users)

    def whois(self, name):      # TODO: hier analog Fibs case sensitive
        lname = name.lower()
        if lname in self.list_of_active_users:
            user = self.list_of_active_users[lname]
            if user.name == name:
                return user.whois()
        elif lname in self.list_of_all_users:
            user = self.list_of_all_users[lname]
            if user.name == name:
                return user.whois()
        else:
            return "No information found on user %s." % name

    def game_reports(self, msg):
        for u in self.get_active_toggled_users('report', True):
            u.chat(msg)

    def shouts(self, msg, name, exceptions=[]):
        for u in self.get_active_toggled_users('silent', False):
            if (u.name in exceptions) or u.is_gagged(name):
                continue
            u.chat(msg)

from twisted.internet import threads, defer
from subprocess import Popen, PIPE

class Info:
    """Info soll selbst so wenig Methoden als möglich haben und lediglich
als Datencontainer dienen."""
    def __init__(self, data, toggles, settings, messages, saved_games,
                 gagged, blinded, special):
        self.login, self.last_logout, self.host, self.name, self.passwd, \
                self.rating, self.experience, self.address = data
        self.toggles = toggles
        self.settings = settings
        self.messages = messages
        self.saved_games = saved_games
        self.gagged = gagged
        self.blinded = blinded
        self.special = special      # special flag (test, premium, bot, ...)
        self.away = 0
        logger.info('initializing INFO %s' % self.show())

    def set_login_data(self, login, host):
        self.last_login = self.login
        self.login = int(login)
        self.last_host = self.host
        self.host = host
        d = threads.deferToThread(self.nslookup, host)
        d.addCallback(self.host_dns_name)

    def set_logout_data(self, logout,):
        self.last_logout = int(logout)

    def set_rating(self, rating, experience):
        self.rating = rating
        self.experience = experience

    def advance_rating(self, rating, experience):
        self.rating += rating
        self.experience += experience

    def message(self, msg):
        """message() is used for persisting messages."""
        self.messages.append(msg)
        logger.info('saving message: %s' % msg)

    def save_game(self, opponent, gid, score, ML):
        """save_game() is used for persisting games."""
        self.saved_games[opponent] = {'gid':gid, 'score':score, 'ML':ML,}
        # TODO: this could be changed to record multiple games between 2 players
        logger.info('saving game: %s' % gid)

    def gag(self, user):
        """gag() is used for persisting gagged users."""
        if user in self.gagged:
            self.gagged.remove(user)
            logger.info('ungagging: %s' % user)
            msg = "** You ungag %s" % user
        else:
            self.gagged.append(user)
            logger.info('gagging: %s' % user)
            msg = "** You gag %s" % user
        return msg

    def blind(self, user):
        """blind() is used for persisting blinded users."""
        if user in self.blinded:
            self.blinded.remove(user)
            logger.info('unblinding: %s' % user)
            msg = "** You unblind %s" % user
        else:
            self.blinded.append(user)
            logger.info('blinding: %s' % user)
            msg = "** You blind %s" % user
        return msg

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
        ret = '%s %s %d %s %d %s %.2f %s %s %s %s (%s)' % \
            (self.name, t[0], getattr(self, 'away', 0), t[1], self.experience,
             t[2], self.rating, t[3], self.settings[3], t[4], self.settings[5],
             self.host)
        return ret

    def nslookup(self, ip):
        output = Popen(["nslookup", ip], stdout=PIPE).communicate()[0]
        ret = output.find('name = ')
        if ret == -1:
            ret = ''
        else:
            ret = output[ret+7:].splitlines()[0]
            if ret[-1] == '.':
                ret = ret[:-1]
        return ret

    def host_dns_name(self, host_name):
        if host_name:
            self.host = host_name

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
        return hasattr(self,'logged_in') and self.logged_in

    def set_away(self, msg):
        self.away = True
        self.away_msg = msg
        self.user.info.away = 1

    def set_back(self,):
        self.away = False
        self.away_msg = ''
        self.user.info.away = 0

    def stamp(self,):
        self.timestamp = time.time()    # must be seconds; used for delta

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
            True, True, False, False, False, False, True, True, False,
            False, False, True, False, False, True, False, True, False,
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
##        self._boardstyle = 2          defaults from FIBS (nada, telnet)
##        self._linelength = 0
##        self._pagelength = 0
##        self._redoubles = 'none'
##        self._sortwho = 'login'
##        self._timezone = 'UTC'
##        self._delay = '0.3'
        self._settings = info.settings
        # TODO: hier sollte statt info DRINGEND nur "settings" übergeben werden.
        #       Diese Abhängigkeit von Info() ist nicht akzeptabel.
        self._boardstyle = info.settings[0]
        self._linelength = info.settings[1]
        self._pagelength = info.settings[2]
        self._redoubles = info.settings[3]
        self._sortwho = info.settings[4]
        self._timezone = info.settings[5]
        self._delay = info.settings[6]
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
        if len(vals) == 0:
            res = "Value of 'timezone' is %s" % self._timezone
        elif ZONEINFO.is_valid(vals[0]):
            self._timezone = vals[0]
            res = "Value of 'timezone' set to %s." % self._timezone
        else:
            res = "Can't find timezone '%s'. Try one of: \n" % vals[0] + \
                                                                  ZONEINFO.text
        return res

    def get_timezone(self,):
        return self._timezone

    def delay(self, *values):
        vals = values[0]
        if len(vals) == 0:
            res = "Value of 'delay' is %s" % self._delay
        else:
            try:
                self._delay = float(vals[0])
                res = "Value of 'delay' set to %.3f." % self._delay
            except ValueError:
                res = "** Valid arguments are seconds like 1 or 0.5 or 2.7555. " \
                      "Use 0. for the default value (0.3 seconds)."
        return res

    def get_delay(self,):
        return self._delay

    def get_default_delay(self,):
        return 0.3

    def show(self,):    # TODO
        out = StringIO()
        print >> out, 'Settings of variables:'
        print >> out, '%-12s%d' % ('boardstyle:', self._boardstyle)
        print >> out, '%-12s%s' % ('linelength:', self._linelength)
        print >> out, '%-12s%s' % ('pagelength:', self._pagelength)
        print >> out, '%-12s%s' % ('redoubles:', self._redoubles)
        print >> out, '%-12s%s' % ('sortwho:', self._sortwho)
        print >> out, '%-12s%s' % ('timezone:', self._timezone)
        print >> out, '%-12s%.3f' % ('delay:', self._delay)
        return out.getvalue()

    def save(self,):
        self._settings[0] = self._boardstyle
        self._settings[1] = self._linelength
        self._settings[2] = self._pagelength
        self._settings[3] = self._redoubles
        self._settings[4] = self._sortwho
        self._settings[5] = self._timezone
        self._settings[6] = self._delay

class User(Persistent):
    def __init__(self, data):
        Persistent.__init__(self, DB_Users, 'users')
        self.info = data
        #print 'in User',data
        self.name = self.info.name
        self.settings = Settings(self.info)
        self.toggles = Toggles(self.info)
        self.status = Status(self.toggles, self)
##        self.info.is_away = self.is_away
        self._waves = 0
        self.invitations = {}
        self.dice = 'random'
        self.db_key = self.name.lower()
        self.db_load = self.info
        self.watchers = {}
        self.nr_of_logins = 0

    def set_protocol(self, protocol):
        self.protocol = protocol

    def disconnect_hard(self,):
        self.protocol.dropConnection('hard disconnect')

    def tried_second_login(self,):
        return self.nr_of_logins

    def set_second_login(self, cnt):
        self.nr_of_logins = cnt

    def check_password(self, password):
        return self.info.passwd == password

    def set_password(self, password):
        # TODO:  warum hab ich hier neben change_password() ne extra funktion?
        self.info.passwd = password
        self.save('user.set_password')

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
        self.save('user.set_address')

    def save_settings(self,):
        self.settings.save()
        self.save('user.save_settings')

    def set_login_data(self, login_time, host):
        self.info.set_login_data(login_time, host)  # TODO: rather formated string?
        self.save('user.set_login_data')

    def set_logout_data(self, logout_time,):
        self.info.set_logout_data(logout_time)      # TODO: rather formated string?
        self.save('user.set_logout_data')

    def advance_rating(self, rating, experience):
        self.info.advance_rating(rating, experience)
        self.save('user.advance_rating')

    def get_kibitz_addressees(self,):
        ret = {}
        running_game = getattr(self, 'running_game', False)
        if running_game:
            opponent = self.status.opponent
            ret['players'] = [opponent,]
            ret['watchers'] = self.watchers.values() + \
                              opponent.watchers.values()
        else:
            watchee = self.status.watchee
            ret = watchee.get_kibitz_addressees()
            ret['players'].append(watchee)
            ret['watchers'].remove(self)
        return ret

    def kibitz(self, msg, whisper=False):
        ka = self.get_kibitz_addressees()
        if whisper:
            kibitz = '14 %s %s' % (self.name, msg)
            ka = ka['watchers']
            self.chat('18 %s' % msg)
        else:
            kibitz = '15 %s %s' % (self.name, msg)
            ka = ka['players'] + ka['watchers']
            self.chat('19 %s' % msg)
        for k in ka:
            k.chat(kibitz)
        n = len(ka)
        if n > 1:
            users = '%d users' % n
        else:
            users = '1 user'
        self.chat('** %s heard you.' % users)

    def tell(self, user, msg):
        if not self.info.special == 'banned':
            user.chat('12 %s %s' % (self.name, msg))
        self.chat('16 %s %s' % (user.name, msg))

    def say(self, user, msg):
        user.chat('12 %s' % msg)
        self.chat('16 %s %s' % (user.name, msg))

    def shout(self, msg):
        shout = '13 %s %s' % (self.name, msg)
        tw_log.msg(shout)
        self.chat('17 %s' % (msg))
        if not self.info.special == 'banned':
            excpt = self.info.gagged + [self.name,]
            self.shouts(shout, self.name, exceptions=excpt)

    def deliver_messages(self,):
        """Delivers messages when user logs in"""
        msgs = self.info.messages
        if msgs:
            self.info.messages = []
            self.save('user.deliver_messages')
        return msgs

    def send_message(self, user, msg):
        """Use send_message() to send a message to another player."""
        user.message(self.name, int(time.time()), msg)  # time.time() correct

    def message(self, user, at_time, msg):
        """message() will receive a message from another player."""
        # 9 from time message
        self.info.messages.append('9 %s %d %s' % (user, at_time, msg))
        self.save('user.message')
        # TODO: if logged in trigger receive_message()

    def chat(self, msg):
        self.protocol.tell(msg)

    def chat_watchers(self, msg):
        for w in self.watchers.values():
            w.chat(msg)

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
        args['host'] = getattr(self.info, 'last_host', self.info.host)
                                # TODO: warum kann last_host fehlen??????
                                # TODO: wenn er eingeloggt ist, was ist dann
                                # der richtige? der jetzige oder der davor???
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
  Last login:  %(date)s from %(host)s
  %(last_login_details)s
  %(play_status)s
  %(rating_exp)s
  %(email)s""" % args

    def invite(self, name, ML, opponent):
        valid = True
        inv = {'ML': ML}
        if ML is None:
            sg = self.info.saved_games.get(name, None)
            if sg is None:
                valid = False
            else:
                inv['gid'] = sg['gid']
                gid = inv['gid'].split('.')[0]
                valid = opponent.has_saved_game(self.name, gid)
        if valid:
            self.invitations[name] = inv
        return valid
        
    def join(self, invited_and_joining, list_of_games):
        inv = self.invitations.get(invited_and_joining.name, None)
        ML = inv['ML']
        kw = {'ML':ML, 'dice':self.dice, 'list_of_games':list_of_games}
        iaj = invited_and_joining
        if ML is None:
            ML = self.info.saved_games[iaj.name]['ML']
            score = self.info.saved_games[iaj.name]['score']
            s, t = score
            opp_score = (t, s)
            self.status.playing(iaj)
            rml = 'Your running match was loaded.'
            self.chat('%s has joined you. %s' % (iaj.name, rml))
            # TODO hier fehlt ein blind (spez watch)
            watchers_msg = '%s and %s are resuming their %s point match'
            game_report = watchers_msg % (self.name, iaj.name, ML)
            self.chat_watchers(game_report)
            iaj.status.playing(self)
            iaj.chat('You are now playing with %s. %s' % (self.name, rml))
            iaj.chat_watchers(watchers_msg % (iaj.name, self.name, ML))
           # TODO msg = ????????? was wollt ich hier?
            gid = inv['gid']
# ------------------------------------ TODO: auf p1 und p2 mappen und dann ausserhalb
            if gid.endswith('.p1'):
                kw['player1'] = self    # the inviting player is p1
                kw['player2'] = iaj
            else:
                kw['player1'] = iaj     # the inviting player is p1
                kw['player2'] = self
                                # des if blocks von p1 und p2 abhängig machen
            kw['gid'] = gid.split('.')[0]
# ------------------------------------            
        else:
            score = (0, 0)
            opp_score = (0, 0)
            self.status.playing(iaj)
            self.chat('** Player %s has joined you for a %s point match' % \
                                                                (iaj.name, ML))
            # TODO hier fehlt ein blind (spez watch)
            watchers_msg = '%s and %s start a %s point match'
            game_report = watchers_msg % (self.name, iaj.name, ML)
            self.chat_watchers(game_report)
            iaj.status.playing(self)
            iaj.chat('** You are now playing a %s point match with %s.' % \
                                                                (ML, self.name))
            iaj.chat_watchers(watchers_msg % (iaj.name, self.name, ML))
            kw['player1'] = self    # the inviting player is p1
            kw['player2'] = iaj
        self.gameReports(game_report)
        kw['player1'].running_game, kw['player2'].running_game = getGame(**kw)
        sg = self.info.saved_games.get(iaj.name, None) # overwrite a saved game?
        if not sg is None:                             # yes
            list_of_games.delete_saved_game(sg['gid'])
        self.info.save_game(iaj.name, self.running_game, score, ML)
        self.save('user.join')
        iaj.info.save_game(self.name, iaj.running_game, opp_score, ML)
        iaj.save('user.join')
        self.getGame = list_of_games.get #  schau mal, ob du das einsetzen kannst
        iaj.getGame = list_of_games.get  #  JA - in continue_match und leave_game
        del self.invitations[iaj.name]   # TODO: kein synch! kann das zu problemen führen????

    def continue_match(self,):
        self.ready_to_continue = True
        if getattr(self.status.opponent, 'ready_to_continue', False):
            if self.status.opponent.ready_to_continue:
                running_game = getattr(self, 'running_game', False)
                if running_game:
                    game, player = self.getGame(running_game)
                    game.continue_game()
        else:
            self.chat('** Please wait for %s to join too.' % \
                                          self.status.opponent_name)

    def teardown_game(self, score, save=False):
        opp = self.status.opponent_name
        self.status.playing('-', ON=False)
        self.update_who(self)
        if hasattr(self, 'running_game'):
            if save:
                self.info.saved_games[opp]['score'] = score
                self.save('user.teardown_game')
            else:
                del self.info.saved_games[opp]
            del self.running_game

    def leave_game(self,):
        running_game = getattr(self, 'running_game', False)
        if running_game:
            game, player = self.getGame(running_game)
            self.status.opponent.chat('** Player %s has left the game. ' \
                                          'The game was saved.' % self.name)
            game.stop()

    def watch(self, user):
        """Perform 'watch' on the player being watched.
    self.watchers is a dictionary listing the players that watch user.
"""
        # TODO: blind mechanism
        # TODO: user logs out
        self.watchers[user.name] = user
        user.set_watching(self)
        self.chat('%s is watching you.' % user.name)
        self.status.opponent.chat('%s starts watching %s.' % \
                                              (user.name, self.name))

    def unwatch(self, user):
        """Perform 'unwatch' on the player being watched.
    The player stopping to watch calls this and is thereby deleted
    from the watchers list.
"""
        del self.watchers[user.name]
        self.chat('%s stops watching you.' % user.name)
        opp = self.status.opponent
        if not opp is None:
            opp.chat('%s stops watching %s.' % (user.name, self.name))

    def set_watching(self, user):
        """Perform 'set_watching' on the player starting to watch.
    It is called by his watchee and updates his status.
"""
        self.status.set_watching(user, ON=True)
        self.update_who(self)
        
    def unset_watching(self, forced=False):
        """Perform 'unset_watching' on the player stopping to watch.
    If watching at all, his watchee is being ridded of him and his
    status is updated.
"""
        # TODO: wieso geh ich nicht auch über unwatch() rein?
        #       Das scheint inkonsequent
        if self.status.get_watchflag():
            if not forced:
                self.status.watchee.unwatch(self)
            self.status.set_watching(None, ON=False)
            self.update_who(self)

    def rid_watchers(self, reason):
        for w in self.watchers.values():
            w.chat("%s. You're not watching anymore." % reason)
            w.unset_watching(forced=True)
        self.watchers = {}

    def gag(self, user):
        msg = self.info.gag(user)
        self.save('user.gag')
        return msg

    def show_gagged(self,):
        if len(self.info.gagged):
            return "** Gagged users: " + ','.join(self.info.gagged)
        else:
            return "** Gagged users: none"

    def blind(self, user):
        msg = self.info.blind(user)
        self.save('user.blind')
        return msg

    def show_blinded(self,):
        if len(self.info.blinded):
            return "** Blinded users: " + ','.join(self.info.blinded)
        else:
            return "** Blinded users: none"
    
    def welcome(self,):
        info = self.info
        return '1 %s %s %s' % (self.name, info.last_login, info.last_host)

    def own_info(self,):
        return '2 %s' % str(self.info)

    def drop_connection(self,):
        self.leave_game()
        self.rid_watchers('%s logs out.' % self.name) # TODO: other messages
        self.unset_watching()
        self.invitations = {}
        self.protocol.factory.broadcast('8 %s %s drops connection' % \
                                        (self.name,self.name), (self.name,)) 

    def wave(self,):
        if self._waves == 0:
            self._waves += 1
            self.protocol.factory.broadcast('%s waves goodbye.' % \
                                        (self.name,), (self.name,)) 
            return 'You wave goodbye.'
        else:
            self._waves = 0
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

    def is_gagged(self, name):
        return name in self.info.gagged

    def is_blinded(self, name):
        return name in self.info.blinded

    def online(self,):
        online = self.status.is_online()
        logger.info('online status: %s' % online)
        return online

    def show_saved(self,):
        out = StringIO()
        for s, v in self.info.saved_games.iteritems():
            pre = '  '
            if s == self.status.opponent_name:
                pre = ' *'
            elif self.getUser(s) and self.getUser(s).online():
                pre = '**'
            print >>out, '%s%-22s %2s               %2d - %2d' % \
                                              ((pre, s, v['ML']) + v['score'])
        return out.getvalue()

    def has_saved_game(self, name, gid):
        return self.info.saved_games[name]['gid'].split('.')[0] == gid

    def __str__(self,):
        return self.who()

def newUser(**kw):
    data = (kw['login'], 0, kw['host'], kw['user'], kw['password'],
                                                            1500., 0, '-')
    toggles = dict(zip(Toggles.toggle_names, Toggles.toggle_std))
    settings = [2, 0, 0, 'none', 'login', 'UTC', 0.3]
    info = Info(data, toggles, settings, [], {}, [], [], '')
    user = User(info)
    user.save('newUser')
    user.getUser = kw['lou'].get_from_all
    user.gameReports = kw['lou'].game_reports
    user.shouts = kw['lou'].shouts
    kw['lou'].add(user)
    kw['lou'].online(user)
    user.status.stamp()
    return user

def getUser(**kw):
    lou = kw['lou']
    user = lou.get_user(kw['user'], kw['password'])
    if not user is None and not user.online():
        lou.online(user)
    return user

def isUser(**kw):
    return not kw['lou'].get_from_all(kw['user']) is None
    
def dropUser(**kw):
    kw['lou'].drop(kw['user'])      # TODO: muss dieser Umweg sein? besser direkt?
                                    #       Wenn überhaupt, dann, weil diese
                                    #       Funktionen Convenience sind. Dann
                                    #       darf aber nicht nötig sein, dass man
                                    #       alles in **kw mitgibt.
