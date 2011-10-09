#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

import sys
import logging
import time
from version import Version

v = Version()
v.register(__name__, REV)

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.INFO,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('states')
logger.setLevel(logging.DEBUG)

class State:
    """Base class for states in this state machine."""
    
    error_turn = {'roll': ("** It's not your turn to roll the dice.", False),
                  'move': ("** It's not your turn to move.", False),
                  'double': ("** Please wait until %s has moved.", True),
                  'off': ("** It's not your turn.", False),
                  'accept': ("** %s didn't double or resign.", True),
                  }

    error_wrong_cmd = {}

    error_wrong_cmd_genericals = {
                  'accept': ("** %s didn't double or resign.", True),
                  'reject': ("** %s didn't double or resign.", True),
                  }

    def __init__(self,):
        self.active = False
        self.actions = {}
        self.error_wrong_cmd.update(self.error_wrong_cmd_genericals)
        self.label = '%s %s' % (self.__doc__.split()[1], self.name)

    def activate(self, player, **params):
        """Activates this state.
    player:     class Player
    params:     **kw
    """
        logger.log(TRACE, '%s: wird aktiviert mit player %s und Parametern %s)' % (self.name,player.name,params))
        self.player = player
        self.approved_player = self.player  # This may have to be overwritten
                                            # in special(); may be the opponent.
        self.params = params
        self.results = None
        self.active = True
        self.machine(self)      # self.machine is set by the state machine
        self._special()
        self._chat()
        logger.info('%s: player %s, Parameter %s' % (self.label, player.name,params))
        self._auto_action()

    def deactivate(self,):
        self.active = False

    def action(self, player, cmd, **params):
        logger.info('%s: action called by %s: %s with %s' % \
                                    (self.label, player.name, cmd, params))
        if self._state_check(player, cmd):      # action is allowed, only,
            self._action(player, cmd, **params) # when state_check is passed
            if not self.actions[cmd]['follow_up'] is None:
                self._transit(self.actions[cmd]['follow_up'])

    def _auto_action(self,):
        """Method intended for being overwritten. _auto_action() is the last
    method being called during activation phase.
    Default behavior is to perform an action automatically if it is the only
    action and is flagged as 'auto'.
    """
        if (len(self.actions) == 1):
            k = self.actions.keys()[0]
            if self.actions[k]['auto']:
                logger.log(TRACE, '(State) automatisch standard cmd: %s' % k)
                self.action(self.player, k, **self.params)

    def _state_check(self, player, cmd):
        if (player.name == self.approved_player.name):
            if self.actions.has_key(cmd):
                return True
            else:
                message = self._error_message(self.error_wrong_cmd, cmd,
                                                player.opp_name)
                logger.log(TRACE, 'Wrong cmd message (%s) Player %s Approved ' \
                        '%s CMD %s' % (message, player.name,
                                       self.approved_player.name, cmd))
                player.chat_player(message)
                return False
        else:
            message = self._error_message(self.error_turn, cmd,
                                               self.approved_player.name)
            logger.log(TRACE, 'Wrong turn message %s Player %s Approved ' \
                       '%s CMD %s' % (message, player.name,
                                      self.approved_player.name, cmd))
            player.chat_player(message)
            return False

    def _action(self, player, cmd, **params):
        action = self.actions[cmd]['action']
        logger.debug('calling %s with %s' % (action, params))
        self.result = action(player, **params)
        # set attribute instead of return to be able to do some processing
        
    def _transit(self, next_state):
        self.deactivate()
        next_state.activate(self.player, **self.result)
        # parameters come from _action

    def _special(self,):
        """Method intended for being overwritten. _special() is being
    called during activation phase.
    """
        pass

    def _chat(self, msg=None):
        """Send messages to the players during activation phase. This Method
    is intended for being overwritten.
    """
        if not msg is None:
            print msg
        else:
            logger.log(TRACE, '%s: hat nix zu chatten' % (self.name,))

    def _error_message(self, error_messages, cmd, name):
        """Generate a qualified error message in case the command is issued
    by the player not in turn or an erroneous command by the player in turn.
    """
        if not error_messages.has_key(cmd):
            msg = "** Error, no qualified message available for '%s'" % cmd
            give_user = False
            logger.error("%s (%s)" % (msg, name))
        else:
            msg, give_user = error_messages[cmd]
        if give_user:
            msg = msg % name
        return msg

