#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

REV = '$Revision$'

from StringIO import StringIO
from time import time
from math import sqrt
from dice import getDice
from twisted.internet import reactor
import logging
from persistency import Persistent, Db
import game_utilities
from version import Version

v = Version()
v.register(__name__, REV)

DB_Games = 'db/games'

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.DEBUG,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('game')
logger.setLevel(logging.DEBUG)

class GamesList:        # TODO: mit UsersList in eine Klasse überführen
    """Keeps a list of active and saved games.
    GamesList is implemented as a Borg pattern.

    gid                 str     unique ids with postfix denoting player
                                <uid>.<pid>[.<pid>]

    Example:            1286806072940669.p1         player1
                        1286806072940669.w13.p1     watcher #13, watching pl
                        
    Lists are:
    
    active_games        dict    '<gid>': (game, <player>) <player> is p1,p2,...
    active_ids          list    containing active uids as used in the gids
"""
    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
                        # TODO: kann man das Borg Pattern ableitbar machen?
                        
    def __init__(self,):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'active_games'):
            self.active_games = {}
            self.active_ids = []
            self.db = Db(DB_Games, 'games').db
                            # TODO: hier so an der PersistenzKlasse
                            #       vorbeizuangeln ist schon krass!

    def add(self, game):
        for i in game.ids:
            self.active_games[i] = (game, game.player[i])
        self.active_ids.append(game.id)
        # TODO: denk dran, beim Ende des Spiels aufzuräumen

    def remove(self, game):
        for i in game.ids:
            del self.active_games[i]
        try:
            self.active_ids.remove(game.id)
        except ValueError:
            logger.error('Game id %s not in list of active ids!' % game.id)

    def show_games(self,):
        out = StringIO()
        for g in self.active_ids:
            game = self.get(g + '.p1')[0]
            print >>out, game.show_game()
        return out.getvalue()

    def get(self, gid, default=None):
        logger.info('returning gid %s' % gid)
        return self.active_games.get(gid, default)

    def get_saved_game(self, gid,):
        logger.info('returning saved game with gid %s' % gid)
        return self.db[gid]

    def delete_saved_game(self, gid,):
        g = gid.split('.')
        if len(g):
            g = g[0]
        if g in self.db:
            logger.info('deleting saved game with gid %s' % g)
            del self.db[g]
        else:
            logger.debug('could not find game with %s' % g)        

    def get_game_from_user(self, user, default=(None,'')):
        logger.info('returning gid for user %s' % user.name)
        res = default
        if hasattr(user, 'running_game'):
            res = self.active_games.get(user.running_game, default)
        return res

    def uid(self,):     # TODO: hier muss noch ein locking mechanismus rein
        gen = lambda: ''.join(('%f' % time()).split('.'))
        gid = gen()
        while gid in self.active_ids:
            logger.error('collision with %s' % gid)
            gid = gen()
        return gid

