#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

from StringIO import StringIO
import inspect

NYI = '##NYI##'

class Command():
    def __init__(self, lou):
        self.commands = dict(self.sample_commands())
        self.list_of_users = lou
        print 'available commands:', self.commands.keys()
        
# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line, me):
        return 'you shout: %s    %s' % (line[1:], NYI)

    def c_kibitz(self, line, me):
        return 'you kibitz: %s    %s' % (line[1:], NYI)

    def c_tell(self, line, me):
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get(name, None)
        if user is None:
            return '%s is not here' % name
        else:
            me.tell(user, msg)
##        return 'you tell: %s    %s' % (line[1:], NYI)

    def c_say(self, line, me):
        return 'you say: %s    %s' % (line[1:], NYI)

    def c_whisper(self, line, me):
        return 'you whisper: %s    %s' % (line[1:], NYI)

    def c_message(self, line, me):
        return 'message sent to %s: %s    %s' % (line[1], line[2:], NYI)

    def c_waitfor(self, line, me):
        return 'you now wait for: %s    %s' % (line[1], NYI)

    def c_gag(self, line, me):
        return 'you gagged: %s    %s' % (line[1], NYI)

    def c_blind(self, line, me):
        return 'you blinded: %s    %s' % (line[1], NYI)


# ----------------------------------------  Between Game Actions

    def c_invite(self, line, me):
        return 'you invited %s for a match of length %s    %s' % (line[1], line[2], NYI)

    def c_join(self, line, me):
        return 'you joined: %s    %s' % (line[1], NYI)

    def c_watch(self, line, me):
        return 'you now watch: %s    %s' % (line[1], NYI)

    def c_unwatch(self, line, me):
        return 'you are not watching any more: %s    %s' % (line[1], NYI)

    def c_look(self, line, me):
        return 'you look at: %s    %s' % (line[1], NYI)

    def c_oldboard(self, line, me):
        return 'you see the oldboard of: %s    %s' % (line[1], NYI)

    def c_oldmoves(self, line, me):
        return 'you see your old moves    %s' % NYI

    def c_away(self, line, me):
        return 'you are away    %s' % NYI

    def c_back(self, line, me):
        return 'welcome back    %s' % NYI

    def c_bye(self, line, me):
        return 'bye, bye    %s' % NYI

    def c_wave(self, line, me):
        return 'you wave goodbye    %s' % NYI

# ----------------------------------------  Setting Commands

    def c_toggle(self, line, me):
        return "you toggle '%s'" % line[1], NYI

    def c_set(self, line, me):
        return "you set '%s'" % line[1], NYI
    
    def c_address(self, line, me):
        return "you set your address to '%s'" % line[1], NYI

    def c_password(self, line, me):
        return "you changed your password to '%s'" % line[1], NYI

    def c_save(self, line, me):
        return "you save your settings", NYI

# ----------------------------------------  General Info

    def c_help(self, line, me):
        return 'die Hilfe gibt es noch nicht    %s' % NYI

    def c_show(self, line, me):
        return 'shown: %s    %s' % (line[1], NYI)

    def c_who(self, line, me):
        out = StringIO()
        lou = self.list_of_users.get_active_users()
        users = lou.keys()
        # TODO          set sortwho auf  users  anwenden
        for u in users:
            print >>out, lou[u].who()
        return out.getvalue()
##        return 'list of some ore more players    %s' % NYI

    def c_where(self, line, me):
        return 'where is %s from' % (line[1], NYI)

    def c_rawwho(self, line, me):
        return 'raw where is %s from' % (line[1], NYI)

    def c_whois(self, line, me):
        return 'info about player: %s    %s' % (line[1], NYI)

    def c_ratings(self, line, me):
        return 'ratings given    %s' % NYI

    def c_last(self, line, me):
        return 'info about last player    %s' % NYI

    def c_time(self, line, me):
        return 'it is 5 past 12    %s' % NYI

# ----------------------------------------  FIBS Info

    def c_motd(self, line, me):
        return 'an apple a day keeps the doctor away :)    %s' % NYI

    def c_about(self, line, me):
        return 'about SIBS    %s' % NYI

    def c_average(self, line, me):
        return 'the average is about 8.3    %s' % NYI

    def c_dicetest(self, line, me):
        return 'the dice are nice and cubic    %s' % NYI

    def c_version(self, line, me):
        return 'SIBS/clip 0.01    %s' % NYI

    def c_stat(self, line, me):
        return 'status of SIBS    %s' % NYI

# ----------------------------------------  Other Commands

    def c_clear(self, line, me):
        return 'other commands    %s' % NYI

    def c_erase(self, line, me):
        return 'other commands    %s' % NYI

    def c_shutdown(self, line, me):
        return 'other commands    %s' % NYI

# ----------------------------------------  Undocumented Commands

    def c_port(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_name(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_co(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_ne(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_ye(self, line, me):
        return 'undocumented commands    %s' % NYI

# ----------------------------------------  Game Commands

    def c_roll(self, line, me):
        return 'you reject    %s' % NYI

    def c_move(self, line, me):
        return 'you move    %s' % NYI

    def c_off(self, line, me):
        return 'you bear off    %s' % NYI

    def c_board(self, line, me):
        return 'you get a new board    %s' % NYI

    def c_pip(self, line, me):
        return 'you are 7 pips behind    %s' % NYI

    def c_double(self, line, me):
        return 'you double    %s' % NYI

    def c_accept(self, line, me):
        return 'you accept    %s' % NYI

    def c_reject(self, line, me):
        return 'you reject    %s' % NYI

    def c_resign(self, line, me):
        return 'you resign    %s' % NYI

    def c_leave(self, line, me):
        return 'you leave the game    %s' % NYI

    def c_redouble(self, line, me):
        return 'you redouble    %s' % NYI

    def c_beaver(self, line, me):
        return 'you beaver    %s' % NYI

    def c_raccoon(self, line, me):
        return 'you raccoon    %s' % NYI

    def c_otter(self, line, me):
        return 'you otter    %s' % NYI

    def c_panic(self, line, me):
        return "don't panic ... where is your towel    %s" % NYI

# ----------------------------------------  ====================

    def unknown(self, line, me):
        return 'unknown command %s    %s' % (line[0], NYI)

    def command(self, cmd):
        print self.commands.get(cmd, self.unknown)
        return self.commands.get(cmd, self.unknown)

    def sample_commands(self,):
        # TODO: falls man mal commands in den laufenden server injizieren will:
        #       als Plugin realisieren
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0].lstrip('c_'),f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('c_')]
        return lofc
