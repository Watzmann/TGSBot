#!/usr/bin/python
"""teste Argumente von der Befehlszeile


c 12/2004 A.Hausmann (Rheinhausen)
"""

import sys
sys.path.insert(1,'/home/andreas/Python/modules')
from cmdfw import CommandFrameWork

# --------- TestRoutine ----------
# brauch ich die jetzt noch?
# oder brauch ich _die_ und nicht TestArgs?

def test(o,tests):
    print arguments
    print tests
    for t in tests:
            print '-'*10, t, '-'*10
            sts = o.run(t)
            print "Exit status:", `sts`

# --------- TestArgsRoutine ----------

def testargs(o):
    tests = [
            [],
            ['hello'],
            ['help'],
            ['-x'],
            ['hello', '-x'],
#            ['tricky.py', 'seven', 'old', 'women'],
            ['--test', 'hello', '34', '54', 'pass=17'],
            None,
            ]
    print arguments
    print tests
    for t in tests:
            print '-'*10, t, '-'*10
            sts = o.run(t)
            print "Exit status:", `sts`

# --------- Ablauf ----------

print __name__
arguments = sys.argv[:]

class myCommands(CommandFrameWork):

    def do_hello(self,opts,args):
        "hello -- first trial, no args"
        print "hello"

    def do_help(self,opts,args):
        "help  -- evoke help messages"
        #help(__name__)
        self.usage('My name is '+__name__)

#    def default(self):
#            """Default method, called when no subcommand is given.
#            You should always override this."""
#            print "No arguments given; no default action specified!"

x = myCommands()
        
if __name__ == "__main__" and arguments[0].startswith('testargs'):
    testargs(x)
else:
    sts = x.run()
    print "Exit status:", `sts`