class GameStarted(State):
    """State A: game has started."""
    
    def __init__(self,):
        self.name = 'game_started'
        State.__init__(self)

    def _chat(self, msg=None):
        if self.params['action'] == 'start':
            msg = 'Starting a new game with %s.'
            self.player.chat_player(msg % self.player.opp_name)
            self.player.chat_player_watchers(msg % self.player.opp_name)
            self.player.chat_opponent(msg % self.player.name)
            self.player.chat_opponent_watchers(msg % self.player.name)

    def _auto_action(self,):
        """Start or resume the game, as given by params."""
        cmd = self.params['action']
        logger.log(TRACE, 'automatically starting cmd: %s' % cmd)
        self.action(self.player, cmd, **self.params)

    def _action(self, player, cmd, **params):
        """Special treatment while starting a game. Set active player as a
    result of starting rolls.
    """
        action = self.actions[cmd]['action']
        logger.debug('calling %s with %s' % (action, params))
        self.result = action(player, **{})
        self.player = self.result.pop('turn')
        if cmd == 'resume':
            self.actions[cmd]['follow_up'] = self.result.pop('follow')

    # +++++++++++ start
    # you rolled, he rolled
    # it is you turn; he makes the first move
    # board
    
class TurnStarted(State):
    """State B: a new turn has started."""
    
    error_wrong_cmd = {'move': "** You have to roll the dice before moving.",}

    def __init__(self,):
        self.name = 'turn_started'
        State.__init__(self)

    # automatisch weitergehen bei no_double oder auto_roll
    #  sonst
    # please roll or double
    # +++++++++++ roll, double

    def _chat(self, msg=None):
        self.player.board_opponent()
        self.player.board_player()
        if self.params['may_double']:
            if msg is None:
                msg = "It's your turn. Please roll or double"
            self.player.chat_player(msg)

    def _auto_action(self,):
        """Decide whether player may double and automatically perform
    'roll (state H)' if he may not.
    """
        if not self.params['may_double']:
            logger.log(TRACE, 'automatisches cmd: %s' % 'roll')
            self.action(self.player, 'roll')

class Doubled(State):
    """State C: the cube has been turned."""
    
    def __init__(self,):
        self.name = 'doubled'
        State.__init__(self)

    # you double, please wait; he doubles, please accept
    # +++++++++++ take, drop

    def _chat(self, msg=None):
        if msg is None:
            msg = 'You double. Please wait for %s to accept or reject.' % \
                                                      self.player.opp_name
            self.player.chat_player(msg)
            msg = "%s doubles." % self.player.name
            self.player.chat_opponent(msg + " Type 'accept' or 'reject'.")
            self.player.chat_player_watchers(msg)
            self.player.chat_opponent_watchers(msg)

    def _special(self,):
        self.approved_player = self.player.opponent

class Taken(State):
    """State D: the cube has been taken."""
    
    def __init__(self,):
        self.name = 'taken'
        State.__init__(self)

    # you accept, the cube shows; he accepts, the cube shows
    # +++++++++++ roll      (auto)

    def _chat(self, msg=None):
        if msg is None:
            cube = 'The cube shows %d.' % self.params['value']
            msg = 'You accept the double. %s' % cube
            self.player.chat_opponent(msg)
            msg = '%s accepts the double.' % self.player.opp_name
            self.player.chat_player(msg + ' %s' % cube)
            self.player.chat_player_watchers(msg)
            self.player.chat_opponent_watchers(msg)

class Rolled(State):
    """State H: dice have been rolled."""
    
    def __init__(self,):
        self.name = 'rolled'
        State.__init__(self)

    def _chat(self, msg=None):
        if self.params.has_key('game_started'):
            self.player.chat_player("It's your turn to move.")
            msg = '%s makes the first move.' % self.player.name
            self.player.chat_opponent(msg)
            self.player.chat_player_watchers(msg)
            self.player.chat_opponent_watchers(msg)
        else:
            a, b = self.params['roll']
            msg = 'You roll %d and %d.' % (a,b)
            self.player.chat_player(msg)
            msg = '%s rolls %d and %d.' % (self.player.name, a, b)
            self.player.chat_opponent(msg)
            self.player.chat_player_watchers(msg)
            self.player.chat_opponent_watchers(msg)

class TurnFinished(State):
    """State I: this turn has been finished."""
    
    def __init__(self,):
        self.name = 'turn_finished'
        State.__init__(self)

    # send board
    # +++++++++++ hand_over      (auto)

    def _transit(self, next_state):
        self.deactivate()
        next_state.activate(self.player.opponent, **self.result)
        # parameters come from _action

