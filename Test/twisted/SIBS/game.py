#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

from StringIO import StringIO
from time import time
from dice import getDice

VERBOSE = True

def talk(msg):
    if VERBOSE:
        print msg
        
class GamesList:        # TODO: mit UsersList in eine Klasse überführen

    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/
                        # TODO: kann man das Borg Pattern ableitbar machen?
                        
    def __init__(self,):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'active_games'):
            self.active_games = {}
            self.active_ids = {}

    def add(self, game):
        for i in game.ids:
            self.active_games[i] = (game, game.player[i])
        self.active_ids[game.id] = game.id
        # TODO: denk dran, beim Ende des Spiels aufzuräumen

    def get(self, gid, default=None):
        #talk('returning gid %s' % gid)
        return self.active_games.get(gid, default)

    def uid(self,):     # TODO: hier muss noch ein locking mechanismus rein
        gen = lambda: ''.join(('%f' % time()).split('.'))
        gid = gen()
        while self.active_ids.has_key(gid):
            talk('collision with %s' % gid)
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
        talk('checke eben noch nicht %s' % self)
        return True

    def move(self,):
        for m in self.moves:
            if m == 'zero':
                break
            z = m.split('-')
            if z[0] == 'bar':
                z0 = self.control.direction[self.player]['bar']
            else:
                z0 = int(z[0])
            z1 = int(z[1])
            z = (z0,z1)
            talk('Move: moving %d to %d' % (z0,z1))
            self.control.move(z, self.player)
        self.control.set_position()
        talk('in Move.move as %s' % self.player)
        self.control.hand_over()

    def __str__(self,):
        return ' '.join(self.moves)

class Player:
    def __init__(self, name, user, opponent, color):
        self.name = name
        self.user = user
        self.opponent = opponent
        self.color = color

class Status:
    def __init__(self, position, dice, cube, direction, move):
        self.position = position
        self.dice = dice
        self.cube = cube
        self.direction = direction
        self.move = move
    
class Match:
    def __init__(self, score, cube,):
        self.score = score
        self.cube = cube

from states import StateMachine
from states import GameStarted, TurnStarted, Doubled, Taken, Rolled, Moved
from states import GameFinished

class BGMachine(StateMachine):
    def __init__(self, caller):
        states = dict((('game_started', GameStarted()),
                       ('turn_started', TurnStarted()),
                       ('doubled', Doubled()),
                       ('taken', Taken()),
                       ('rolled', Rolled()),
                       ('moved', Moved()),
                       ('finished', GameFinished()),
                       ))
        model = \
            {'game_started': (('start', states['rolled'], True, caller.start),),
             'turn_started': (('roll', states['rolled'], False, caller.roll),
                        ('double', states['doubled'], False, caller.double),),
             'doubled': (('take', states['taken'], False, caller.take),
                        ('pass', states['finished'], False, caller.drop),),
             'taken': (('roll', states['rolled'], True, caller.roll),),
             'rolled': (('move', states['moved'], False, caller.move),
                        ('cant_move', states['turn_started'], True, caller.nop),),
             'moved': (('turn', states['taken'], False, caller.hand_over),
                       ('win', states['finished'], True, caller.nop),),
                }
        # TODO: Parameter könnte man natürlich auch noch unterbringen
        for s in model:
            for k,x,y,z in model[s]:
                states[s].actions[k] = {'action': z, 'follow_up': x, 'auto': y}
        StateMachine.__init__(self, states)

class GameControl:
    """GameControl controls the process of playing a single game of BG."""
    def __init__(self, game, board=None, dice='random'):
        self.game = game
        self.p1 = game.player1
        self.p2 = game.player2
        self.dice = getDice(dice)
        self.cube = 1
        self.turn = 0       # TODO oder was im board-status richtig ist
        self.home = {'p1':0, 'p2':0}
        self.bar = {'p1':0, 'p2':0}
        self.opp = {'p1':'p2', 'p2':'p1'}
        self.direction = {'p1':{'home':0, 'bar':25}, 'p2':{'home':25, 'bar':0}}
            # TODO:  wenn es hier definiert ist, dann muss es von hier
            #        im board gesetzt werden.
        self.score = {'p1':0, 'p2':0}
        if not board is None:
            self.board = board
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
                # TODO:  position muss vom Board abgekupfert werden.
        else:
            self.board = Board()
            self.board.set_score((self.p1.name, self.score['p1']),
                                 (self.p2.name, self.score['p2']),
                                  self.game.ML)
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
            self.set_position()