class Board:
    """The Board holds all information about position etc.. Special methods
check for valid moves etc.."""

    def __init__(self,):
        self.score_fmt = "board:%s:%s:%d:%d:%d:"
        self.position_fmt_4 = "%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:"
        self.position_fmt_3 = "%d:"*26
        self.dice_fmt = "%d:%d:%d:%d:%d:"
        self.cube_fmt = "%d:%d:%d:%d:"
        self.direction = {'p1':"1:-1:0:25:",
                          'p2':"-1:1:25:0:"}
        self.move_fmt = "%d:%d:%d:%d:%d:0:0:0"

    def set_score(self, p1, p2, ML):
        """('name_p1', score_p1), ('name_p2', score_p2), ML."""
        self._score_info = (p1, p2, ML)

    def _fmt_score(self, player, watcher=False):
        pn1 = self._score_info[0][0]
        pn2 = self._score_info[1][0]
        sc1 = self._score_info[0][1]
        sc2 = self._score_info[1][1]
        ML = self._score_info[2]
        logger.debug("_fmt_score with player '%s' and watcher '%s'" % (player, watcher))
        if watcher:
            if player == 'p1':
                return self.score_fmt % (pn1, pn2, ML, sc1, sc2)
            else:
                return self.score_fmt % (pn2, pn1, ML, sc2, sc1)
        else:
            if player == 'p1':
                return self.score_fmt % ('You', pn2, ML, sc1, sc2)
            else:
                return self.score_fmt % ('You', pn1, ML, sc2, sc1)

    def set_dice(self, turn, dice,):
        self._dice_info = (turn, dice)

    def _fmt_dice(self, player):
        turn, dice = self._dice_info
        if turn == 1:
            ret = {'p1':self.dice_fmt % ((1,) + dice + (0,0)),
                   'p2':self.dice_fmt % ((1,) + (0,0) + dice)}
        elif turn == 2:
            ret = {'p1':self.dice_fmt % ((-1,) + (0,0) + dice),
                   'p2':self.dice_fmt % ((-1,) + dice + (0,0))}
        else:
            ret = {'p1':self.dice_fmt % ((0,)*5)}
            ret['p2'] = ret['p1']
        return ret[player]

    def set_cube(self, cube, p1_allowed, p2_allowed, just_doubled, who=''):
        p1_wd, p2_wd = {'': (0,0), 'p1': (0,1), 'p2': (1,0)}[who]
        self._cube_info = {'p1': (cube, p1_allowed, p2_allowed, p1_wd),
                           'p2': (cube, p2_allowed, p1_allowed, p2_wd),}

    def _fmt_cube(self, player):
        return self.cube_fmt % self._cube_info[player]

    def set_move(self, p1, p2, pieces):
        """('home_p1', bar_p1), ('home_p2', bar_p2), pieces to move."""
        self._move_info = (p1, p2, pieces)

    def _fmt_move(self, player):
        hm1 = self._move_info[0][0]
        hm2 = self._move_info[1][0]
        br1 = self._move_info[0][1]
        br2 = self._move_info[1][1]
        pie = self._move_info[2]
        if player == 'p1':
            return self.move_fmt % (hm1, hm2, br1, br2, pie)
        else:
            return self.move_fmt % (hm2, hm1, br2, br1, pie)

    def set_position(self, position):
        self._position_info = position

    def _fmt_position(self,):
        if self.style == 4:
            position_fmt = self.position_fmt_4
        else:
            position_fmt = self.position_fmt_3
        return position_fmt % tuple(self._position_info)
        
    def check(self, player, move):
        msg = "can't move to Berlin"
        return msg

    def show_board(self, whom, style, watcher=False):
        if style in (1,2,3,4):
            self.style = style
            return {1: self.board_sl,
                    3: self.board_sl,
                    4: self.board_sl,
                    2: self.board_aa}[style](whom, watcher)

    def board_sl(self, whom, watcher=False):
        """Single line representation of the board."""
        score = self._fmt_score(whom, watcher)
        position = self._fmt_position()
        dice = self._fmt_dice(whom)
        cube = self._fmt_cube(whom)
        direction = self.direction[whom]
        move = self._fmt_move(whom)
        if self.style == 4:
            board = '%s | '*6 % (score, position, dice, cube, direction, move)
        else:
            board = score + position + dice + cube + direction + move
            #      0       5          31     36     40          44
        logger.info(board)
        return board

    def load(self, board):
        b = board.split(':')
        if b[0] == 'board':
            b = b[1:]
        if b[31] == b[40]:
            self.set_score((b[1],int(b[4])),(b[0],int(b[3])),int(b[2]))
            self._act_player = 'p2'
        else:
            self.set_score((b[0],int(b[3])),(b[1],int(b[4])),int(b[2]))
            self._act_player = 'p1'
        position = [int(p) for p in b[5:31]]
        self.set_position(position)
        turn = {'0':0, '1':1, '-1':2}[b[31]]
        if turn == 0:
            dice = (0,0)
        elif b[31] == b[40]:
            dice = (int(b[32]),int(b[33]))
        else:
            dice = (int(b[34]),int(b[35]))
        self.set_dice(turn, dice)
        self.set_move((int(b[44]),int(b[46])),(int(b[45]),int(b[47])),int(b[48]))

    def get_act_player(self,):
        return getattr(self, '_act_player', None)
    
    def board_aa(self, player, board=None, watcher=False):
        """Ascii art representation of the board."""
        skel = \
            ("  +13-14-15-16-17-18-------19-20-21-22-23-24-+ %c: %s - score: %d",
             "  | %s  %s  %s  %s  %s  %s |   |  %s  %s  %s  %s  %s  %s |",
             " v|                  |BAR|                   |    %d-point match",
             "  +12-11-10--9--8--7--------6--5--4--3--2--1-+ %c: %s - score: %d",
             "  BAR: O-%d X-%d   OFF: O-%d X-%d   Cube: %d  %s rolled %d %d.",
             )
        out = StringIO()
        score = self._score_info
        print >>out, 'announced player', player
        if player == 'p1':
            print >>out, skel[0] % ('X', score[1][0], score[1][1])
            for i in range(5):
                pos = []
                for p in self._position_info[13:25]:
                    if p > i:
                        pos.append('O')
                    elif p < -i:
                        pos.append('X')
                    else:
                        pos.append(' ')
                print >>out, skel[1] % tuple(pos)
            print >>out, skel[2] % score[2]
            for i in range(4,-1,-1):
                pos = []
                for p in self._position_info[1:13]:
                    if p > i:
                        pos.append('O')
                    elif p < -i:
                        pos.append('X')
                    else:
                        pos.append(' ')
                pos.reverse()
                print >>out, skel[1] % tuple(pos)
            print >>out, skel[3] % ('O', 'myself', score[0][1])
        else:
            print >>out, skel[3] % ('X', score[0][0], score[0][1])
            for i in range(5):
                pos = []
                for p in self._position_info[1:13]:
                    if p > i:
                        pos.append('O')
                    elif p < -i:
                        pos.append('X')
                    else:
                        pos.append(' ')
                pos.reverse()
                print >>out, skel[1] % tuple(pos)
            print >>out, skel[2] % score[2]
            for i in range(4,-1,-1):
                pos = []
                for p in self._position_info[13:25]:
                    if p > i:
                        pos.append('O')
                    elif p < -i:
                        pos.append('X')
                    else:
                        pos.append(' ')
                print >>out, skel[1] % tuple(pos)
            print >>out, skel[0] % ('O', 'myself', score[1][1])
        print >>out
        move = self._move_info
        dice = self._dice_info[1]
        onturn = {'p1': ('You',score[1][0])[self._dice_info[0]-1],
                  'p2': (score[0][0],'You')[self._dice_info[0]-1]}[player]
        print >>out, skel[4] % ((move[0][1],move[1][1],move[0][0],move[1][0],
                                0,onturn,) + dice),
