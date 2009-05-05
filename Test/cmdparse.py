#!/usr/bin/python
# -*- coding: utf-8 -*-
"""cmdparse - ein Command-Parser nach dem Vorbild von optparse"""

__svn_date__ = "$Date: 2006-09-26 11:12:58 +0200 (Di, 26 Sep 2006) $"
__version__ = "$Revision: 49 $"[11:-2]
__svn_url__ = "$URL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/Test/cmdparse.py $"

# etwa 8 Std. Aufwand für eine erste Implementierung
# konzentriert, ohne vorher Design gemacht zu haben.
# Selbst hier hätte sich gelohnt, vorher zu überlegen und zu designen.

# TODOs:
# - help-Texte für Kommandos generieren

class Argument:
    """Das Argument und seine Methoden #??#"""
    types = ('string','int','long','float','list','tuple',)
    def __init__(self, name='', optflag=True, argtype='', default=None):
        self.name = name
        self.optflag = optflag
        self.type = argtype
        self.value = default
        return

class Command:
    """Single command, its syntax, its arguments"""

    arguments = {}
    arg_list = []
    mandatory = []
    optional = []

    def __init__(self,name,args):
        """Store away name and arguments.
        name : string     the Command Name
        args : [<argument-descriptor>,]
        <argument-descriptor> : 4-tuple (arg_name, opt_flag, arg_type, default)
            arg_name : name of the argument
            opt_flag : flag 'optional'; True:optional; False:mandatory
            arg_type : type of the argument [string, int, long, float,list,tuple,]
            default  : default value of missing mandatory argument
        """
        # das mit den 'arguments' (hier: 4-tupel) muss vielleicht in Konstruktor
        # von class Argument. Das heißt, dass hier eine Liste von Instanzen von
        # Argument übergeben wird. Oder die Liste wird gerade so an Argument()
        # weitergegeben      #??#
        self.name = name
        for a in args:
            arg_name, opt_flag, arg_type, default = a
            arg = Argument(arg_name, opt_flag, arg_type, default)
            self.arguments[arg_name] = arg
            if opt_flag:
                self.optional.append(arg)
            else:
                self.mandatory.append(arg)
        self.arg_list = self.arguments.keys()
        return

    def get_arg_list(self,):
        return self.arg_list

class ClCommand(Command):
    """ClCommand is a command found on the commandline"""

    arg_list = []

    def __init__(self,name,args):
        self.name = name
        self.arg_list = args
    
class Commands:
    """Container for commands found on the commandline"""

    # die Trennung zwischen den 2 Command-Typen (mögliche Kommandos und
    # tatsächlich auf der Kommandozeile gegebene Kommandos) ist absolut
    # unsauber und noch nicht durchdacht. Außerdem fehlt eine treffende
    # Bezeichnung für diese beiden Arten.
    # Im Moment ist das Problem durch Class 'ClCommand' gelöst
    #
    #??# Es fehlt die Verwertung des Wissens über Kommandos; also die Auswertung
    # der Syntax, die beim Aufbau geliefert wird (das gehört nach add_command()
    # oder so ähnlich.

    given_commands = []
    available_commands = {}    # dito??        #??#
    index = []              # index for fast access to given_commands
                            #   #??# das doppelt führen (index und given_commands) ist fehlerträchtig
    current_command = None

    def __init__(self, commands=None):
        """#??# commands ist ein Liste [(cmd,[argumente])]"""
        if commands is not None:
            for cmd, args in commands:
                c = ClCommand(cmd,args)
                self.given_commands.append((cmd,c))
                self.index.append(cmd)
                setattr(self, cmd, c)
        return

    def add_command(self, cmd, args):
        """#??# cmd : string   args : [string]
        das ist jetzt ein gefundenes Kommando
        """
        c = ClCommand(cmd,args)
        self.given_commands.append((cmd,c))
        self.index.append(cmd)
        setattr(self, cmd, c)

    def add_command_to_list(self, command):
        """#??# command ist eine Instanz von Command"""
        self.available_commands[command.name] = command

    def commands(self,):
        return self.index

    def get_args(self, cmd):
        """returns the list of arguments for a given command 'cmd'"""
        idx = self.index.index(cmd)     # beware of ValueError   #??#
        cmd = self.given_commands[idx][1]
        return cmd.get_arg_list()

    def pop_command(self,):
        """Renders the next command to execute, beginning with the first.
        First call to pop_command results in a copy of given_commands
        """
        if self.current_command is None:
            self.current_command = 0
        if self.current_command == len(self.given_commands):
            return None, None        #??#  das Verhalten find ich noch nicht so gut
       # print self.given_commands, self.current_command
        cmd, c = self.given_commands[self.current_command]
        self.current_command += 1
        return (cmd, c.get_arg_list())

    def get_list_of_commands(self,):
        """#??# damit sind die generell verfügbaren Kommandos gemeint"""
        return self.available_commands.keys()

    def reset_command_list(self,):
        """#??# command ist eine Instanz von Command"""
        self.given_commands = []
        self.index = []
        self.current_command = None

