#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Erste Implementierung des SIBS-Protokolls.
Siehe fibs_interface.html.
"""

REV = '$Revision$'

from StringIO import StringIO
import inspect
import sibs_utils as utils
from tz_utils import TZ
from help import Help
from version import Version

VERSION = Version()
VERSION.register(__name__, REV)

ZONEINFO = TZ()

## where
## waitfor
## gag
## last   
## stat
## off
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
        aliases = (('k', 'kibitz'),
                   ('t', 'tell'),
                   ('tellx', 'tell'),
                   ('s', 'say'),
                   ('m', 'move'),
                   ('resi', 'resign'),
                   ('ver', 'version'),
                   ('adios', 'bye'),
                   ('ciao', 'bye'),
                   ('end', 'bye'),
                   ('exit', 'bye'),
                   ('logout', 'bye'),
                   ('quit', 'bye'),
                   ('tschoe', 'bye'),
                   )
        for k,v in aliases:
            self.commands[k] = self.commands[v]

# ----------------------------------------  Chat and Settings for other Players

    def c_shout(self, line, me):            # implemented
        if me.toggles.read('silent'):
            return "** Please type 'toggle silent' again before you shout."
        else:
            me.shout(' '.join(line[1:]))

    def c_kibitz(self, line, me):           # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        watchee = me.is_watching()
        if (game is None) and (not watchee):
            return "** You're not watching or playing."
        else:
            msg = ' '.join(line[1:])
            whisper = line[0].lower() == 'whisper'
            me.kibitz(msg, whisper)

    c_whisper = c_kibitz                    # implemented

    def c_tell(self, line, me):             # implemented
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_active(name, None)
        if user is None:
            return '** There is no one called %s' % name
        elif user.is_gagged(me.name):
            return "** %s won't listen to you." % name
        elif me.is_gagged(name):
            return "** You can't talk if you won't listen."
        elif name == me.name:
            msg = "You say to yourself: %s" % msg
        me.tell(user, msg)

    def c_say(self, line, me):              # implemented
        game, player = self.list_of_games.get_game_from_user(me)
        if game is None:
            return "** 'say' can't be used outside a game."
        else:
            msg = ' '.join(line[1:])
            user = game.players(player).opponent.user
            me.say(user, msg)  # TODO: stimmt das jetzt so?

    def c_message(self, line, me):          # implemented
        name = line[1]
        msg = ' '.join(line[2:])
        user = self.list_of_users.get_from_all(name, None)
        if user is None:
            return "Don't know user %s" % name
        else:
            me.send_message(user, msg)
            # TODO: complete message alltogether

    def c_waitfor(self, line, me):
        return '** waitfor %s' % NYI

    def c_gag(self, line, me):              # implemented
        arglen = len(line)
        if arglen == 1:
            return me.show_gagged()
        else:
            name = line[1]
            user = self.list_of_users.get_active(name, None)
            if user is None:
                return "** There is no one called '%s'" % name
            elif name == me.name:
                return "** You talk too much, don't you?"                
            else:
                return me.gag(name)

    def c_blind(self, line, me):            # implemented
        arglen = len(line)
        if arglen == 1:
            return me.show_blinded()
        else:
            name = line[1]
            user = self.list_of_users.get_active(name, None)
            if user is None:
                return "** There is no one called '%s'" % name
            elif name == me.name:
                return "** You can't read this message now, can you?"                
            else:
                return me.blind(name)

# ----------------------------------------  Between Game Actions

    def c_invite(self, line, me):           # implemented
        if not me.ready():
            me.toggles.toggle('ready',)
            self.update_who(me)
        if len(line) < 2:
            return '** invite who?'
        user = line[1]
        if user == me.name:
            return "** You can't invite yourself."
        him = self.list_of_users.get_active(user)
        if him is None:
            return '** There is no one called %s.' % user
        if him.is_playing():            # TODO: dies hier und ready
                                        #       das muss doch über status eleganter gehen
            return '** %s is already playing with someone else.' % user
        if not him.ready():
            return '** %s is refusing games.' % user
                        # TODO:    hier fehlen noch ne Menge Fälle
        if len(line) > 2:
            ML = line[2]
            msg_invite = '%s wants to play a %s point match with you.' % \
                                                                 (me.name, ML)
            msg_reflect = '** You invited %s to a %s point match.' % (user, ML,)
        else:
            ML = None
            msg_invite = '%s wants to resume a saved match with you.' % me.name
            msg_reflect = '** You invited %s to resume a saved match.' % user
        if me.invite(user, ML, him):
            him.chat(msg_invite)
            return msg_reflect
        else:
            return "** There's no saved match with" \
                                    " %s. Please give a match lenth." % user

    def c_join(self, line, me):             # implemented
        if me.is_playing():
            me.continue_match()
            return
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
            him.join(me, self.list_of_games)    # TODO: deferred? still a good
                                                #       idea; join seems to take
                                                #       about > .1 seconds
            self.update_who(me)                 # this update is very important
            self.update_who(him)                # for the clients - see #0061
        else:
            return "** %s is not logged in" % user

    def c_watch(self, line, me):            # implemented
        if me.is_watching():
            me.chat(self.c_unwatch(line, me))
        if me.is_playing():
            return "** You can't watch another game while you're playing."
        if len(line) < 2:
            return "** Watch who?"
        user = line[1]
        if user == me.name or me.info.special == 'banned':
            return "** Use a mirror to do that."
        him = self.list_of_users.get_active(user)
        if him is None:
            return "** There's no one called %s." % user
        if him.is_blinded(me.name):
            return "** %s doesn't want you to watch." % him.name
        if him.is_playing and him.status.opponent.is_blinded(me.name):
            return "** %s doesn't want you to watch." % him.status.opponent.name
        ret = "You're now watching %s" % user
        if not him.is_playing():
            ret += '\n%s is not doing anything interesting.' % user
        him.watch(me)
        return ret

    def c_unwatch(self, line, me):          # implemented
        watchee = me.is_watching()
        if watchee:
            me.unset_watching()
            return 'You stop watching %s' % watchee
        else:
            return "** You're not watching"

    def c_look(self, line, me):             # implemented
        if len(line) < 2:
            return "** Look at who?"
        user = line[1]
        if user is me.name or me.info.special == 'banned':
            return "You look great."
        him = self.list_of_users.get_active(user)
        if him is None:
            return "** There's no one called %s." % user
        if him.is_blinded(me.name):
            return "** %s doesn't want you to look." % him.name
        if him.is_playing and him.status.opponent.is_blinded(me.name):
            return "** %s doesn't want you to look." % him.status.opponent.name
        if not him.is_playing():
            return '%s is not playing.' % user
        board = me.settings.get_boardstyle()
        game, player = self.list_of_games.get_game_from_user(him)
        if game is None:        # playing safe: game might just have ended
            if not hasattr(me.status.watchee, 'running_game'):
                return "** %s is not playing." % watchee
        return game.control.board.show_board(player, board, watcher=True)

    def c_oldboard(self, line, me):
        return '** oldboard %s' % NYI

    def c_oldmoves(self, line, me):
        return '** oldmoves %s' % NYI

    def c_away(self, line, me):             # implemented
        if len(line) < 2:
            awayees = self.list_of_users.get_sorted_keys(ufilter='away',)
            if len(awayees) == 0:
                return "None of the users is away."
            else:
                out = StringIO()
                print >>out, "The following users are away:"
                for a in awayees:
                    user = self.list_of_users.get_from_all(a)
                    print >>out, user.get_away_message(me.name)
                ret = out.getvalue()
                #out.close()
                return ret
            # TODO: away message at 'invite' fehlt
        else:
            away_message = ' '.join(line[1:])
            me.set_away(away_message)
            return "You're away. Please type 'back'."

    def c_back(self, line, me):             # implemented
        if not me.is_away():
            ret = "** You're not away."
        else:
            me.set_back()
            ret = "Welcome back."
        return ret

    def c_bye(self, line, me):              # implemented
        # TODO: unklar ist, welche Texte gesendet werden, wenn
        #       1) bye
        #       2) netzwerkfehler
        #       3) sonstwas(???)
        #       vorliegt.
        me.protocol.logout()

    def c_wave(self, line, me):             # implemented
        return me.wave()

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
            return me.settings.boardstyle(values[0])
        
        def linelength(*values):
            return me.settings.linelength(values[0])
            
        def pagelength(*values):
            return me.settings.pagelength(values[0])

        def redoubles(*values):
            return me.settings.redoubles(values[0])

        def sortwho(*values):
            return me.settings.sortwho(values[0])

        def timezone(*values):
            return me.settings.timezone(values[0])

        def delay(*values):
            return me.settings.delay(values[0])

        def show_settings():
            return me.settings.show()

        def alias(keys, v):
            for k in keys:
                if k.startswith(v):
                    return keys[k]
            return None

        # TODO: das hier kann man stark vereinfachen!!! etwas programmierarbeit
        
        sub_commands = {'boardstyle': boardstyle,
                        'linelength': linelength,
                        'pagelength': pagelength,
                        'redoubles': redoubles,
                        'sortwho': sortwho,
                        'timezone': timezone,
                        'delay': delay,
                        }
        arglen = len(line)
        if arglen == 1:
            res = show_settings()
        else:
            cmd = sub_commands.get(line[1], alias(sub_commands, line[1]))
            if cmd is None:
                res = "** Invalid argument. Type 'help set'."
            else:
                res = cmd(line[2:])
        return res
    
    def c_address(self, line, me):          # implemented
        arglen = len(line)
        if arglen == 1:
            ret = "** You didn't give your address."
        else:
            me.set_address(line[1])
            ret = "Your email address is '%s'." % line[1]
            who = self.c_rawwho(['rawwho', me.name], me)
            me.protocol.schedule_broadcast(who) # TODO: bitte direkt broadcast
                                                # und dann schedule... entfernen
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


    def c_show(self, line, me):             # implemented
        if len(line) < 2:
            return "** show what?"
        command = line[1]
        if not command in ('games','saved','savedcount','watchers','max',):
            return "** Don't know how to show %s" % command
        out = StringIO()
        if command == 'games':
            print >>out, 'List of games:'
            print >>out, self.list_of_games.show_games()
        if command == 'saved':
            saved = me.show_saved()
            if saved == '':
                print >>out, 'no saved games.'
            else:
                print >>out, '  opponent          matchlength   score' \
                                                      '(your points first)'
                print >>out, saved
        if command == 'savedcount':
            if len(line) > 2:
                name = line[2]
                him = self.list_of_users.get_from_all(name)
                if him is None:
                    print >>out, "** There is no user called '%s'." % name
                    saved = -1
                else:
                    saved = len(him.info.saved_games)
            else:
                name = me.name
                saved = len(me.info.saved_games)
            if saved == 0:
                print >>out, '%s has no saved games. ' % name
            elif saved == 1:
                print >>out, '%s has 1 saved game. ' % name
            elif saved > 1:
                print >>out, '%s has %d saved games. ' % (name, saved)
        if command == 'watchers':
            print >>out, 'Watching players:'
            for u in self.list_of_users.get_watchers():
                print >>out, '%s is watching %s.' % (u.name, u.is_watching())
        if command == 'max':
            print >>out, 'max_logins is %d (maximum: 1000)' % \
                                   me.protocol.factory.maxProtocols
        return out.getvalue()

    def c_info(self, line, me):
        return me.info.show()

    def c_invitations(self, line, me):
        out = StringIO()
        print >>out, 'online', me.online()
        print >>out, 'invita', me.invitations
        return out.getvalue()

    def c_who(self, line, me):              # implemented
        # TODO: wieder gerade ziehen
        #       user=None kommt weg und wird ersetzt durch "who user"
        #       Implementieren von "who" mit parametern
        lou = self.list_of_users
        loau = lou.get_active_users()
        sort_who = me.settings.get_sortwho()
        if len(line) == 1:
            users = lou.get_sorted_keys(sort = sort_who)
        elif line[1] in ('away','ready','playing','count','from'):
            users = lou.get_sorted_keys(ufilter=line[1], sort = sort_who)
            # TODO: weiteres argument holen, abfragen
        else:
            user = lou.get_active(line[1])
            if not user is None:
                users = [user.name.lower(),]
            else:
                return "** There is no one called '%s'" % line[1]
        out = StringIO()
        if len(users) == 0:     # TODO: was soll diese erste Bedingung??? nur wenn die Liste leer ist???????
            print >>out, 'No  S  username        rating   exp login  idle from'
        else:
##            print 'in who()', users
            for u in users:
                print >>out, loau[u].who()
            # TODO:  laut spez wird nur beim rawwho die 6 garantiert geschickt
            #        aber javafibs kriegt die 6 und schickt nur n ordinaeres who
            print >>out, '6'
        return out.getvalue()

    def c_where(self, line, me):
        return '** where %s' % NYI

    def c_rawwho(self, line, me):           # implemented
        out = StringIO()
        print >>out, self.c_who(line, me),
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
        return '** ratings %s' % NYI

    def c_last(self, line, me):
        return '** last %s' % NYI

    def c_time(self, line, me):             # implemented
        if len(line) == 1:
            zone = me.settings.get_timezone()
            ret = ZONEINFO.long_time(zone=zone)
        if len(line) > 1:
            if ZONEINFO.is_valid(line[1]):
                ret = ZONEINFO.long_time(zone=line[1])
            else:
                ret = "Can't find timezone '%s'. Try one of: \n" % line[1] + \
                                                                  ZONEINFO.text
        return ret

    c_date = c_time

# ----------------------------------------  SIBS Info

    def c_motd(self, line, me):             # implemented
        return utils.render_file('motd')

    def c_about(self, line, me):            # implemented
        return utils.render_file('about')

    def c_news(self, line, me):             # implemented
        return utils.render_file('news')

    def c_average(self, line, me):
        return '** average %s' % NYI

    def c_dicetest(self, line, me):
        return '** dice  %s' % NYI

    def c_version(self, line, me):          # implemented
        # TODO: version line wie in fibs
        return 'TGS  %s' % VERSION.version()

    def c_stat(self, line, me):
        return '** status %s' % NYI

# ----------------------------------------  Other Commands

    def c_clear(self, line, me):
        return '** clear %s' % NYI

    def c_erase(self, line, me):
        return '** erase %s' % NYI

    def c_shutdown(self, line, me):
        return '** shutdown %s' % NYI

# ----------------------------------------  Undocumented Commands

    def c_port(self, line, me):
        return '** undocumented commands    %s' % NYI

    def c_name(self, line, me):             # implemented
        return "** You're not supposed to change your name."

    def c_co(self, line, me):
        return '** undocumented commands    %s' % NYI

    def c_ne(self, line, me):
        return '** undocumented commands    %s' % NYI

    def c_ye(self, line, me):
        return '** undocumented commands    %s' % NYI

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

    def c_off(self, line, me):
        return '** off %s' % NYI

    def c_board(self, line, me):            # implemented
        # TODO: Fehlerbehandlung
        game, player = self.list_of_games.get_game_from_user(me)
        watchee = me.is_watching()
        state = False
        if (game is None) and (not watchee):
            return "** You're not playing."
        else:
            board = me.settings.get_boardstyle()
            if game is None:
                if not hasattr(me.status.watchee, 'running_game'):
                    return "** %s is not playing." % watchee
                else:
                    state = True
                    game, player = self.list_of_games.get_game_from_user\
                                                           (me.status.watchee)
            return game.control.board.show_board(player, board, watcher=state)

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
            return '** You terminated the game. The game was saved.'

    def c_redouble(self, line, me):
        return '** redouble %s' % NYI

    def c_beaver(self, line, me):
        return '** beaver %s' % NYI

    def c_raccoon(self, line, me):
        return '** raccoon %s' % NYI

    def c_otter(self, line, me):
        return '** otter %s' % NYI

    def c_panic(self, line, me):
        return "** don't panic ... where is your towel %s" % NYI

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
        who = self.c_rawwho(['rawwho', me.name], me)
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