##        print >>out, self._position_info
        return out.getvalue()

class Move:
    def __init__(self, move, control, player):
        self.moves = move
        self.control = control
        self.player = player    # TODO: player wird bisher nicht gebraucht

# TODO: eigene exceptions fangen fehler beim move ab
#       rollback in position ermöglichen

    def check(self,):
        logger.log(TRACE, 'checke eben noch nicht %s' % self)
        return True

    def render(self, value):
        z = value.split('-')
        if len(z) == 2:
            return z
        if z[0] == '':
            return ['0',z[2]]
        if z[1] == '':
            return [z[0],'0']

    def move(self,):
        # folgendes muss gehen:   parsing ['m', '1--3', '-3-off']
        # folgendes muss gehen:   parsing ['m', '24-28', '28-off']
        for m in self.moves:
            if m == 'zero':
                break           # TODO: vermutlich Altlast, kann weg
            z = self.render(m)
            logger.log(TRACE, 'in move mit %s aus %s' % (z, self.moves))
            if z[0] == 'bar':
                z0 = self.control.direction[self.player]['bar']
            else:
                z0 = min(int(z[0]), 25)
            if z[1] == 'off':
                z1 = self.control.direction[self.player]['home']
            else:
                z1 = min(int(z[1]), 25)
            z = (z0,z1)
            logger.debug('Move: moving %d to %d' % (z0,z1))
            yield z, m
##            self.control.move(z, self.player)
##        self.control.set_position()

    def __str__(self,):
        return ' '.join(self.moves)

class Waiter:
    """Waiter delays actions by a minimum amount of time.
    It grants the player a certain length of time to grasp the board,
    when otherwise automatic actions or bots react so quick, that details
    of the board could could be overlooked.

    Minimum lag is determined by an individual setting (set delay).

    The action is awaken by virtue of twisted.reactor.call_later().
    """

    def __init__(self, lag):
        self.load_action = self.delay_action
        self.action = self._idle
        self.player = None
        self.cmd = None
        self.params = None
        reactor.call_later(lag, self._wake())

    def _wake(self,):
        self.action(self.player, self.cmd, **self.params)

    def delay_action(self, action, player, cmd, params):
        self.player = player
        self.cmd = cmd
        self.params = params
        self.action = action

    def execute_action(self, action, player, cmd, params):
        action(player, cmd, **params)
        
    def _idle(self, player, cmd, **params):
        self.load_action = self.execute_action

class Player:
    """Player represents a player in a game/match. It supports the statemachine
    and the game control in communication with the players.

    name:       string, User.name, name of the player
    user:	User, the hosting player object
    opponent:   Player, the opponent player object
    color:      int, the color of the player as used in board (0, 1)
                color stays the same for each player throughout the game/match

    For convenience, Player offers the following attributes:

    opp_name:   string, User.name, name of the player
    opp_user:	User, the hosting player object
    """
    def __init__(self, user, opponent, color, owns_cube=False):
        self.user = user
        self.name = user.name
        self.color = color
        self.turn = color + 1
        self.owns_cube = owns_cube
        if not opponent is None:
            self.set_opponent(opponent)

    def set_opponent(self, opponent):
        self.opponent = opponent
        self.opp_user = opponent.user
        self.opp_name = opponent.user.name

    def chat_player(self, msg):
        self.user.chat(msg)

    def chat_player_watchers(self, msg):
        self.user.chat_watchers(msg)

    def chat_opponent(self, msg):
        self.opp_user.chat(msg)

    def chat_opponent_watchers(self, msg):
        self.opp_user.chat_watchers(msg)

    def board_player(self,):
        """Display the board for the player."""
        boardstyle = self.user.settings.get_boardstyle()
        self.chat_player(self.board.show_board(self.nick, boardstyle))
        self.board_watchers(self.user, self.nick)
        logger.info("sent board to player %s and watchers" % self.name)
        
    def board_opponent(self,):
        """Display the board for the players opponent."""
        boardstyle = self.opp_user.settings.get_boardstyle()
        opp_nick = {'p1':'p2', 'p2':'p1'}[self.nick]    # TODO: nick notlösung wegmachen
        self.chat_opponent(self.board.show_board(opp_nick, boardstyle))
        self.board_watchers(self.opp_user, opp_nick)
        logger.info("sent board to player %s and watchers" % self.opp_name)

    def board_watchers(self, player, nick):
        if len(player.watchers):
            boards = {}
            for w in player.watchers.values():
                brdstyle = w.settings.get_boardstyle()
                board = boards.get(brdstyle, None)
                if board is None:
                    board = self.board.show_board(nick, brdstyle, watcher=True)
                    boards[brdstyle] = board
                w.chat(board)

    def may_double(self,):
        wd = self.user.toggles.read('double')
        co = self.owns_cube
        oco = self.opponent.owns_cube
        md = wd and (co or not oco)
        logger.debug('player.may_double %s; reason toggle %d   owns %s' \
                                    '    opp owns %s' % (md, wd, co, oco))
        return md

    def crawford(self,):
        return self.user.toggles.read('crawford')

    def doubles(self,):
        logger.log(TRACE, 'player %s doubles' % self.name)
        self.owns_cube = False
        self.opponent.owns_cube = True

    def get_delay(self,):
        return self.user.settings.get_delay()

    def reset_toggles(self,):
        self.user.toggles.set_switch('double', True)
        self.user.toggles.set_switch('autoroll', False)
        self.user.toggles.set_switch('greedy', False)
        
