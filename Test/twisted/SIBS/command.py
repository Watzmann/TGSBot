#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

REV = '$Revision$'

from StringIO import StringIO
import inspect
import sibs_utils as utils
from help import Help
from version import Version

VERSION = Version()
VERSION.register(__name__, REV)

## 0
## x tell
## x help
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
## x pip
## x leave
##
## x register
## x authentication
## x CLIP

## 3
## x say               0
## x invite
## x join
## show
## stat
## off
## double
## x accept
## x reject
## x resign
## redouble

NYI = 'is not implemented, yet'

class Command():
    def __init__(self, lou, log):
        self.commands = dict(self.sample_commands())
        self.list_of_implemented_commands = self.list_implemented()
        self.list_of_users = lou
        self.list_of_games = log   # TODO: was besseres als log (log ist logging)
        print 'implemented commands:', self.list_of_implemented_commands
        self.help = Help(self.list_of_implemented_commands)

# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line, me):            # implemented
        if me.toggles.read('silent'):
            return "** Please type 'toggle silent' again before you shout."
        else:
            me.shout(' '.join(line[1:]))

    def c_kibitz(self, line, me):           # implemented
        self.c_say(line, me)        # TODO: notbehelf - reparieren!!!

    def c_tell(self, line, me):             # implemented
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_active(name, None)
        if user is None:
            return '%s is not here' % name
        else:
            me.tell(user, msg)

    def c_say(self, line, me):              # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** 'say' can't be used outside a game."
        else:
            msg = ' '.join(line[1:])
            user = game.players(player).opponent.user
            me.tell(user, msg)

    def c_whisper(self, line, me):
        return '** whisper %s' % NYI

    def c_message(self, line, me):          # implemented
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_from_all(name, None)
        if user is None:
            return "Don't know user %s" % name
        else:
            me.send_message(user, msg)

    def c_waitfor(self, line, me):
        return 'waitfor %s' % NYI

    def c_gag(self, line, me):
        return 'gag %s' % NYI

    def c_blind(self, line, me):
        return 'blind %s' % NYI


# ----------------------------------------  Between Game Actions

    def c_invite(self, line, me):           # implemented
        if len(line) < 2:
            return '** invite who?'
        user = line[1]
        if user == me.name:
            return "** You can't invite yourself."
        if len(line) > 2:
            ML = line[2]
        else:                           # TODO:    resume organisieren
            return '++ no resume of saved games implemented, yet.'
        him = self.list_of_users.get_active(user)
        if him is None:
            return '** There is no one called %s.' % user
        if him.is_playing():            # TODO: dies hier und ready
                                        #       das muss doch über status eleganter gehen
            return '** %s is already playing with someone else.' % user
        if not him.ready():
            return '** %s is refusing games.' % user
                        # TODO:    hier fehlen noch ne Menge Fälle
        me.invite(user, ML)
        him.chat('%s wants to play a %s point match with you.' % (me.name, ML))
        return '** You invited %s to a %s point match.' % (user, ML,)

    def c_join(self, line, me):             # implemented
        if len(line) < 2:
            return "** Error: Join who?"    # TODO: noch nicht komplett
        user = line[1]
        him = self.list_of_users.get_active(user)
        if not him is None:
            if not him.is_ready():
                return "** %s is refusing games." % user
            if him.is_playing():
                return "** Error: %s is already playing with someone else." % \
                                                                           user
                # TODO: didn't invite you????
            him.join(me, self.list_of_games)    # TODO: deferred?
            self.update_who(me)
            #self.update_who(him)       # TODO: broadcast doppelt, kann weg
        else:
            return "** %s is not logged in" % user

    def c_watch(self, line, me):
        return 'watch %s' % NYI

    def c_unwatch(self, line, me):
        return 'unwatch %s' % NYI

    def c_look(self, line, me):
        return 'look %s' % NYI

    def c_oldboard(self, line, me):
        return 'oldboard %s' % NYI

    def c_oldmoves(self, line, me):
        return 'oldmoves %s' % NYI

    def c_away(self, line, me):
        return 'away %s' % NYI

    def c_back(self, line, me):
        return 'back %s' % NYI

    def c_bye(self, line, me):              # implemented
        # TODO: unklar ist, welche Texte gesendet werden, wenn
        #       1) bye
        #       2) netzwerkfehler
        #       3) sonstwas(???)
        #       vorliegt.
        me.protocol.logout()

    def c_wave(self, line, me):             # implemented
        return me.wave()

    def c_adios(self, line, me):            # implemented
        return self.c_bye(line, me)
    def c_ciao(self, line, me):             # implemented
        return self.c_bye(line, me)
    def c_end(self, line, me):              # implemented
        return self.c_bye(line, me)
    def c_exit(self, line, me):             # implemented
        return self.c_bye(line, me)
    def c_logout(self, line, me):           # implemented
        return self.c_bye(line, me)
    def c_quit(self, line, me):             # implemented
        return self.c_bye(line, me)
    def c_tschoe(self, line, me):           # implemented
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
                if switch == 'autoroll':
                    toggles.toggle('double')
                if switch == 'double':
                    toggles.toggle('autoroll')
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
    
    def c_address(self, line, me):          # implemented
        arglen = len(line)
        if arglen == 1:
            ret = "** You didn't give your address."
        else:
            me.set_address(line[1])
            ret = "Your email address is '%s'." % line[1]
            who = self.c_rawwho(['rawwho',], me, user=me)
            me.protocol.schedule_broadcast(who)
        return ret
  
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

    def c_save(self, line, me):             # implemented
        me.save_settings()
        return "Settings saved."

