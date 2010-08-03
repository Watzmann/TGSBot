#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von Game-related Routinen."""

from dice import getDice

class GamesList:        # TODO: als Singleton ausführen
                        # TODO: mit UsersList in eine Klasse überführen
    def __init__(self,):
        self.active_games = {}

    def add(self, game):
        for i in game.ids:
            self.active_games[i] = (game, game.player[i])

    def get(self, gid, default=None):
        #print 'returning gid %s' % gid
        return self.active_games.get(gid, default)

class Board:
    """The Board holds all information about position etc.. Special methods
check for valid moves etc.."""

    def __init__(self,):
        self.score_fmt = "board:%s:%s:%d:%d:%d:"
##        self.position_fmt = "%d:"*26
        self.position_fmt = "%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:%d:%d:%d:%d:%d:  %d:"
        self.dice_fmt = "%d:"*5
        self.cube = "1:1:1:0:"
        self.direction = {'you':"1:-1:0:25:",
                          'opp':"-1:1:25:0:"}
        self.move_fmt = "%d:%d:%d:%d:%d:0:0:0"
        
    def set_score(self, you, opp, ML):
##        print you, opp, type(ML)
        self.score = {'you':self.score_fmt % ('You', opp[0], ML, you[1], opp[1]),
                      'opp':self.score_fmt % ('You', you[0], ML, opp[1], you[1])}

    def set_dice(self, turn, dice,):
        print 'turn', turn
        if turn in [1,2]:
            t = [0,1,-1][turn]
            self.dice = {'you':self.dice_fmt % ((t,) + dice + (0,0)),
                         'opp':self.dice_fmt % ((t,) + (0,0) + dice)}
        else:
            self.dice = {'you':self.dice_fmt % (0,)*5,}
            self.dice['opp'] = self.dice['you']

    def set_move(self, you, opp, move):
        self.move = {'you':self.move_fmt % (you[0], opp[0], you[1], opp[1], move),
                     'opp':self.move_fmt % (opp[0], you[0], opp[1], you[1], move)}

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
##        return score + self.position + dice + cube + direction + move
        return '%s | '*6 % (score, self.position, dice, cube, direction, move)

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
        self.score = {'p1':1, 'p2':2}
        if not board is None:
            self.board = board
        else:
            self.board = Board()
            self.board.set_score((self.white.name, self.score['p1']),
                                 (self.black.name, self.score['p2']),
                                  self.game.ML)
            self.set_position()

    def start(self,):
        a = b = 0
        while a == b:
            a,b = self.dice.roll()
            self.game.starting_rolls(a,b)
        self.turn = {True:1, False:2}[a>b]

    def whos_turn(self,):
        return {1:self.white, 2:self.black, 0:None}[self.turn]

    def roll(self, player):
        # TODO: kontrollieren, ob der dran ist
        d = self.dice.roll()    # TODO    turn und dice eintragen
        self.dice_roll = d
        self.pieces = {True:4, False:2}[d[0]==d[1]]
        self.board.set_dice(self.turn, d)
        self.set_move()
        return d

    def set_move(self,):
        p1 = (self.home['p1'], self.bar['p1'])
        p2 = (self.home['p2'], self.bar['p2'])
        self.board.set_move(p1, p2, self.pieces)

    def set_position(self,):
        self.board.set_position(self.position)
        
    def move(self, move, player):
        # TODO: kontrollieren, ob der dran ist
        print move, 'changes the board'
        print 'player', player, 'whos_turn', self.whos_turn().name
        self.position[move[0]] -= 1
        self.position[move[1]] += 1

    def hand_over(self,):
        self.turn = 3 - self.turn
        self.board.set_dice(self.turn, (0,0))

class Game:
    # players watchers
    def __init__(self, p1, p2, ML, board=None, dice='random'):
        self.id = '908239874918'    # funny id, is that neccessary?
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
        print 'rolling fool', player
        you.chat('You roll %d, %d' % d)
        you.chat(self.control.board.show_board('you'))
        opp.chat('%s rolled %d, %d' % ((you.name,)+d))
        opp.chat(self.control.board.show_board('opp'))

    def move(self, move, player):
        you,opp = self.players(player)
        mv = Move(move, self.control, player)
        if mv.check():
            mv.move()
            you.chat(self.control.board.show_board('you'))
            opp.chat('%s moves %s' % (you.name, mv))
            opp.chat(self.control.board.show_board('opp'))

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
    game = Game(kw['player1'], kw['player2'], kw['ML'], dice=kw['dice'])
    kw['list_of_games'].add(game)
    game.start()
    return game.ids