class Checked(State):
    """State E: dice have been checked."""

    error_wrong_cmd = {'roll': "** You did already roll the dice.",}

    def __init__(self,):
        self.name = 'checked'
        State.__init__(self)

    def _chat(self, msg=None):
        self.player.board_player()
        self.player.board_opponent()

    def _auto_action(self,):
        """Decide whether no moves can be made and automatically perform
    the 'cant_move' automatic action.
    """
        follower = 'move'       # TODO: hier ist ziemlich stark ausprogrammiert
                                #       nicht sehr generisch
        if self.params['nr_pieces'] == 0:
            self.player.chat_player("You can't move.")
            follower = 'cant_move'
        if self.player.user.greedy_bearoff():
            logger.log(TRACE, 'automatic move because greedy')
            if self.params.get('greedy_possible', False):
                params = {'move': self.params['moves']}
                self.action(self.player, follower, **params)
        if self.actions[follower]['auto']:
            logger.log(TRACE, 'automatic cmd: %s' % follower)
            self.action(self.player, follower)
            ## TODO: chat The only possible move is d-e ... j-k .
        else:
            self.player.chat_player("Please move %d pieces." % \
                                        self.params['nr_pieces'])

class Moved(State):
    """State F: move has been made."""
    
    def __init__(self,):
        self.name = 'moved'
        State.__init__(self)

    def _chat(self, msg=None):
        if msg is None:
            msg = '%s moves %s  .' % (self.player.name,
                                   ' '.join(self.params['moved']))
        self.player.chat_opponent(msg)

    # he moves.....
    #  oder
    # Spiel zu Ende?   automatisch weitergehen (generisch)
    # +++++++++++ handover, nop      (auto)
    # board

    def _auto_action(self,):
        """Decide whether game is finished and automatically perform
    'nextturn (state I)' or 'wingame (state G)'.
    """
        follower = {True: 'win', False: 'turn'}[self.params['finished']]
        if self.actions[follower]['auto']:
            logger.log(TRACE, 'automatic cmd: %s' % follower)
            self.action(self.player, follower)

class GameFinished(State):
    """State G: game has ended."""
    
    def __init__(self,):
        self.name = 'finished'
        State.__init__(self)

    def _chat(self, msg=None):
        if msg is None:
            try:
                reason = self.params['reason']
            except:
                logger.error("FINISH WITHOUT 'reason'!!!")
                raise           # TODO: alle fälle abfangen, dann kann das hier weg
            v = self.params['value']
            opp = self.player.opp_name
            me = self.player.name
            if v == 1:
                points = '1 point'
            else:
                points = '%d points' % v
            if reason == 'won':
                msg_me = 'You win the game and get %s. ' \
                                         'Congratulations!' % points
                msg = '%s wins the game and gets %s.'
                msg_him = msg % (me, points,) + ' Sorry.'
                msg_watchers = msg % (me, points,)
            elif reason == 'passed':
                msg_me = '%s gives up. You win %s.' % (opp, points)
                msg_him = "You give up. %s wins %s." % (me, points)
                msg_watchers = '%s gives up. %s wins %s.' % (opp, me, points)
            elif reason == 'resigned':
                msg_me = "%s accepts and wins %s." % (opp, points)
                msg_him = 'You accept and win %s.' % points
                msg_watchers = msg_me
            else:
                logger.warning("FINISH: reason '%s' not known!" % reason)
                msg_him = msg_me = 'I feel a little confused.'
            self.player.chat_player(msg_me)
            self.player.chat_opponent(msg_him)
            self.player.chat_player_watchers(msg_watchers)
            self.player.chat_opponent_watchers(msg_watchers)