#-------------------------------------------------------------------
        self.SM = BGMachine(self)
#-------------------------------------------------------------------

    def start(self,):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)
        self.dice_roll = d = (a,b)
        self.turn = {True:1, False:2}[a>b]
        self.pieces = {True:4, False:2}[d[0]==d[1]]
        self.board.set_dice(self.turn, d)
        talk('in start  %s  %s  %s' % (self.turn, self.pieces,
                                       self.board._dice_info))
        self.set_move()

    def whos_turn(self,):
        return {1:self.p1.user, 2:self.p2.user, 0:None}[self.turn]

    def check_roll(self, dice, player):
        """Checks for possible moves depending on 'dice'."""
        talk('check_roll %s fuer spieler %s' % (dice, player))
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
            talk('der spieler %s hat %d moves von der bar (%d)' % \
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
                            talk('pasch getested: bar %d  wurf %d   point %d   ' \
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
                            talk('pasch getested: bar %d  wurf %d   point %d   ' \
                                 'checker %d  (%s) (%s) (%d)' % \
                                 (bar,d,p,pos[p],list_of_moves,my_dice,bar_moves))
                            break
                talk('hab getested: bar %d  wurf %d   point %d   ' \
                     'checker %d  (%s)' % (bar,d,p,pos[p],list_of_moves))
        if len(list_of_moves) < bar_moves:
            nr_of_moves = len(list_of_moves)
            exhausted = True
        if exhausted:
            talk('spieler %s kann nur %d zuege ziehen' % (player, nr_of_moves))
        return (nr_of_moves, list_of_moves)
        
    def roll(self, player):
        # TODO: kontrollieren, ob der dran ist
        talk('der spieler %s hat die wuerfel' % (player,))
        d = self.dice.roll()    # TODO    turn und dice eintragen
        self.dice_roll = d
        self.possible_moves = self.check_roll(d, player)
        self.pieces = self.possible_moves[0]
        self.board.set_dice(self.turn, d)
        self.set_move()
        return d

    def double(self, player):
        pass

    def take(self, player):
        pass

    def drop(self, player):
        pass

    def nop(self, player):
        pass

    def set_move(self,):
        """Sets certain groups of flags in the board."""
        p1 = (self.home['p1'], self.bar['p1'])
        p2 = (self.home['p2'], self.bar['p2'])
        self.board.set_move(p1, p2, self.pieces)

    def set_position(self,):
        self.board.set_position(self.position)
        
    def move(self, move, player):
        # TODO: kontrollieren, ob der dran ist
        talk('%s changes the board' % (move,))
        talk('player %s   turn %s   whos_turn %s' % \
                    (player, self.turn, self.whos_turn().name))
        if self.turn == 1:              # immer 'p1'  TODO: stimmt das?
                                        #               dann kann self.turn weg!
            self.position[move[0]] -= 1
            if move[0] == 25:
                talk('bar  (player %s==p1)  %s' % (player, self.bar))
                self.bar['p1'] -= 1
            if self.position[move[1]] == -1:    # werfen
                self.position[move[1]] = 1
                self.position[0] -= 1
                talk('%s wirft %s' % (player, self.opp[player]))
                self.bar[self.opp[player]] += 1   # TODO: siehe oben;
                                                  #   hier könnte hart 'p2' hin
                                                  #   dann kann self.opp weg
            else:
                self.position[move[1]] += 1
        elif self.turn == 2:
            self.position[move[0]] += 1
            if move[0] == 0:
                talk('bar  (player %s==p2)  %s' % (player, self.bar))
                self.bar['p2'] -= 1
            if self.position[move[1]] == 1:    # werfen
                self.position[move[1]] = -1
                self.position[25] += 1
                talk('%s wirft %s' % (player, self.opp[player]))
                self.bar[self.opp[player]] += 1
            else:
                self.position[move[1]] -= 1
        self.set_move()

    def hand_over(self,):
        self.turn = 3 - self.turn
        self.board.set_dice(self.turn, (0,0))
        talk('in handover:  -> %d' % self.turn)

class Game:
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
        self.player1 = Player(p1.name, p1, p2, 0)
        self.player2 = Player(p2.name, p2, p1, 1)
        self.ids = ['.'.join((self.id, 'p1')), '.'.join((self.id, 'p2'))]
                                            # TODO: hier kommen noch watchers
        self.player = dict(zip(self.ids,('p1','p2')))
        self.who = dict(zip(('p1', 'p2'),(p1, p2)))
        self.ML = int(ML)
        self.opp = {p1.name:p2, p2.name:p1}
        self.control = GameControl(self, board=board, dice=dice)
        talk('New game with id %s, %s vs %s' % (self.id, p1.name, p2.name))

    def start(self,):
        msg = 'Starting a new game with %s'
        self.player1.user.chat(msg % self.player2.name)
        self.player2.user.chat(msg % self.player1.name)
        self.control.start()
        self.whos_turn()

    def starting_rolls(self, p1, p2):
        msg = 'You rolled %s, %s rolled %s'
        self.player1.user.chat(msg % (p1, self.player2.name, p2))
        self.player2.user.chat(msg % (p2, self.player1.name, p1))

    def roll(self, player):
        you,opp = self.players(player)
        d = self.control.roll(player)
        you.chat('You roll %d, %d' % d)
        player = self.player[you.running_game]
        board = you.settings.get_boardstyle()
        you.chat(self.control.board.show_board(player, board))
        opp.chat('%s rolled %d, %d' % ((you.name,)+d))
        player = self.player[opp.running_game]
        board = opp.settings.get_boardstyle()
        opp.chat(self.control.board.show_board(player, board))
        if self.control.pieces == 0:
            you.chat("You can't move.")
            self.move(['zero',], player)

    def move(self, move, player):
        you,opp = self.players(player)
        mv = Move(move, self.control, player)
        if mv.check():
            mv.move()
            oooold_player = player
            player = self.player[you.running_game]
            talk('nach mv.move() war ich %s - jetzt bin ich %s' % (oooold_player,player))
            board = you.settings.get_boardstyle()
            you.chat(self.control.board.show_board(player, board))
            if not str(mv) == 'zero':
                opp.chat('%s moves %s' % (you.name, mv))
            player = self.player[opp.running_game]
            board = opp.settings.get_boardstyle()
            opp.chat(self.control.board.show_board(player, board))
##     TODO: ganz zufällig ist hier auf player "opponent" umgestellt worden.
##           Das sollte man nicht so lassen, sondern im folgenden explizit auf
##           "Opponent" umstellen.
##        opposing_player = self.control.opp[player]
##        talk('....und der zu %s opposing player is %s' % (player,opposing_player))
        if not self.may_double(player):
            talk('autoroll ' + '-'*60)
            talk('autoroll because not may double - new player %s' % player)
            self.roll(player)

    def may_double(self, player):
        return self.ML > 1
            
    def whos_turn(self,):
        msg = 'It is your turn to move'
        self.control.whos_turn().chat(msg)
##        self.player2.chat(msg % (p2, self.player1.name, p1))

    def players(self, player):
        """Gibt die player des Spiels als Tupel (p1,p2) zurück."""
        p1 = self.who[player]
        p2 = self.opponent(p1.name)
        return (p1, p2)
        
    def opponent(self, player):
        return self.opp[player] # TODO: prüfen, ob man das nicht direkt mit opp
                                #       machen kann. Überflüssige Schleife

def getGame(**kw):
    log = kw['list_of_games']
    gid = log.uid()
    game = Game(gid, kw['player1'], kw['player2'], kw['ML'], dice=kw['dice'])
    log.add(game)
    game.start()
    return game.ids

def set_verbose():
    global VERBOSE
    VERBOSE = True