class Status:
    def __init__(self,):
        self.cube = 1
        self.value = 1
        self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
##            self.position = [0, 0,0,0,1,4,5, 0,3,0,0,0,0,
##                                0,0,0,2,0,0, -7,-5,-3,0,0,0, 0]
##            self.position = [0, 0,0,0,3,5,7, 0,0,-2,0,0,0,
##                                0,0,0,0,-3,0, -5,-4,-1,0,0,0, 0]

    def pips(self,):    # ist nicht persistent, muss nicht ausgelagert werden
        pips1 = 0
        pips2 = 0
        for e,p in enumerate(self.position):
            if p > 0:
                pips1 += p*e
            elif p < 0:
                pips2 += p*(25-e)
        return (pips1, abs(pips2))

    def __str__(self,):
        out = StringIO()
        print >>out, self.cube, self.value, self.position,
        return out.getvalue()

    __repr__ = __str__
    
class Match:
    def __init__(self, ML, score,):
        self.score = score
        self.ML = ML
        self.crawford = False

    def __str__(self,):
        out = StringIO()
        print >>out, self.score, self.ML, self.crawford,
        return out.getvalue()

    __repr__ = __str__
    
from states import StateMachine
from states import GameStarted, TurnStarted, Doubled, Taken, Rolled, Moved
from states import GameFinished, Checked, TurnFinished, Resigned

class BGMachine(StateMachine):
    def __init__(self, caller):
        states = dict((('game_started', GameStarted()),     # A
                       ('turn_started', TurnStarted()),     # B
                       ('doubled', Doubled()),              # C
                       ('taken', Taken()),                  # D
                       ('rolled', Rolled()),                # H
                       ('checked', Checked()),              # E
                       ('moved', Moved()),                  # F
                       ('finished', GameFinished()),        # G
                       ('turn_finished', TurnFinished()),   # I
                       ('resigned', Resigned()),            # J
                       ))
        model = {
              # TODO: hier kurz mal sagen
             'game_started': (('start', states['rolled'], True, caller._start),
                              ('resume', None, True, caller._resume),),
             'turn_started': (('roll', states['rolled'], False, caller._roll),
                        ('double', states['doubled'], False, caller._double),),
             'doubled': (('accept', states['taken'], False, caller._take),
                        ('reject', states['finished'], False, caller._pass),),
             'taken': (('roll', states['rolled'], True, caller._roll),),
             'rolled': (('check', states['checked'], True, caller.check_roll),),
             'checked': (('move', states['moved'], False, caller._move),
                         ('cant_move', states['turn_finished'], True,
                                                          caller.nop),),
             'moved': (('turn', states['turn_finished'], True, caller.nop),
                       ('win', states['finished'], True, caller._win),),
             'finished': (('leave', None, True, caller.finish_game),),
             'turn_finished': (('hand_over', states['turn_started'], True,
                                                           caller.hand_over),),
             'resigned': (('accept', states['finished'], False,
                                                           caller._accepted),
                          ('reject', '', False, caller._rejected),),
                }
        # TODO: Parameter könnte man natürlich auch noch unterbringen
        for s in model:
            for k,x,y,z in model[s]:
                states[s].actions[k] = {'action': z, 'follow_up': x, 'auto': y}
        StateMachine.__init__(self, states)
        self.persistent = caller.save_state_to_status

