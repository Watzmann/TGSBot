"""Enable bot to invite other players (i.e. other bots)."""

from twisted.internet import defer
from operation.basics import Request, Response
from operation.play import Join

class Bots(Request):
    def __init__(self, dispatch, manage, callback):
        self.expected = "Playing bots:"
        Request.__init__(self, dispatch, manage,)
        self.bots = defer.Deferred()
        self.bots.addCallback(callback)
        self.send_command('show bots_ready' % opponent)

    def received(self, message):
        self.settings = {}
        log.msg('BOTS tests: %s' % message[0], logLevel=VERBOSE)
        try:
            idx = message.index('')
            self.bots = message[1:idx]
        except ValueError:
            self.bots = message[1:]
        log.msg('BOTS: bots present: %s' % t, logLevel=logging.DEBUG)
        log.msg('BOTS applies '+'+'*40, logLevel=VERBOSE)
        self.purge()
        del message[:idx+1]

class Busy(Request):

    def __init__(self, dispatch, manage, opponent, refusal, invitation):
        self.expected = refusal
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        self.settings = {}
        log.msg('BUSY tests: %s' % message[0], logLevel=VERBOSE)
        if invitation in self.manage:
            del self.manage[invitation]
        log.msg('BUSY applies '+'+'*40, logLevel=VERBOSE)
        self.purge()
        del message[0]

def invite_bots(dispatch, manage):
    invite = Invite(dispatch, manage)

        #join = Join(self, self.requests, opponent, ML, type_of_invitation)
        #if type_of_invitation == 0:
            #join.send_command('join %s' % opponent)

def join(self, opponent, ML, type_of_invitation=0):
    join = Join(self, self.requests, opponent, ML, type_of_invitation)
    if type_of_invitation == 0:
        join.send_command('join %s' % opponent)

def invitation(dispatch, manage, opponent, ML=-1):
    refusal = "** %s is already playing with someone else." % opponent
    Busy(
