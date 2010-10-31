#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

REV = '$Revision$'

from StringIO import StringIO
from time import time
from dice import getDice
import logging
from persistency import Persistent, Db
from version import Version

v = Version()
v.register(__name__, REV)

DB_Games = 'db/games'

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.INFO,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('game')

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
            self.db = saved_games = Db(DB_Games, 'games').db
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

    def get(self, gid, default=(None,'')):
        logger.log(TRACE, 'returning gid %s' % gid)
        return self.active_games.get(gid, default)

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
        self.dice_fmt = "%d:"*5
        self.cube = "1:1:1:0:"
        self.direction = {'p1':"1:-1:0:25:",
                          'p2':"-1:1:25:0:"}
        self.move_fmt = "%d:%d:%d:%d:%d:0:0:0"

    def set_score(self, p1, p2, ML):
        """('name_p1', score_p1), ('name_p2', score_p2), ML."""
        self._score_info = (p1, p2, ML)

    def _fmt_score(self, player):
        pn1 = self._score_info[0][0]
        pn2 = self._score_info[1][0]
        sc1 = self._score_info[0][1]
        sc2 = self._score_info[1][1]
        ML = self._score_info[2]
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
            ret = {'p1':self.dice_fmt % (0,)*5,}
            ret['p2'] = ret['p1']
        return ret[player]

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

    def show_board(self, whom, style):
        if style in (1,2,3,4):
            self.style = style
##            print self.board_sl(whom)
            return {1: self.board_sl,
                    3: self.board_sl,
                    4: self.board_sl,
                    2: self.board_aa}[style](whom)

    def board_sl(self, whom):
        """Single line representation of the board."""
        score = self._fmt_score(whom)
        position = self._fmt_position()
        dice = self._fmt_dice(whom)
        cube = self.cube
        direction = self.direction[whom]
        move = self._fmt_move(whom)
        if self.style == 4:
            return '%s | '*6 % (score, position, dice, cube, direction, move)
        else:
            return score + position + dice + cube + direction + move
            #      0       5          31     36     41          45

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
    
    def board_aa(self, player, board=None):
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
        self.player = player

# TODO: eigene exceptions fangen fehler beim move ab
#       rollback in position ermöglichen

    def check(self,):
        logger.log(TRACE, 'checke eben noch nicht %s' % self)
        return True

    def move(self,):
        for m in self.moves:
            if m == 'zero':
                break           # TODO: vermutlich Altlast, kann weg
            z = m.split('-')
            if z[0] == 'bar':
                z0 = self.control.direction[self.player]['bar']
            else:
                z0 = int(z[0])
            if z[1] == 'off':
                z1 = self.control.direction[self.player]['home']
            else:
                z1 = int(z[1])
            z = (z0,z1)
            logger.info('Move: moving %d to %d' % (z0,z1))
            yield z, m
##            self.control.move(z, self.player)
##        self.control.set_position()

    def __str__(self,):
        return ' '.join(self.moves)

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
    def __init__(self, user, opponent, color):
        self.user = user
        self.name = user.name
        self.color = color
        if not opponent is None:
            self.set_opponent(opponent)

    def set_opponent(self, opponent):
        self.opponent = opponent
        self.opp_user = opponent.user
        self.opp_name = opponent.user.name

    def chat_player(self, msg):
        self.user.chat(msg)

    def chat_opponent(self, msg):
        self.opp_user.chat(msg)

    def board_player(self,):
        """Display the board for the player."""
        boardstyle = self.user.settings.get_boardstyle()
        self.chat_player(self.board.show_board(self.nick, boardstyle))
        
    def board_opponent(self,):
        """Display the board for the players opponent."""
        boardstyle = self.opp_user.settings.get_boardstyle()
        opp_nick = {'p1':'p2', 'p2':'p1'}[self.nick]    # TODO: nick notlösung wegmachen
        self.chat_opponent(self.board.show_board(opp_nick, boardstyle))

    def may_double(self,):
        return self.user.toggles.read('double')
        
