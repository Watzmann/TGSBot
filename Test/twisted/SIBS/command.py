#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

import inspect
 
class Command():
    def __init__(self,):
        self.commands = dict(self.sample_commands())
        print 'available commands:', self.commands.keys()
        
    def c_show(self, line):
        return 'shown'

    def c_help(self, line):
        return 'die Hilfe gibt es noch nicht'

    def c_toggle(self, line):
        return "you toggle '%s'" % line[1]

    def c_reject(self, line):
        return 'you reject'

    def c_invite(self, line):
        return 'you invited %s for a match of length %s' % (line[1], line[2])

    def c_watch(self, line):
        return 'you now watch', line[1]

    def c_rating(self, line):
        return 'rating given'

    def c_unknown(self, line):
        return 'unknown command %s' % line[0]

# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line):
        return 'you shout', line[1:]

    def c_kibitz(self, line):
        return 'you kibitz', line[1:]

    def c_tell(self, line):
        return 'you tell', line[1:]

    def c_say(self, line):
        return 'you say', line[1:]

    def c_whisper(self, line):
        return 'you whisper', line[1:]

    def c_message(self, line):
        return 'message sent to %s: %s' % (line[1], line[2:])

    def c_waitfor(self, line):
        return 'you now wait for', line[1]

    def c_gag(self, line):
        return 'you gagged', line[1]

    def c_blind(self, line):
        return 'you blinded', line[1]


# ----------------------------------------  Between Game Actions



# ----------------------------------------  ====================

    def command(self, cmd):
        print self.commands.get(cmd, self.c_unknown)
        return self.commands.get(cmd, self.c_unknown)

    def sample_commands(self,):
        # TODO: falls man mal commands in den laufenden server injizieren will:
        #       als Plugin realisieren
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0].lstrip('c_'),f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('c_')]
        return lofc