class CommandParser:
    """baut einen Parser für Commands in positional Arguments auf.
    Beim Instanziieren kann ein bereits existierendes Dict von Kommandos
    direkt übergeben werden
    """
    def __init__(self,commands={}):
        self.commands = Commands(commands)
        return

    def add_command(self, name='', args=[]):
        self.commands.add_command_to_list(Command(name,args))
        return

    def check_command(self, cmd, args):
        """#??# Baut das eigentliche gefundene Kommando zusammen"""
        self.commands.add_command(cmd, args)
        return []

    def parse_args(self,positional_args):
        """
        parse_args(positional_args : [string] = args,
#??#                   values : Values = None)
#??#        -> (values : Commands, args : [string])

        Parse the positional arguments found in 'args' (no default
        possible) after parsing the commandline with OptParse.
#??#        Any errors result in a call to 'error()', which
#??#        by default prints the usage message to stderr and calls
#??#        sys.exit() with an error message.  On success returns a pair
#??#        (values, args) where 'values' is an Values instance (with all
#??#        your option values) and 'args' is the list of arguments left
#??#        over after parsing options.
        """
        left_overs = []
        if len(positional_args) < 1:    # no parsing done when list is empty
            return self.commands, left_overs
        existing_commands = self.command_list()
        pargs = positional_args[:]      # don't modify caller's list
        
        # Iterate one pass through positional_args.
        # Up to the first command, elements are considered left_overs.
        # If a command is met, cur_cmd is set to this command (initial
        # value is '').
        # Up to then next command, all elements are considered args.
        # Commands and their args are checked and stored when
        #   - a new command is found, and when
        #   - the iteration is finished.
        # The checking method also does type-conversion.
        # The check may result in an exception.
        
        cur_cmd = ''
        for pa in pargs:
            if pa in existing_commands:
                if cur_cmd:
                    lo = self.check_command(cur_cmd,args)
                    if lo: left_overs.append(lo)
                cur_cmd = pa
                args = []
            elif cur_cmd:
                args.append(pa)
            else:
                left_overs.append(pa)
                
        if cur_cmd:
            lo = self.check_command(cur_cmd,args)
            if lo: left_overs.append(lo)
        return self.commands, left_overs

    def get_args(self, cmd):
        return self.commands[cmd]

    def reset(self,):
        """#??# public"""
        self.commands.reset_command_list()

    def command_list(self,):
        return self.commands.get_list_of_commands()

def test(parser,tc):
    for e,t in enumerate(tc):
        print '-'*50, e + 1
        print 'Zeile:',t
        parser.reset()
        commands, left_over = parser.parse_args(t)
        # Bei dem folgenden Verfahren gibt es einen Fehler:
        #   bei Doppeltnennungen wird in Commands.get_args() u.U. der falsche
        #   Index ermittelt. Das passiert hier im 4. Testfall
##        for c in commands.commands():
##            print "Command ('%s', %s)" % (c,str(commands.get_args(c)))
        cmd, args = commands.pop_command()
        while cmd:
            print "Command ('%s', %s)" % (cmd,str(args))        
            cmd, args = commands.pop_command()
        if left_over:
            print 'Left over',left_over
    return
    
if __name__ == "__main__":
    #print 'Version:',__version__
    parser = CommandParser()
    cmds = {
        'start': [('instance',True,'string',''),],
        'stop': [('instance',True,'string',''),],
        'show': [('instance',True,'string',''),],
        }
    for c in cmds.keys():
        parser.add_command(c,cmds[c])
    test_cases = [
        ['start',],
        ['start','xxx','ste',],
        ['start','xxx','show','stop',],
        ['---',
         'start','xxx',
         'show','xxx','yyy','zzz',
         'stop',
         'start','aaa','bbb','ccc',
         'stop','xxx',
         'show',],
        # nun systematisch
        [],                                 # 0
        ['start',],                         # 1       cmd
        ['---',],                           # 1     nocmd
        ['start','stop',],                  # 2       cmd   cmd
        ['start','----',],                  # 2       cmd nocmd
        ['-----','stop',],                  # 2     nocmd   cmd
        ['-----','yyyy',],                  # 2     nocmd nocmd
        ['start','stop','show',],           # 3       cmd   cmd   cmd
        ['start','stop','----',],           # 3       cmd   cmd nocmd
        ['start','----','show',],           # 3       cmd nocmd   cmd
        ['start','----','yyyy',],           # 3       cmd nocmd nocmd
        ['xxxxx','stop','show',],           # 3     nocmd   cmd   cmd
        ['xxxxx','stop','----',],           # 3     nocmd   cmd nocmd
        ['xxxxx','----','show',],           # 3     nocmd nocmd   cmd
        ['xxxxx','----','yyyy',],           # 3     nocmd nocmd nocmd
        ]
    test(parser,test_cases)