class GameControl:
    """GameControl controls the process of playing a single game of BG."""
    def __init__(self, game, status, dice='random'):
        # TODO: das komplette init() muss entrümpelt werden.
        self.game = game
        self.status = status
    # PERSIST  position <- db
        self.board = Board()
        self.position = self.status.position
        self.set_position()
        self.p1 = self.set_player(game.player1, 'p1')
        self.p2 = self.set_player(game.player2, 'p2')
        self.players = {'p1':self.p1, 'p2':self.p2}
        self.dice = getDice(dice)
    # PERSIST  cube <- db
    # PERSIST  what about value??    (seems to be unneccessary)
        self.cube = self.status.cube
        just_doubled, who = getattr(self.status, 'doubles', (0,''))
        self.set_cube(just_doubled, who)
        self.turn = 0       # TODO oder was im board-status richtig ist
        self.home = {'p1':0, 'p2':0}
        self.bar = {'p1':0, 'p2':0}
        self.opp = {'p1':'p2', 'p2':'p1'} # TODO: weg damit
        self.direction = {'p1':{'home':0, 'bar':25}, 'p2':{'home':25, 'bar':0}}
        self.home_board = {'p1':(1,7), 'p2':(19,25)}  # TODO: gehört nach OX
            # TODO:  wenn es hier definiert ist, dann muss es von hier
            #        im board gesetzt werden.
        self.set_score()
#-------------------------------------------------------------------
        self.SM = BGMachine(self)