class Status:       # TODO: muss noch eingebunden werden
    def __init__(self, position, dice, cube, direction, move):
        self.position = position
        self.dice = dice
        self.cube = cube
        self.direction = direction
        self.move = move

    def pips(self,):    # TODO: auslagern, wegen Persistenz
        pips1 = 0
        pips2 = 0
        for e,p in enumerate(self.position):
            if p > 0:
                pips1 += p*e
            elif p < 0:
                pips2 += p*(25-e)
        return (pips1, abs(pips2))
    
class Match:
    def __init__(self, ML, score,):
        self.score = score
        self.ML = ML

    def crawford(self,):    # TODO: auslagern, wegen Persistenz
        return False

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
             'game_started': (('start', states['rolled'], True, caller._start),),
             'turn_started': (('roll', states['rolled'], False, caller._roll),
                        ('double', states['doubled'], False, caller.double),),
             'doubled': (('take', states['taken'], False, caller.take),
                        ('pass', states['finished'], False, caller.drop),),
             'taken': (('roll', states['rolled'], True, caller._roll),),
             'rolled': (('check', states['checked'], True, caller.check_roll),),
             'checked': (('move', states['moved'], False, caller._move),
                        ('cant_move', states['turn_finished'], True, caller.nop),),
             'moved': (('turn', states['turn_finished'], True, caller.nop),
                       ('win', states['finished'], True, caller.nop),),
             'finished': (('leave', None, True, caller.finish_game),),
             'turn_finished': (('hand_over', states['turn_started'], True,
                                                           caller.hand_over),),
             'resigned': (('accept', states['finished'], False,
                                                           caller._accepted),
                          ('reject', None, False, caller._rejected),),
                }
        # TODO: Parameter könnte man natürlich auch noch unterbringen
        for s in model:
            for k,x,y,z in model[s]:
                states[s].actions[k] = {'action': z, 'follow_up': x, 'auto': y}
        StateMachine.__init__(self, states)
        self.persistent = caller.save_state_to_status

class GameControl:
    """GameControl controls the process of playing a single game of BG."""
    def __init__(self, game, board=None, dice='random'):
        # TODO: das komplette init() muss entrümpelt werden.
        self.game = game
        if not board is None:
            self.board = board
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
                # TODO:  position muss vom Board abgekupfert werden.
        else:
            self.board = Board()
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
            self.set_position()
        self.p1 = game.player1
        self.p1.board = self.board
        self.p1.nick = 'p1'     # TODO: muss bald weg, nur für den Übergang
        self.p2 = game.player2
        self.p2.board = self.board
        self.p2.nick = 'p2'     # TODO: muss bald weg, nur für den Übergang
        self.players = {'p1':self.p1, 'p2':self.p2}
        self.dice = getDice(dice)
        self.cube = 1
        self.turn = 0       # TODO oder was im board-status richtig ist
        self.home = {'p1':0, 'p2':0}
        self.bar = {'p1':0, 'p2':0}
        self.opp = {'p1':'p2', 'p2':'p1'} # TODO: weg damit
        self.direction = {'p1':{'home':0, 'bar':25}, 'p2':{'home':25, 'bar':0}}
            # TODO:  wenn es hier definiert ist, dann muss es von hier
            #        im board gesetzt werden.
        self.score = {'p1':0, 'p2':0}   # TODO: aus dem Match holen
        self.status = Status(self.position, self.dice, self.cube, self.direction, 0)
        self.board.set_score((self.p1.name, self.score['p1']),
                             (self.p2.name, self.score['p2']),
                              self.game.match.ML)
#-------------------------------------------------------------------
        self.SM = BGMachine(self)
