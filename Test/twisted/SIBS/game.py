#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

from time import time
from dice import getDice

STANDALONE = False

class GamesList:        # TODO: als Singleton ausführen
                        # TODO: mit UsersList in eine Klasse überführen
    def __init__(self,):
        self.active_games = {}
        self.active_ids = {}

    def add(self, game):
        for i in game.ids:
            self.active_games[i] = (game, game.player[i])
        self.active_ids[game.id] = game.id
        # TODO: denk dran, beim Ende des Spiels aufzuräumen

    def get(self, gid, default=None):
        #print 'returning gid %s' % gid
        return self.active_games.get(gid, default)

    def uid(self,):
        gen = lambda: ''.join(('%f' % time()).split('.'))
        gid = gen()
        while self.active_ids.has_key(gid):
            print 'collision with', gid
            gid = gen()
        return gid

class Board:
    """The Board holds all information about position etc.. Special methods
check for valid moves etc.."""

    def __init__(self,):
        self.score_fmt = "board:%s:%s:%d:%d:%d:"
        if STANDALONE:
            self.position_fmt = "%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:"
        else:
            self.position_fmt = "%d:"*26
        self.dice_fmt = "%d:"*5
        self.cube = "1:1:1:0:"
        self.direction = {'p1':"1:-1:0:25:",
                          'p2':"-1:1:25:0:"}
        self.move_fmt = "%d:%d:%d:%d:%d:0:0:0"
        
    def set_score(self, p1, p2, ML):
##        print you, opp, type(ML)
        self.score = {'p1':self.score_fmt % ('You', p2[0], ML, p1[1], p2[1]),
                      'p2':self.score_fmt % ('You', p1[0], ML, p2[1], p1[1])}

    def set_dice(self, turn, dice,):
        print 'set_dice turn', turn
        if turn == 1:
            self.dice = {'p1':self.dice_fmt % ((1,) + dice + (0,0)),
                         'p2':self.dice_fmt % ((1,) + (0,0) + dice)}
        elif turn == 2:
            self.dice = {'p1':self.dice_fmt % ((-1,) + (0,0) + dice),
                         'p2':self.dice_fmt % ((-1,) + dice + (0,0))}
        else:
            self.dice = {'p1':self.dice_fmt % (0,)*5,}
            self.dice['p2'] = self.dice['p1']

    def set_move(self, p1, p2, move):
        self.move = {'p1':self.move_fmt % (p1[0], p2[0], p1[1], p2[1], move),
                     'p2':self.move_fmt % (p2[0], p1[0], p2[1], p1[1], move)}

    def set_position(self, position):
        self.position = self.position_fmt % tuple(position)
        
    def check(self, player, move):
        msg = "can't move to Berlin"
        return msg

    def show_board(self, whom):
        score = self.score[whom]
        dice = self.dice[whom]
        cube = self.cube
        direction = self.direction[whom]
        move = self.move[whom]
        if STANDALONE:
            return '%s | '*6 % (score, self.position, dice, cube, direction, move)
        else:
            return score + self.position + dice + cube + direction + move

class Move:
    def __init__(self, move, control, player):
        self.mv = move
        self.control = control
        self.player = player

# TODO: eigene exceptions fangen fehler beim move ab
#       rollback in position ermöglichen

    def check(self,):
        print 'checke %s' % self
        return True

    def move(self,):
        for m in self.mv:
            z = m.split('-')
            if z[0] == 'bar':
                z0 = self.control.direction[self.player]['bar']
            else:
                z0 = int(z[0])
            z1 = int(z[1])
            z = (z0,z1)
            print 'moving %d to %d' % (z0,z1)
            self.control.move(z, self.player)
        self.control.set_position()
        self.control.hand_over()

    def __str__(self,):
        return ' '.join(self.mv)

