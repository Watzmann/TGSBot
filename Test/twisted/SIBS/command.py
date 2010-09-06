#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

REV = '$Revision$'

from StringIO import StringIO
import inspect
import sibs_utils as utils
from version import Version

VERSION = Version()
VERSION.register(__name__, REV)

## 0
## x tell
## 0 help
## 0 motd
## x version

## 1
## x bye
## x wave
## where
## time
## 0 about

## x persistency

## 2
## x message
## waitfor
## gag
## x password
## x whois
## last   
## x roll
## x move
## x board
## pip
## leave             0
##
## register
## authentication
## CLIP


## 3
## say               0
## x invite
## x join
## show
## stat
## off
## double
## accept
## reject
## resign
## redouble

NYI = '##NYI##'

class Command():
    def __init__(self, lou, log):
        self.commands = dict(self.sample_commands())
        self.list_of_users = lou
        self.list_of_games = log   # TODO: was besseres als log (log ist logging)
        print 'available commands:', self.commands.keys()
        
# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line, me):
        return 'you shout: %s    %s' % (line[1:], NYI)

    def c_kibitz(self, line, me):
        return 'you kibitz: %s    %s' % (line[1:], NYI)

    def c_tell(self, line, me):             # implemented
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_active(name, None)
        if user is None:
            return '%s is not here' % name
        else:
            me.tell(user, msg)

    def c_say(self, line, me):
        return 'you say: %s    %s' % (line[1:], NYI)

    def c_whisper(self, line, me):
        return 'you whisper: %s    %s' % (line[1:], NYI)

    def c_message(self, line, me):
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_from_all(name, None)
        if user is None:
            return "Don't know user %s" % name
        else:
            me.send_message(user, msg)
##        return 'message sent to %s: %s    %s' % (line[1], line[2:], NYI)

    def c_waitfor(self, line, me):
        return 'you now wait for: %s    %s' % (line[1], NYI)

    def c_gag(self, line, me):
        return 'you gagged: %s    %s' % (line[1], NYI)

    def c_blind(self, line, me):
        return 'you blinded: %s    %s' % (line[1], NYI)


# ----------------------------------------  Between Game Actions

    def c_invite(self, line, me):           # implemented
        user = line[1]
        ML = line[2]
        him = self.list_of_users.get_active(user)
        me.invite(user, ML)
        him.chat('%s wants to play a %s point match with you.' % (me.name, ML))
        msg = '** You invited %s to a %s point match.' % (user, ML,)
        return msg

    def c_join(self, line, me):             # implemented
        user = line[1]
        him = self.list_of_users.get_active(user)
        if not him is None:
            him.join(me, self.list_of_games)    # TODO: deferred
            msg = '** You are now playing a n point match with %s.' % user
        else:
            msg = "user %s is not logged in" % user
        return msg

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

    def c_bye(self, line, me):              # implemented
        # TODO: unklar ist, welche Texte gesendet werden, wenn
        #       1) bye
        #       2) netzwerkfehler
        #       3) sonstwas(???)
        #       vorliegt.
        me.protocol.logout()

    def c_wave(self, line, me):             # implemented
        return me.wave()

    def c_adios(self, line, me):
        return self.c_bye(line, me)
    def c_ciao(self, line, me):
        return self.c_bye(line, me)
    def c_end(self, line, me):
        return self.c_bye(line, me)
    def c_exit(self, line, me):
        return self.c_bye(line, me)
    def c_logout(self, line, me):
        return self.c_bye(line, me)
    def c_quit(self, line, me):
        return self.c_bye(line, me)
    def c_tschoe(self, line, me):
        return self.c_bye(line, me)

# ----------------------------------------  Setting Commands

    def c_toggle(self, line, me):           # implemented
        toggles = me.toggles
        arglen = len(line)
        if arglen == 1:
            res = toggles.show()
        else:
            switch = toggles.has(line[1], None)
            if switch is None:
                res = "** Don't know how to toggle %s." % line[1]
            else:
                res = toggles.toggle(switch)
                if switch == 'ready':
                    self.update_who(me)
        return res

    def c_set(self, line, me):              # implemented
        
        def boardstyle(*values):
##            print 'in boardstyle of', me.name, 'with', values
            return me.settings.boardstyle(values[0])
        
        def linelength(*values):
##            print 'in linelength of', me.name, 'with', values
            return me.settings.linelength(values[0])
            
        def pagelength(*values):
##            print 'in pagelength of', me.name, 'with', values
            return me.settings.pagelength(values[0])

        def redoubles(*values):
##            print 'in redoubles of', me.name, 'with', values
            return me.settings.redoubles(values[0])

        def sortwho(*values):
##            print 'in sortwho of', me.name, 'with', values
            return me.settings.sortwho(values[0])

        def timezone(*values):
##            print 'in timezone of', me.name, 'with', values
            return me.settings.timezone(values[0])

        def show_settings():