# ----------------------------------------  General Info

    def c_help(self, line, me):             # implemented
        if len(line) == 1:
            line.append('help')
        return ''.join(self.help.help_(line[1]))

    def c_show(self, line, me):
        return 'show %s' % NYI

    def c_info(self, line, me):
        return me.info.show()

    def c_who(self, line, me, user=None):   # implemented
        # TODO: wieder gerade ziehen
        #       user=None kommt weg und wird ersetzt durch "who user"
        #       Implementieren von "who" mit parametern
#        if user is None:
        lou = self.list_of_users
        loau = lou.get_active_users()
        sort_who = me.settings.get_sortwho()
        if len(line) == 1:
            users = lou.get_sorted_keys(sort = sort_who)
        elif line[1] in ('away','ready','playing','count','from'):
            users = lou.get_sorted_keys(ufilter=line[1], sort = sort_who)
        else:
            user = lou.get_active(line[1])
            if not user is None:
                users = [user.name,]
            else:
                return "** There is no one called '%s'" % line[1]

        out = StringIO()
        if len(users) == 0:
            print >>out, 'No  S  username        rating   exp login  idle from'
        else:
            for u in users:
                print >>out, loau[u].who()
            # TODO:  laut spez wird nur beim rawwho die 6 garantiert geschickt
            #        aber javafibs kriegt die 6 und schickt nur n ordinaeres who
            print >>out, '6'
        return out.getvalue()

    def c_where(self, line, me):
        return 'where %s' % NYI

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
            res = self.list_of_users.whois(name)
        return res

    def c_ratings(self, line, me):
        return 'ratings %s' % NYI

    def c_last(self, line, me):
        return 'last %s' % NYI

    def c_time(self, line, me):
        return 'time %s' % NYI

# ----------------------------------------  SIBS Info

    def c_motd(self, line, me):             # implemented
        return utils.render_file('motd')

    def c_about(self, line, me):            # implemented
        return utils.render_file('about')

    def c_news(self, line, me):             # implemented
        return utils.render_file('news')

    def c_average(self, line, me):
        return 'average %s' % NYI

    def c_dicetest(self, line, me):
        return 'dice  %s' % NYI

    def c_version(self, line, me):          # implemented
        # TODO: version line wie in fibs
        return 'TGS  %s' % VERSION.version()

    def c_stat(self, line, me):
        return 'status %s' % NYI

