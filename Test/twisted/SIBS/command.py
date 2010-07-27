#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

import inspect

NYI = '##NYI##'

class Command():
    def __init__(self,):
        self.commands = dict(self.sample_commands())
        print 'available commands:', self.commands.keys()
        
# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line):
        return 'you shout: %s    %s' % (line[1:], NYI)

    def c_kibitz(self, line):
        return 'you kibitz: %s    %s' % (line[1:], NYI)

    def c_tell(self, line):
        return 'you tell: %s    %s' % (line[1:], NYI)

    def c_say(self, line):
        return 'you say: %s    %s' % (line[1:], NYI)

    def c_whisper(self, line):
        return 'you whisper: %s    %s' % (line[1:], NYI)

    def c_message(self, line):
        return 'message sent to %s: %s    %s' % (line[1], line[2:], NYI)

    def c_waitfor(self, line):
        return 'you now wait for: %s    %s' % (line[1], NYI)

    def c_gag(self, line):
        return 'you gagged: %s    %s' % (line[1], NYI)

    def c_blind(self, line):
        return 'you blinded: %s    %s' % (line[1], NYI)


# ----------------------------------------  Between Game Actions

    def c_invite(self, line):
        return 'you invited %s for a match of length %s    %s' % (line[1], line[2], NYI)

    def c_join(self, line):
        return 'you joined: %s    %s' % (line[1], NYI)

    def c_watch(self, line):
        return 'you now watch: %s    %s' % (line[1], NYI)

    def c_unwatch(self, line):
        return 'you are not watching any more: %s    %s' % (line[1], NYI)

    def c_look(self, line):
        return 'you look at: %s    %s' % (line[1], NYI)

    def c_oldboard(self, line):
        return 'you see the oldboard of: %s    %s' % (line[1], NYI)

    def c_oldmoves(self, line):
        return 'you see your old moves    %s' % NYI

    def c_away(self, line):
        return 'you are away    %s' % NYI

    def c_back(self, line):
        return 'welcome back    %s' % NYI

    def c_bye(self, line):
        return 'bye, bye    %s' % NYI

    def c_wave(self, line):
        return 'you wave goodbye    %s' % NYI

# ----------------------------------------  Setting Commands

    def c_toggle(self, line):
        return "you toggle '%s'" % line[1], NYI

    def c_set(self, line):
        return "you set '%s'" % line[1], NYI
    
    def c_address(self, line):
        return "you set your address to '%s'" % line[1], NYI

    def c_password(self, line):
        return "you changed your password to '%s'" % line[1], NYI

    def c_save(self, line):
        return "you save your settings", NYI

# ----------------------------------------  General Info

    def c_help(self, line):
        return 'die Hilfe gibt es noch nicht    %s' % NYI

    def c_show(self, line):
        return 'shown: %s    %s' % (line[1], NYI)

    def c_who(self, line):
        return 'list of some ore more players    %s' % NYI

    def c_where(self, line):
        return 'where is %s from' % (line[1], NYI)

    def c_rawwho(self, line):
        return 'raw where is %s from' % (line[1], NYI)

    def c_whois(self, line):
        return 'info about player: %s    %s' % (line[1], NYI)

    def c_ratings(self, line):
        return 'ratings given    %s' % NYI

    def c_last(self, line):
        return 'info about last player    %s' % NYI

    def c_time(self, line):
        return 'it is 5 past 12    %s' % NYI

# ----------------------------------------  FIBS Info

    def c_motd(self, line):
        return 'an apple a day keeps the doctor away :)    %s' % NYI

    def c_about(self, line):
        return 'about SIBS    %s' % NYI

    def c_average(self, line):
        return 'the average is about 8.3    %s' % NYI

    def c_dicetest(self, line):
        return 'the dice are nice and cubic    %s' % NYI

    def c_version(self, line):
        return 'SIBS/clip 0.01    %s' % NYI

    def c_stat(self, line):
        return 'status of SIBS    %s' % NYI

# ----------------------------------------  Other Commands

    def c_clear(self, line):
        return 'other commands    %s' % NYI

    def c_erase(self, line):
        return 'other commands    %s' % NYI

    def c_shutdown(self, line):
        return 'other commands    %s' % NYI

# ----------------------------------------  Undocumented Commands

    def c_port(self, line):
        return 'undocumented commands    %s' % NYI

    def c_name(self, line):
        return 'undocumented commands    %s' % NYI

    def c_co(self, line):
        return 'undocumented commands    %s' % NYI

    def c_ne(self, line):
        return 'undocumented commands    %s' % NYI

    def c_ye(self, line):
        return 'undocumented commands    %s' % NYI

# ----------------------------------------  Game Commands

    def c_roll(self, line):
        return 'you reject    %s' % NYI

    def c_move(self, line):
        return 'you move    %s' % NYI

    def c_off(self, line):
        return 'you bear off    %s' % NYI

    def c_board(self, line):
        return 'you get a new board    %s' % NYI

    def c_pip(self, line):
        return 'you are 7 pips behind    %s' % NYI

    def c_double(self, line):
        return 'you double    %s' % NYI

    def c_accept(self, line):
        return 'you accept    %s' % NYI

    def c_reject(self, line):
        return 'you reject    %s' % NYI

    def c_resign(self, line):
        return 'you resign    %s' % NYI

    def c_leave(self, line):
        return 'you leave the game    %s' % NYI

    def c_redouble(self, line):
        return 'you redouble    %s' % NYI

    def c_beaver(self, line):
        return 'you beaver    %s' % NYI

    def c_raccoon(self, line):
        return 'you raccoon    %s' % NYI

    def c_otter(self, line):
        return 'you otter    %s' % NYI

    def c_panic(self, line):
        return "don't panic ... where is your towel    %s" % NYI

# ----------------------------------------  ====================

    def unknown(self, line):
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