##            print 'in timezone of', me.name, 'with', values
            return me.settings.show()

        # TODO: das hier kann man stark vereinfachen!!! etwas programmierarbeit
        
        sub_commands = {'boardstyle': boardstyle,
                        'linelength': linelength,
                        'pagelength': pagelength,
                        'redoubles': redoubles,
                        'sortwho': sortwho,
                        'timezone': timezone,
                        }
##        print 'the line', line
        arglen = len(line)
        if arglen == 1:
            res = show_settings()
        else:
            cmd = sub_commands.get(line[1], None)
            if cmd is None:
                res = "** Invalid argument. Type 'help set'."
            else:
                res = cmd(line[2:])
##        print 'the result', res
        return res
    
    def c_address(self, line, me):
        return "you set your address to '%s'" % line[1], NYI

    def c_password(self, line, me):         # implemented
        msgs = ("Password changed.",
                """** usage: password <old password>:<new password>:<new password>
** NOTE: The character between the passwords is now a colon!""",
                "** Sorry. Old password not correct.",
                "** Please give your new password twice.",
                )
        arglen = len(line)
        if arglen == 1:
            ret = msgs[1]
        else:
            ret = me.change_password(line[1])
            ret = msgs[ret]
        return ret

    def c_save(self, line, me):
        return "you save your settings", NYI

# ----------------------------------------  General Info

    def c_help(self, line, me):             # implemented
        return utils.render_file('help')

    def c_show(self, line, me):
        return 'shown: %s    %s' % (line[1], NYI)

    def c_info(self, line, me):
        return me.info.show()

    def c_who(self, line, me, user=None):   # implemented
        # TODO: wieder gerade ziehen
        #       user=None kommt weg und wird ersetzt durch "who user"
        #       Implementieren von "who" mit parametern
        out = StringIO()
        if user is None:
            lou = self.list_of_users.get_active_users()
        else:
            lou = {user.name:user}
        users = lou.keys()
        # TODO          set sortwho auf  users  anwenden
        for u in users:
            print >>out, lou[u].who()
        # TODO:  laut spez wird nur beim rawwho die 6 garantiert geschickt
        #        aber javafibs kriegt die 6 und schickt nur n ordinaeres who
        print >>out, '6'
        return out.getvalue()

    def c_where(self, line, me):
        return 'where is %s from' % (line[1], NYI)

    def c_rawwho(self, line, me, user=None):  # implemented
        out = StringIO()
        print >>out, self.c_who(line, me, user),
##        print >>out, '6'
        # TODO   siehe TODO bei c_who()
        return out.getvalue()

    def c_whois(self, line, me):            # implemented
        arglen = len(line)
        if arglen == 1:
            res = "** please give a name as an argument."
        else:
            name = line[1]
            lou = self.list_of_users.get_active_users()
            if not name in lou:
                res = "No information found on user %s." % name
            else:
                res = lou[name].whois()
        return res

    def c_ratings(self, line, me):
        return 'ratings given    %s' % NYI

    def c_last(self, line, me):
        return 'info about last player    %s' % NYI

    def c_time(self, line, me):
        return 'it is 5 past 12    %s' % NYI

# ----------------------------------------  SIBS Info

    def c_motd(self, line, me):             # implemented
        return utils.render_file('motd')

    def c_about(self, line, me):            # implemented
        return utils.render_file('about')

    def c_average(self, line, me):
        return 'the average is about 8.3    %s' % NYI

    def c_dicetest(self, line, me):
        return 'the dice are nice and cubic    %s' % NYI

    def c_version(self, line, me):          # implemented
        # TODO: version line wie in fibs
        return 'SIBS  %s' % VERSION.version()

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

    def c_name(self, line, me):             # implemented
        return "** You're not supposed to change your name."

    def c_co(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_ne(self, line, me):
        return 'undocumented commands    %s' % NYI

    def c_ye(self, line, me):
        return 'undocumented commands    %s' % NYI

# ----------------------------------------  Game Commands

    def c_roll(self, line, me):             # implemented
        game, player = self.list_of_games.get(me.running_game)
        game.roll(player)

    def c_move(self, line, me):             # implemented
        game, player = self.list_of_games.get(me.running_game)
        game.move(line[1:], player)

    def c_off(self, line, me):
        return 'you bear off    %s' % NYI

# TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 
    def c_game(self, line, me):

        msg = utils.render_file('fake_game')

        return msg
# TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST 

    def c_board(self, line, me):            # implemented
        game, player = self.list_of_games.get(me.running_game)
        return game.control.board.show_board(player)

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
##        print self.commands.get(cmd, self.unknown)
        return self.commands.get(cmd, self.unknown)

    def sample_commands(self,):
        # TODO: falls man mal commands in den laufenden server injizieren will:
        #       als Plugin realisieren
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0].lstrip('c_'),f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('c_')]
        return lofc

    def update_who(self, me):
        factory = me.protocol.factory
        who = self.c_rawwho(['rawwho',], me, user=me)
        factory.broadcast(who,)
        
if __name__ == "__main__":
    c = Command(None, None)
    print c.c_version(1,2)