# ----------------------------------------  Other Commands

    def c_clear(self, line, me):
        return 'clear %s' % NYI

    def c_erase(self, line, me):
        return 'erase %s' % NYI

    def c_shutdown(self, line, me):
        return 'shutdown %s' % NYI

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
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        else:
            game.roll(player)

    def c_move(self, line, me):             # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        else:
            game.move(line[1:], player)

    def c_m(self, line, me):                # implemented
        self.c_move(line, me)

    def c_off(self, line, me):
        return 'off %s' % NYI

    def c_board(self, line, me):            # implemented
        # TODO: Fehlerbehandlung
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        else:
            board = me.settings.get_boardstyle()
            return game.control.board.show_board(player, board)

    def c_pip(self, line, me):              # implemented
        # TODO:  abfragen, ob beide Spieler das erlauben
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        else:
            return game.pips(player)

    def c_double(self, line, me):
        game, player = self.list_of_games.get(me.running_game)
        if game is None:
            return "** You're not playing."
        else:
            game.double(player)

    def c_accept(self, line, me):           # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        else:
            game.accept(player)

    def c_reject(self, line, me):           # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing, so you can't give up."
        else:
            game.reject(player)

    def c_resign(self, line, me):           # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** You're not playing."
        arglen = len(line)
        value_names = ('n', 'normal', 'g', 'gammon', 'b', 'backgammon')
        values = dict(zip(value_names, (1,1,2,2,3,3)))
        if (arglen < 2) or (not line[1] in value_names):
            return "** Type 'n' (normal), 'g' (gammon) or 'b' (backgammon) " \
                                                              "after resign."
        else:
            game.resign(player, values[line[1]])

    def c_leave(self, line, me):            # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** Error: No one to leave."
        else:
            me.leave_game()  # TODO: korrekte ausgaben/fehlerchecking
            return '** You terminated the game. Saving games is not implemented, yet'

    def c_redouble(self, line, me):
        return 'redouble %s' % NYI

    def c_beaver(self, line, me):
        return 'beaver %s' % NYI

    def c_raccoon(self, line, me):
        return 'raccoon %s' % NYI

    def c_otter(self, line, me):
        return 'otter %s' % NYI

    def c_panic(self, line, me):
        return "don't panic ... where is your towel %s" % NYI

# ----------------------------------------  ====================

    def unknown(self, line, me):
        return "** Unknown command: '%s'" % line[0]

    def command(self, cmd):
##        print self.commands.get(cmd, self.unknown)
        return self.commands.get(cmd.lower(), self.unknown)

    def sample_commands(self,):
        # TODO: falls man mal commands in den laufenden server injizieren will:
        #       als Plugin realisieren
        # TODO: inspect.getmembers() halte ich nicht für der Weisheit letzten
        #       Schluss; vielleicht gibt es da eine bessere (offiziellere) Lösung
        lofc = [(f[0][2:],f[1]) for f in inspect.getmembers(self) \
                  if inspect.ismethod(f[1]) and f[0].startswith('c_')]
        return lofc

    def update_who(self, me):
        factory = me.protocol.factory
        who = self.c_rawwho(['rawwho',], me, user=me)
        factory.broadcast(who,)

    def list_implemented(self, verbose=False):
        imp = self.commands.keys()[:]
        imp.sort()
        for c in imp[:]:
            try:
                ret = self.commands[c]([c,'list',],None)
##                print c
##                print ret
                if ret.endswith(NYI):
##                    print 'removed', c
                    imp.remove(c)
            except:
                pass
        return imp

if __name__ == "__main__":
    c = Command(None, None)
    print c.c_version(1,2)
    for i in c.list_implemented():
        print i