class GameControl:
    """GameControl controls the process of playing a single game of BG."""
    def __init__(self, game, board=None, dice='random'):
        self.game = game
        self.white = game.player1   # TODO: sehr wichtig, diese Zuordnungen
        self.black = game.player2   #       zu überarbeiten
        self.dice = getDice(dice)
        self.cube = 1
        self.turn = 0       # TODO oder was im board-status richtig ist
        self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                            5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
        self.home = {'p1':0, 'p2':0}
        self.bar = {'p1':0, 'p2':0}
        self.opp = {'p1':'p2', 'p2':'p1'}
        self.direction = {'p1':{'home':0, 'bar':25}, 'p2':{'home':25, 'bar':0}}
            # TODO:  wenn es hier definiert ist, dann muss es von hier
            #        im board gesetzt werden.
        if STANDALONE:
            self.score = {'p1':1, 'p2':2}
        else:
            self.score = {'p1':0, 'p2':0}
        if not board is None:
            self.board = board
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
                # TODO:  position muss vom Board abgekupfert werden.
        else:
            self.board = Board()
            self.board.set_score((self.white.name, self.score['p1']),
                                 (self.black.name, self.score['p2']),
                                  self.game.ML)
            self.position = [0, -2,0,0,0,0,5, 0,3,0,0,0,-5,
                                5,0,0,0,-3,0, -5,0,0,0,0,2, 0]
            self.set_position()

    def start(self,):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)
        self.dice_roll = d = (a,b)
        self.turn = {True:1, False:2}[a>b]
        self.pieces = {True:4, False:2}[d[0]==d[1]]
        self.board.set_dice(self.turn, d)
        print 'in start', self.turn, self.pieces, self.board.dice
        self.set_move()

    def whos_turn(self,):
        return {1:self.white, 2:self.black, 0:None}[self.turn]

    def check_roll(self, dice, player):
        """Checks for possible moves depending on 'dice'."""
        print 'check_roll %s fuer spieler %s' % (dice, player)
        exhausted = False
        list_of_moves = []
        pos = self.position
        d1, d2 = dice
        nr_of_moves = {True:4, False:2}[d1 == d2]
        # -------------------------------------------enter from the bar
        bar_moves = min(nr_of_moves, self.bar[player])
        bar = self.direction[player]['bar']
        print 'der spieler %s hat %d moves von der bar (%d)' % (player, bar_moves, bar)
        for m in range(bar_moves):
            d = dice[m]
            if bar == 25:
                p = bar - d
                if abs(pos[p]) < 2:
                    list_of_moves.append('bar-%d' % p)
                print 'hab getested: bar %d  wurf %d   point %d   checker %d' % \
                      (bar,d,p,abs(pos[p]))
        if len(list_of_moves) < bar_moves:
            nr_of_moves = len(list_of_moves)
            exhausted = True
        if exhausted:
            print 'spieler %s kann nur %d zuege ziehen' % (player, nr_of_moves)
        return (nr_of_moves, list_of_moves)
        
    def roll(self, player):
        # TODO: kontrollieren, ob der dran ist
        d = self.dice.roll()    # TODO    turn und dice eintragen
        self.dice_roll = d
        self.possible_moves = self.check_roll(d, player)
        self.pieces = self.possible_moves[0]
        self.board.set_dice(self.turn, d)
        self.set_move()
        return d

    def set_move(self,):        # TODO: was passiert hier eigentlich
        p1 = (self.home['p1'], self.bar['p1'])
        p2 = (self.home['p2'], self.bar['p2'])
        self.board.set_move(p1, p2, self.pieces)

    def set_position(self,):
        self.board.set_position(self.position)
        
    def move(self, move, player):
        # TODO: kontrollieren, ob der dran ist
        print move, 'changes the board'
        print 'player', player, 'whos_turn', self.whos_turn().name
        if self.turn == 1:              # immer 'p1'  TODO: stimmt das?
                                        #               dann kann self.turn weg!
            self.position[move[0]] -= 1
            if move[0] == 25:
                print 'bar', self.bar
                self.bar['p1'] -= 1
            if self.position[move[1]] == -1:    # werfen
                self.position[move[1]] = 1
                self.position[0] -= 1
                print player, 'wirft', self.opp[player]
                self.bar[self.opp[player]] += 1   # TODO: siehe oben;
                                                  #   hier könnte hart 'p2' hin
                                                  #   dann kann self.opp weg
            else:
                self.position[move[1]] += 1
        elif self.turn == 2:
            self.position[move[0]] += 1
            if move[0] == 0:
                print 'bar', self.bar
                self.bar['p2'] -= 1
            if self.position[move[1]] == 1:    # werfen
                self.position[move[1]] = -1
                self.position[25] += 1
                print player, 'wirft', self.opp[player]
                self.bar[self.opp[player]] += 1
            else:
                self.position[move[1]] -= 1
        self.set_move()

    def hand_over(self,):
        self.turn = 3 - self.turn
        self.board.set_dice(self.turn, (0,0))

class Game:
    # players watchers
    def __init__(self, gid, p1, p2, ML, board=None, dice='random'):
        self.id = gid #'908239874918'    # funny id, is that neccessary?
                                    # TODO: YES - die muss unique sein!!!!!
        self.player1 = p1
        self.player2 = p2
        self.ids = (self.id + '_p1', self.id + '_p2')
        self.player = dict(zip(self.ids,('p1','p2')))
        self.who = dict(zip(('p1','p2'),(p1,p2)))
        self.ML = int(ML)
        self.opp = {p1.name:p2, p2.name:p1}
        self.control = GameControl(self, board=board, dice=dice)
        print 'New game with id %s, %s vs %s' % (self.id, p1.name, p2.name)

    def start(self,):
        msg = 'Starting a new game with %s'
        self.player1.chat(msg % self.player2.name)
        self.player2.chat(msg % self.player1.name)
        self.control.start()
        self.whos_turn()

    def starting_rolls(self, p1, p2):
        msg = 'You rolled %s, %s rolled %s'
        self.player1.chat(msg % (p1, self.player2.name, p2))
        self.player2.chat(msg % (p2, self.player1.name, p1))

    def roll(self, player):
        you,opp = self.players(player)
        d = self.control.roll(player)
        you.chat('You roll %d, %d' % d)
        you.chat(self.control.board.show_board(self.player[you.running_game]))
        opp.chat('%s rolled %d, %d' % ((you.name,)+d))
        opp.chat(self.control.board.show_board(self.player[opp.running_game]))
        if self.control.pieces == 0:
            you.chat("You can't move.")
            self.control.hand_over()
        return self.control.pieces > 0

    def move(self, move, player):
        you,opp = self.players(player)
        mv = Move(move, self.control, player)
        if mv.check():
            mv.move()
            you.chat(self.control.board.show_board(self.player[you.running_game]))
            opp.chat('%s moves %s' % (you.name, mv))
            opp.chat(self.control.board.show_board(self.player[opp.running_game]))

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

def set_standalone():
    global STANDALONE
    STANDALONE = True