#-------------------------------------------------------------------

    def start(self,):
        self.SM.start(self.p1)  # TODO: player is not relevant; can we drop it?

    def _start(self, p, **kw):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)
        self.dice_roll = d = (a,b)
        self.turn = {True:1, False:2}[a>b]
        self.pieces = {True:4, False:2}[d[0]==d[1]]
        self.board.set_dice(self.turn, d)
        logger.log(TRACE, 'in start  %s  %s  %s' % (self.turn, self.pieces,
                                                    self.board._dice_info))
        self.set_move()
        return {'roll': self.dice_roll, 'turn': self.whos_turn_p1()}

    def whos_turn(self,):
        return {1:self.p1.user, 2:self.p2.user, 0:None}[self.turn]

    def whos_turn_p1(self,):
        # TODO   das hier muss dringend aufgeräumt werden (start-sequenz, self.start())
        return {1:self.p1, 2:self.p2, 0:None}[self.turn]

    def check_roll(self, player, **kw):
        """Checks for possible moves depending on 'dice'."""
        dice = kw['roll']
        player = player.nick    # TODO: prüfen, was man hier am besten nimmt,
                                #       um die Zuordnung zum Spieler zu kriegen
        logger.info('check_roll %s fuer spieler %s' % (dice, player))
        exhausted = False
        list_of_moves = []  # TODO: lieber dict?
        pos = self.position
        d1, d2 = dice
        my_dice = list(dice[:])
        nr_of_moves = {True:4, False:2}[d1 == d2]
        # -------------------------------------------enter from the bar
        bar_moves = min(nr_of_moves, self.bar[player])
        bar = self.direction[player]['bar']
        if bar_moves:
            logger.info('der spieler %s hat %d moves von der bar (%d)' % \
                        (player, bar_moves, bar))
            for d in dice:
                if bar == 25:
                    p = bar - d
                    if pos[p] > -2:
                        if nr_of_moves == 2:
                            list_of_moves.append('bar-%d' % p)
                            my_dice.remove(d)
                            bar_moves -=1
                        else:
                            list_of_moves = ['bar-%d' % p,]*bar_moves
                            my_dice = [my_dice[0],]*(4-bar_moves)
                            bar_moves = 0
                            logger.info('pasch getested: bar %d  wurf %d   point %d   ' \
                                 'checker %d  (%s) (%s) (%d)' % \
                                 (bar,d,p,pos[p],list_of_moves,my_dice,bar_moves))
                            break
                if bar == 0:
                    p = bar + d
                    if pos[p] < 2:
                        if nr_of_moves == 2:
                            list_of_moves.append('bar-%d' % p)
                            my_dice.remove(d)
                            bar_moves -=1
                        else:
                            list_of_moves = ['bar-%d' % p,]*bar_moves
                            my_dice = [my_dice[0],]*(4-bar_moves)
                            bar_moves = 0
                            logger.info('pasch getested: bar %d  wurf %d   point %d   ' \
                                 'checker %d  (%s) (%s) (%d)' % \
                                 (bar,d,p,pos[p],list_of_moves,my_dice,bar_moves))
                            break
                logger.info('hab getested: bar %d  wurf %d   point %d   ' \
                     'checker %d  (%s)' % (bar,d,p,pos[p],list_of_moves))
        if len(list_of_moves) < bar_moves:
            nr_of_moves = len(list_of_moves)
            exhausted = True
        if exhausted:
            logger.info('spieler %s kann nur %d zuege ziehen' % (player, nr_of_moves))
        self.pieces = nr_of_moves
        self.set_move()
        return {'nr_pieces': nr_of_moves, 'list_of_moves': list_of_moves}
        
    def roll(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'roll')

    def _roll(self, player, **kw):
        d = self.dice.roll()    # TODO    turn und dice eintragen
        self.board.set_dice(self.turn, d)
        return {'roll': d}

    def double(self, player):
        return {}

    def take(self, player):
        return {}

    def drop(self, player):
        return {}

    def resign(self, player, value):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'resign', value=value)

    def finish_game(self, player, **kw):
        out = {}
        # wer hat gewonnen?
        out['winner'] = 'p1'
        # value bestimmen
        out['value'] = 1
        #    position (gammon?)
        # cube? multiply
        # match up one notch
        logger.info('%s in finish_game with %s' % (player.nick, kw))
        self.game.game_over(**out)
        return {}
        
    def nop(self, player):
        return {}

    def set_move(self,):
        """Sets certain groups of flags in the board."""
        p1 = (self.home['p1'], self.bar['p1'])
        p2 = (self.home['p2'], self.bar['p2'])
