"""Commands about toggles, settings, etc."""

from operation.basics import Request

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
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        self.toggles = {}
        #print 'TOGGLE: READ MY LINES', message
        try:
            for t in message[1:]:
                #print 'TOGGLE: working on >%s<' % t
                s = t.split()
                self.toggles[s[0]] = s[-1]
        except:
            raise RuntimeError('TOGGLE got unexpected data: >%s<' % message)
        self.dispatch.toggles = self.toggles
        #print 'TOGGLE: FIND READY', self.toggles['ready']
        if self.toggles['ready'] == 'NO':
            self.set_ready()
        self.purge()

    def set_ready(self,):
        self.dispatch.send_server('toggle ready')
        self.dispatch.toggles['ready'] = 'YES'

class Set(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "Settings of variables:"
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        self.settings = {}
        #print 'SET: READ MY LINES', message
        try:
            for t in message[1:8]:
                #print 'SET: working on >%s<' % t
                s = t.split()
                key = s[0].rstrip(':')
                self.settings[key] = s[-1]
        except:
            raise RuntimeError('SET got unexpected data: >%s<' % message)
        self.dispatch.settings = self.settings
        if self.settings['boardstyle'] != '3':
            self.set_boardstyle()
        self.purge()

    def set_boardstyle(self,):
        self.dispatch.send_server('set boardstyle 3')
        self.dispatch.settings['boardstyle'] = '3'
