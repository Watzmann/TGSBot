#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Commands about toggles, settings, etc."""

import time
from twisted.python import log
from operation.basics import Request

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Toggle(Request):
    """Query the toggles. From the response set dispatch.toggles.

  Explanation of mechanics:

  1) Upon instanciation the expected server answer string is set to
       self.expected = "The current settings are:".
     This takes effect in Request.__init__ as it is stored to 'manage'.
     The instanciated object is stored in 'manage' which is held alive in
     'self.requests' in the dispatcher.

  2) The dispatcher may invoke the 'toggle'-command as it likes.

  3) When parsing the dispatcher detects the expected server answer in
       if lines[0] in self.requests:
     and calls the requests received() method handing over the full response.

  4) Toggle.received() now parses the message and sets the toggles variable.

  5) If toggle 'ready' is 'off', then it now is set 'on'.
     This is indeed a bad side effect; maybe it is not wanted; setting the bot
     'ready off' is not possible.
"""
    def __init__(self, dispatch, manage,):
        self.expected = "The current settings are:"
        self.label = 'TOGGLE'
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        self.toggles = {}
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        try:
            for t in message[1:]:
                if len(t) < 3:
                    break
                s = t.split()
                self.toggles[s[0]] = s[-1]
        except:
            err_msg = '%s got unexpected data: >%s<' % (self.label, message)
            raise RuntimeError(err_msg)
        self.dispatch.toggles = self.toggles
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        del message[:len(self.toggles)+1]
        self.set_standard()
        self.purge()

    def set_standard(self,):
        for t,v in (('ready', 'YES'),
                    ('notify', 'NO'),
                    ('report', 'NO'),
                    ('silent', 'YES'),
                    ('friend', 'NO'),
                    ):
            log.msg('toggle %s == %s|%s#' % (t,v,self.toggles[t]), logLevel=logging.DEBUG)
            if self.toggles[t] != v:
                log.msg('TOGGLE sets %s to %s  ' % (t,v) +'>'*30,
                                                            logLevel=VERBOSE)
                self.dispatch.send_server('toggle %s' % t)
                self.dispatch.toggles[t] = v

class Set(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "Settings of variables:"
        self.label = 'SET'
        Request.__init__(self, dispatch, manage,)

    def set_delay_value(self, delay):
        self._delay = delay

    def received(self, message):
        self.settings = {}
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        try:
            for t in message[1:8]:
                log.msg('SET: working on >%s<' % t, logLevel=logging.DEBUG)
                s = t.split()
                key = s[0].rstrip(':')
                self.settings[key] = s[-1]
        except:
            err_msg = '%s got unexpected data: >%s<' % (self.label, message)
            raise RuntimeError(err_msg)
        self.dispatch.settings = self.settings
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        del message[:8]
        if self.settings['boardstyle'] != '5':
            log.msg('SET sets boardstyle to 5'+'>'*35, logLevel=VERBOSE)
            self.set_boardstyle(5)
        if self.settings['delay'] != self._delay:
            log.msg('SET sets delay '+'>'*35, logLevel=VERBOSE)
            self.set_delay()
        self.purge()

    def set_delay(self,):
        self.dispatch.send_server('set delay %s' % self._delay)
        self.dispatch.settings['delay'] = self._delay

    def set_boardstyle(self, style):
        self.dispatch.send_server('set boardstyle %d' % style)
        self.dispatch.settings['boardstyle'] = str(style)

class GnubgSettings:
    """Action objects can take one of six orders and then, if appropriate, ask
    gnubg for the proper action to take in this case.
"""
    def __init__(self, order, parameters, gnubg, callback):
        log.msg('create gnubgSettings with (%s - %s)' % (order, parameters),
                                                        logLevel=logging.DEBUG)
        self.gnubg = gnubg
        self.callback = callback
        {'get_player': self._get_player,
         }[order](parameters)

    def _get_player(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('get_player')
        log.msg('got GET_PLAYER oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)