#-------------------------------------------------------------------

    def set_player(self, player, nick):
        p = player
        p.board = self.board    # needed for Player.board.... methods
        p.nick = nick           # TODO: muss bald weg, nur für den Übergang
        p.reset_toggles()
        p.owns_cube = False
        return p
        
    def start(self, resume):
        if resume:
            action = 'resume'
            self.status.resume = [s for s in self.status.state]
            print 'ANGERICHTET', self.status.resume
        else:
            action = 'start'
        self.SM.start(self.p1, action=action)
                # player neccessary (states.state_check), no matter which one

    def _start(self, p, **kw):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)   # communicate rolls to players
        self.dice_roll = d = (a,b)
        self.turn = {True:1, False:2}[a>b]
        self.pieces = 2             # TODO: hier gibt's doch keine pasch!!????
                                    #       {True:4, False:2}[d[0]==d[1]]
        self.set_dice(self.turn, d)
        logger.log(TRACE, 'in start  %s  %s  %s' % (self.turn, self.pieces,
                                                    self.board._dice_info))
        self.set_move()
        return {'roll': self.dice_roll, 'turn': self.whos_turn_p1(),
                'game_started': True}

    def _resume(self, p, **kw):
        state, player, params = self.status.resume
        del self.status.resume
        if player == self.p1.name:
            player = self.p1
        elif player == self.p2.name:
            player = self.p2
        else:
            logging.error('control._resume: Wrong player name!!!! %s not in ' \
                                        '(%s, %s)' % (name, p1.name, p2.name))
        logger.log(TRACE, 'in resume  %s  %s  %s' % (state, player.name, params))
        params['follow'] = self.SM.states[state]
        params['turn'] = player
        roll = params.get('roll', self.status.dice)
        self.turn = player.turn
        self.set_dice(self.turn, roll)
        self.pieces = self.status.pieces
        for p in ('p1', 'p2'):
            self.home[p], self.bar[p] = self.status.checkers[p]
        self.set_move()
        score = self.status.match.score
        msg = "turn: %s.\nmatch length: %d\npoints for %s: %d\npoints for " \
              "%s: %d" % (player.name, self.status.match.ML,
                          self.p1.name, score['p1'], self.p2.name, score['p2'])
        self.p1.chat_player(msg)
        self.p1.chat_opponent(msg)
        return params

    def whos_turn(self,):
        return {1:self.p1.user, 2:self.p2.user, 0:None}[self.turn]

    def whos_turn_p1(self,):
        # TODO   das hier muss dringend aufgeräumt werden (start-sequenz, self.start())
        return {1:self.p1, 2:self.p2, 0:None}[self.turn]

    def contact(self,):
        logger.log(TRACE, 'checking contact')
        if sum(self.bar.values()) > 0:
            logger.debug('contact because sum(self.bar.values()) = %d' % \
                        sum(self.bar.values()))
            return True
        x = False
        for p in self.position:
            if p < 0:
                x = True
            elif x and p > 0:
                logger.debug('contact because checker O on point %d' % p)
                return True
        logger.debug('no indication for contact')
        return False
        
    def check_roll(self, player, **kw):
        """Checks for possible moves depending on 'dice'."""
        dice = kw['roll']
        player_obj = player     # TODO: ogottogott
        player = player.nick    # TODO: prüfen, was man hier am besten nimmt,
                                #       um die Zuordnung zum Spieler zu kriegen
        logger.log(TRACE, 'check_roll %s fuer spieler %s' % (dice, player))
        ox = game_utilities.OX(self.direction[player]['bar'], self.home[player])
        # TODO: OX gehört in den Player
        bear_off = ox.bear_off(self.position[1:-1])
        if not self.contact():
            d1, d2 = dice
            if d1 == d2:
                self.pieces = 4
            else:
                self.pieces = 2
            ret = {'nr_pieces': self.pieces}
        else:
            ret = game_utilities.check_roll(dice, self.position,
                    self.bar[player], self.direction[player], ox)
            self.pieces = ret['nr_pieces']
        self.set_move()     # self.pieces wurde hier verändert, daher set_move()
        if bear_off and False: #player_obj.user.greedy_bearoff():
            ret.update(game_utilities.greedy(dice, self.position, ox))
        logger.debug('noch mal check_roll: %s   ' % ret)
        return ret
        
    def roll(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'roll')

    def _roll(self, player, **kw):
        d = self.dice.roll()    # TODO    turn und dice eintragen
        self.set_dice(self.turn, d)
        return {'roll': d}

    def double(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'double')

    def _double(self, player, **kw):
        self.cube = self.cube * 2
        player.doubles()
        # TODO: player.owns.cube setzen
        self.set_cube(1, player.nick)
        return {'value': self.cube}

    def _take(self, player):
        self.status.value = self.cube
        return {'value': self.cube}

    def _pass(self, player):
        return {'winner': player.opponent,
                'value': self.status.value,
                'reason': 'passed'}

    def _win(self, player, **kw):
        if 'value' in kw:
            value = kw['value']
        else:
            logger.debug('wins: %s    %s' % (player.name, self.position))
            loser = player.opponent.nick
            value = 1           # normal
            if self.home[loser] == 0:
                value = 2       # gammon
                a,b = self.home_board[player.nick]
                if sum(self.position[a:b]) != 0:
                    value = 3   # backgammon
        value = value * self.status.value
        return {'winner': player, 'value': value, 'reason': 'won'}

    def resign(self, player, value):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'resign', value=value)

    def finish_game(self, player, **kw):
        logger.info('%s in finish_game with %s' % (player.nick, kw))
        self.game.game_over(**kw)
        
    def nop(self, player):
        return {}       # TODO: sollte mittelfristig verschwinden

    def set_move(self,):
        """Sets certain groups of flags in the board."""
        p1 = (self.home['p1'], self.bar['p1'])
        p2 = (self.home['p2'], self.bar['p2'])
        self.status.pieces = self.pieces
        self.status.checkers = {'p1': p1, 'p2': p2}
        self.board.set_move(p1, p2, self.pieces)

    def set_position(self,):
        self.board.set_position(self.position)

    def set_dice(self, turn, dice):
        self.status.dice = dice
        self.board.set_dice(turn, dice)     # TODO: turn hier berechnen
                                            #       z.B. mit player.turn
                    #       player muss evtl. von der SM abgefragt werden

    def set_cube(self, just_doubled=0, who=''):
        p1 = self.p1.may_double()
        p2 = self.p2.may_double()
        self.status.doubles = (just_doubled, who)
        self.board.set_cube(self.cube, p1, p2, just_doubled, who)

    def set_score(self,):
        score = self.status.match.score
        self.board.set_score((self.p1.name, score['p1']),
                             (self.p2.name, score['p2']),
                              self.status.match.ML)

    def move(self, move, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'move', move=move)

    def _move(self, player, **kw):
        move = kw['move']
        mv = Move(kw['move'], self, player.nick)
        mv.check()
        result = []
        for m, label in mv.move():
            logger.info('%s changes the board' % (m,))
            logger.info('player %s   turn %s   whos_turn %s' % \
                        (player.nick, self.turn, self.whos_turn().name))
            if self.turn == 1:              # immer 'p1'  TODO: stimmt das?
                                            #               dann kann self.turn weg!
                                            # ES STIMMT WOHL
                self.position[m[0]] -= 1
                if m[0] == 25:
                    logger.info('bar  (player %s==p1)  %s' % (player.nick, self.bar))
                    self.bar['p1'] -= 1
                if m[1] == 0:                       # rauswürfeln
                    logger.info('off  (player %s==p1)  %s' % (player.nick, self.home))
                    self.home['p1'] += 1
                elif self.position[m[1]] == -1:     # werfen
                    self.position[m[1]] = 1
                    self.position[0] -= 1
                    logger.info('%s wirft %s' % (player.nick, self.opp[player.nick]))
                    self.bar[self.opp[player.nick]] += 1   # TODO: siehe oben;
                                                      #   hier könnte hart 'p2' hin
                                                      #   dann kann self.opp weg
                else:
                    self.position[m[1]] += 1
            elif self.turn == 2:
                self.position[m[0]] += 1
                if m[0] == 0:
                    logger.info('bar  (player %s==p2)  %s' % (player.nick, self.bar))
                    self.bar['p2'] -= 1
                if m[1] == 25:                       # rauswürfeln
                    logger.info('off  (player %s==p2)  %s' % (player.nick, self.home))
                    self.home['p2'] += 1
                elif self.position[m[1]] == 1:    # werfen
                    self.position[m[1]] = -1
                    self.position[25] += 1
                    logger.info('%s wirft %s' % (player.nick, self.opp[player.nick]))
                    self.bar[self.opp[player.nick]] += 1
                else:
                    self.position[m[1]] -= 1
            self.set_move()
            result.append(label)
        logger.info('player %s finished?  %s %s' % (player.nick,
                                    self.home[player.nick] >= 15, self.home))
        return {'moved': result, 'finished': self.home[player.nick] >= 15}

    def reject(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'reject')

    def _rejected(self, player, **kw):
        player.chat_player('You reject. The game continues.')
        msg = '%s rejects. The game continues.' % player.name
        player.chat_opponent(msg)
        player.chat_player_watchers(msg)
        player.chat_opponent_watchers(msg)
        player.board_player()
        return {'response': 'rejected'}

    def accept(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'accept')

    def _accepted(self, player, **kw):
        return {'response': 'accepted', 'winner': player, 'reason': 'resigned'}

    def hand_over(self, player, **kw):    # TODO: wird das noch gebraucht?
        self.turn = 3 - self.turn         #   JA, solange turn gebraucht wird
        self.set_dice(self.turn, (0,0))
        logger.log(TRACE, 'in handover:  -> %d' % self.turn)
        return {'may_double': self.may_double(player.opponent)}

    def may_double(self, player):
        match = self.status.match
        pmd = player.may_double()
        md = (match.ML > 1) and (not match.crawford) and pmd
        logger.debug('may_double %s; reason ML %d   CR %s   PMD %s' % \
                     (md, match.ML, match.crawford, pmd))
        return md

    def save_state_to_status(self, state, player, params):
        if state in ('turn_started', 'doubled', 'checked', 'resigned'):
            # TODO: fehlt G wegen dem join (das fehlt auch im Bild von der SM)
            mparams = params
            if 'active_state' in params:
                mparams = params.copy()
                del mparams['active_state']  # TODO: muss sauber gepickelt werden
            self.status.state = (state, player.name, mparams)
            self.game.save('control.save_state_to_status')
            