##        print 'SET_MOVE',p1,p2,self.pieces
        self.board.set_move(p1, p2, self.pieces)

    def set_position(self,):
        self.board.set_position(self.position)

    def move(self, move, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'move', move=move)
        
    def _move(self, player, **kw):
        # TODO: kontrollieren, ob der dran ist
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
        return {'moved': result, 'finished': self.home[player.nick] == 15}

    def reject(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'reject')

    def _rejected(self, player, **kw):
        return {'response': 'rejected'}

    def accept(self, player):
        p = self.players[player]    # TODO: hier aufräumen
        self.SM.action(p, 'accept')

    def _accepted(self, player, **kw):
        return {'response': 'accepted'}

    def hand_over(self, player, **kw):    # TODO: wird das noch gebraucht?
        self.turn = 3 - self.turn
        self.board.set_dice(self.turn, (0,0))
##        logger.log(TRACE, 'in handover:  -> %d' % self.turn)
        return {'may_double': self.may_double(player)}

    def may_double(self, player):
        match = self.status.match
        return (match.ML > 1) and (not match.crawford()) \
               and (player.may_double())   # TODO:  and Cube Besitz

    def save_state_to_status(self, name, player, kw):
        self.status.state_name = name
        # TODO: fertigstellen
            
class Game(Persistent):
    # players watchers
    def __init__(self, gid, p1, p2, ML, board=None, dice='random'):
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
                                            # TODO: hier kommen noch watchers
                                            #       <id>.wn.px
        self.player = dict(zip(self.ids,('p1','p2')))
        self.who = dict(zip(('p1', 'p2'),(self.player1, self.player2)))
        self.opp = {p1.name:p2, p2.name:p1}     # TODO: mittelfristig weg
        self.dice = dice
        self.match = Match(int(ML),{'p1': 0, 'p2': 0})
        self.control = GameControl(self, board=board, dice=self.dice)
        logger.info('New game with id %s, %s vs %s' % (self.id, p1.name, p2.name))
        self.control.status.match = self.match
        Persistent.__init__(self, DB_Games, 'games')
        self.db_key = self.id
        self.db_load = self.control.status
        self.save()

    def start(self,):
        msg = 'Starting a new game with %s'
        self.player1.user.chat(msg % self.player2.name)
        self.player2.user.chat(msg % self.player1.name)
        self.control.start()

    def stop(self,):
        self.player1.user.teardown_game()
        self.player2.user.teardown_game()
        self.teardown(self)

    def game_over(self, **kw):
        self.match.score[kw['winner']] += kw['value']
        self.control = GameControl(self, dice=self.dice)
        self.start() #TODO: falls es stimmt

    def starting_rolls(self, p1, p2):   # TODO: gehoert hoch ins control
        msg = 'You rolled %s, %s rolled %s'
        self.player1.user.chat(msg % (p1, self.player2.name, p2))
        self.player2.user.chat(msg % (p2, self.player1.name, p1))

    def roll(self, player):
        self.control.roll(player)

    def move(self, move, player):
        self.control.move(move, player)

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
        
def getGame(**kw):
    log = kw['list_of_games']
    gid = log.uid()
    game = Game(gid, kw['player1'], kw['player2'], kw['ML'], dice=kw['dice'])
    game.teardown = log.remove
    log.add(game)
    game.start()
    return game.ids