class Resigned(State):
    """State J: a player resigns the game."""
    
    def __init__(self,):
        self.name = 'resigned'
        State.__init__(self)

    def _chat(self, msg=None):
        if msg is None:
            a = self.params['value']
            opp = self.player.opp_name
            me = self.player.name
            if a > 1:
                msg_me = '%%s want to resign. %s will win %d points.' % (opp, a)
                msg_him = "%s wants to resign. You will win %d points." \
                          " Type 'accept' or 'reject'." % (me, a)
            elif a == 1:
                msg_me = '%%s want to resign. %s will win 1 point.' % opp
                msg_him = "%s wants to resign. You will win 1 point." \
                          " Type 'accept' or 'reject'." % me
            self.player.chat_player(msg_me % 'You')
            self.player.chat_opponent(msg_him)
            self.player.chat_player_watchers(msg_me % me)
            self.player.chat_opponent_watchers(msg_me % me)

    def _action(self, player, cmd, **params):
        params.update(self.params)  # TODO: diese Zeile weicht von State ab;
                                    #       unschöne Stelle; kann das nicht
                                    #       für alle gelten??
        action = self.actions[cmd]['action']
        logger.debug('calling %s with %s' % (action, params))
        self.result = action(player, **params)
        # set attribute instead of return to be able to do some processing
        
    def _transit(self, next_state):
        self.deactivate()
        if self.result['response'] == 'accepted':
            self.result['value'] = self.params['value']
            next_state.activate(self.player, **self.result)
        else:
            return_to = self.params['active_state']
            player = return_to.player
            params = return_to.params
            return_to.activate(player, **params)

    def _special(self,):
        self.approved_player = self.player.opponent

class StateMachine:
    """Container for a bundle of states. Hands out some controls. Controls
which state is active.
"""
    def __init__(self, states):
        self.states = states
        for s in states:
            self.states[s].machine = self._activate
            # TODO: Verbesserung im Code!!
            #       Aber nur mit Test und in eigenem Verbesserungszyklus machen!
            ##        for s in states.values():
            ##            s.machine = self._activate
        logger.log(TRACE, 'CONSTRUCTING (%d states)' % len(self.states))

    def start(self, player, state=None, **kw):
        """Allows to start the state machine."""
        if state is None:
            state_name = 'game_started'
        else:
            state_name, player, kw = state
        logger.log(TRACE, 'STARTING   player %s' % player.name)
        self.states[state_name].activate(player, **kw)

    def action(self, player, cmd, **kw):
        """Allows control to send actions, taken by the players."""
        #print 'DEBUG', kw
        logger.log(TRACE, 'ACTION   player %s (%s with %s)' % \
                                               (player.name, cmd, kw))
        if cmd == 'resign':  # special treatment for 'resign'; like a "trap"
            kw['active_state'] = self.active
            self.states['resigned'].activate(player, **kw)            
        else:
            self.active.action(player, cmd, **kw)

    def _activate(self, state):
        """States activate themselves using this method."""
        self.active = state
        self.persistent(state.name, state.player, state.params)
        #  TODO: vielleicht nur in states B E C J (performanz)
        logger.log(TRACE, 'ACTIVATING %s (%s)' % (state.name, state.__doc__))

    def done():
        """True, if game is finished."""
        return self.active.name == 'finished'

class Commands:
    """Used for the little standalone test in the __main__ section."""
    def __init__(self, player1):
        self.player1 = player1
        
    def _start(self, p, **kw):
        logger.log(TRACE, 'stub cmd +++++ _start')
        return {'roll': (3,5), 'turn': self.player1}

    def roll(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ roll: %s (%s)' % (player.name, params))
        return {'roll': (3,5),}

    def double(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ double: %s (%s)' % (player.name, params))
        return {}

    def take(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ take: %s (%s)' % (player.name, params))
        return {}

    def drop(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ drop: %s (%s)' % (player.name, params))
        return {}

    def check_roll(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ check_roll: %s (%s)' % (player.name, params))
        return {'nr_pieces': 2}

    def _move(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ _move: %s (%s)' % (player.name, params))
        return {'moved': params['move'].split(), 'finished': False}

    def nop(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ nop: %s (%s)' % (player.name, params))
        return {}

    def hand_over(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ hand_over: %s (%s)' % (player.name, params))
        return {'may_double': False}

class TestUser:
    """Used for the little standalone test in the __main__ section."""
    def __init__(self, name):
        self.name = name

    def chat(self, msg):
        print 'CHAT -> %s:' % self.name, msg
        
if __name__ == '__main__':
    from game import Player
    from game import BGMachine

    try:
        trace = sys.argv[1] == '-t'
    except:
        trace = False
    if trace:
        logger.setLevel(TRACE)

    p1 = Player(TestUser('white'), None, 0)
    p2 = Player(TestUser('black'), p1, 0)
    p1.set_opponent(p2)
    s = BGMachine(Commands(p1))
    logger.info('-'*40 + ' start')
    s.start(p1)
    logger.info('-'*40 + ' move 18-12 12-10')
    s.action(p1, 'move', move='18-12 12-10')
    logger.info('-'*40 + ' move 1-6 2-8')
    s.action(p2, 'move', move='1-6 2-8')
    logger.info('-'*40 + ' ??')