class Game(Persistent):
    def __init__(self, gid, p1, p2, ML, status, dice='random'):
        """Represents a game of Backgammon.
    gid:        unique Id
    p1:         player 1, host, white, O (class User)
    p2:         player 2, guest, black, X (class User)
    ML:         match length (string, must be convertible to int)
    board:      persistency hook
    dice:       choice of dice (random, sequence, ...)
"""
        self.id = gid
        self.player1 = Player(p1, None, 0)
        self.player2 = Player(p2, self.player1, 1)
        self.player1.set_opponent(self.player2)
        self.ids = ['.'.join((self.id, 'p1')), '.'.join((self.id, 'p2'))]
                                        # TODO: variante watchers  <id>.wn.px
        self.player = dict(zip(self.ids,('p1','p2')))
        self.who = dict(zip(('p1', 'p2'),(self.player1, self.player2)))
        self.opp = {p1.name:p2, p2.name:p1}     # TODO: mittelfristig weg
        self.dice = dice                    # TODO: braucht der die permanent??
        if status is None:  # TODO: status könnte auch in getGame gebaut werden
                            #       (wie newUser)
            status = Status()
            status.match = Match(int(ML),{'p1': 0, 'p2': 0})
        logger.debug('GAME with p1 %s p2 %s   status %s match %s' % \
                         (p1.name, p2.name, status, status.match))
        self.control = GameControl(self, status, dice=self.dice)
        logger.info('New game with id %s, %s vs %s' % (self.id, p1.name, p2.name))
        Persistent.__init__(self, DB_Games, 'games')
        self.db_key = self.id
        self.db_load = self.control.status
        self.save('game.__init__')     # TODO: an dieser Stelle vermutlich überflüssig

    def start(self, resume):
        self.control.start(resume)

    def continue_game(self,):
        del self.player1.user.ready_to_continue
        del self.player2.user.ready_to_continue
        new_status = Status()
        self.db_load = new_status
        new_status.match = self.control.status.match
        self.control = GameControl(self, new_status, dice=self.dice)
        logger.info('Next game in match %s vs %s' % (self.player1.name,
                                            self.player2.name))
        self.start(False)

    def stop(self, save=True):
        if save:
            self.save('game.stop')
        else:
            self.delete()
        ms = self.control.status.match.score
        score = ms['p1'], ms['p2']
        self.player1.user.teardown_game(score, save)
        score = ms['p2'], ms['p1']
        self.player2.user.teardown_game(score, save)
        self.teardown(self)

    def game_over(self, **kw):
        winner = kw['winner'].nick
        value = kw['value']
        # TODO: woher kommt der value?
        #       und was haeltst du vom cube??????
        match = self.control.status.match
        match.score[winner] += value
        winners_score = match.score[winner]
        losers_score = match.score[kw['winner'].opponent.nick]
        winner_name = kw['winner'].name
        loser_name = kw['winner'].opp_name
        logger.info('winner %s in game_over. value: %d. score %s' % \
                    (winner_name, value, match.score))
        if winners_score < match.ML:    # match continues
            msg = 'score in %d point match: %s-%d %s-%d' % \
                                  (match.ML, winner_name, winners_score,
                                                   loser_name, losers_score)
            kw['winner'].chat_player(msg)
            kw['winner'].chat_opponent(msg)
            kw['winner'].chat_player_watchers(msg)
            kw['winner'].chat_opponent_watchers(msg)
            match.crawford = ((match.ML - winners_score) == 1) and \
                        (self.player1.crawford() and self.player2.crawford())
                        # TODO: bei player.crawford() wär ein OR angebracht?
            msg = "Type 'join' if you want to play the next game, type " \
                                                      "'leave' if you don't."
            kw['winner'].chat_player(msg)
            kw['winner'].chat_opponent(msg)
        else:                           # match is over
            score = '%d-%d .' % (winners_score, losers_score)
            ML = match.ML
            msg = 'You win the %d point match %s' % (ML, score)
            kw['winner'].chat_player(msg)
            msg = '%s wins the %d point match %s' % (winner_name, ML, score)
            kw['winner'].chat_opponent(msg)
            kw['winner'].chat_player_watchers(msg)
            kw['winner'].chat_opponent_watchers(msg)
            self.book_game(kw['winner'])
            self.stop(save=False)

    def weighed_experience(self, user, ML):
        exp = user.experience() + ML 
        if exp < 400:               # TODO:  bitte dringend noch mal überprüfen
            return 4. * max(1, 5. - exp/100.)
        return 4.

    def book_game(self, winner):
        loser = winner.opponent
        ML = self.control.status.match.ML
        Pw = winner.user.rating()
        Ew = self.weighed_experience(winner.user, ML)
        Pl = loser.user.rating()
        El = self.weighed_experience(loser.user, ML)
        logger.debug('winner:  %f %d    loser:  %f %d' % (Pw,
                        winner.user.experience(), Pl, loser.user.experience()))
        D = abs(Pw - Pl)
        n = sqrt(ML)            # TODO: die eigentliche Berechnung rauslösen
        d = D*n/2000.           #       und durch unittests absichern
        U = 1./(10.**d + 1.)
        F = 1. - U
        if Pw > Pl:
            nU = n * U
            Rw =   Ew * nU
            Rl = - El * nU
        else:
            nU = n * F
            Rw =   Ew * nU
            Rl = - El * nU
        logger.info('booking the game for %s' % winner.name)
        logger.debug('winner: rating %f' % Rw)
        logger.debug('loser:  rating %f' % Rl)
        winner.user.advance_rating(Rw, ML)
        loser.user.advance_rating(Rl, ML)

    def starting_rolls(self, p1, p2):   # TODO: gehoert hoch ins control
                                        #       oder? kommunikation??
        line = '%%s rolled %s, %s rolled %s'
        msg = line % (p1, self.player2.name, p2)
        self.player1.user.chat(msg % 'You')
        self.player1.user.chat_watchers(msg % self.player1.name)
        msg = line % (p2, self.player1.name, p1)
        self.player2.user.chat(msg % 'You')
        self.player2.user.chat_watchers(msg % self.player2.name)

    def roll(self, player):
        self.control.roll(player)

    def move(self, move, player):
        self.control.move(move, player)

    def double(self, player):
        self.control.double(player)

    def accept(self, player,):
        self.control.accept(player)

    def reject(self, player,):
        self.control.reject(player)

    def resign(self, player, value):
        self.control.resign(player, value)

    def whos_turn(self,):   # TODO: kann mittelfristig sicher weg; das macht SM
        msg = 'It is your turn to move'
        self.control.whos_turn().chat(msg)

    def players(self, player):  # TODO: soll mittelfristig weg
        """Matches 'pn' and the according Player object."""
        return self.who[player]

    def pips(self, player):
        pips = self.control.status.pips()
        opp_name = self.players(player).opp_name
        s = {
            'p1': {'you':pips[0], 'other':pips[1], 'opp': opp_name},
            'p2': {'you':pips[1], 'other':pips[0], 'opp': opp_name},
            }
        return 'Pipcounts: You %(you)d   %(opp)s %(other)d' % s[player]

    def show_game(self,):
        p1 = self.player1
        p2 = self.player2
        m = self.control.status.match
        return '%-15s - %15s (%s point match %d-%d)' % (p1.name, p2.name, m.ML,
                                        m.score[p1.nick], m.score[p2.nick])
        
def getGame(**kw):
    log = kw['list_of_games']
    p1 = kw['player1']          # TODO: why do I resolve the dict kw????
    p2 = kw['player2']          #       why not just call Game(gid, **kw)
    ML = kw['ML']
    if ML is None:
        gid = kw['gid']
        status = log.get_saved_game(gid)
        resume = True
    else:
        gid = log.uid()
        status = None
        resume = False
    game = Game(gid, p1, p2, ML, status, dice=kw['dice'])
    game.teardown = log.remove
    log.add(game)
    game.start(resume)
    return game.ids
