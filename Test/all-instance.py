#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  bietet Übersicht über alle auf einem System vorhandenen Zope-Instanzen;
  Ausgabe von Namen, Ports, Status, Plone-Instanzen, debug-status,
  effective-user, Zope- und Plone-Version, ...
"""

## TODO                         7 Lines
#
# 1) restart als Command
# 2) Instanzen an ZEO werden nicht angezeigt, weil sie kein Data.fs haben
#

# Konfiguration
#
# hier werden rechner-abhängige Variablen konfiguriert
#
STANDARD_ROOTS = ('/var/opt/zope', '/var/opt2/zopealt',
                  '/var/opt/develop_zope', '/var/opt/extern_zope',
                  '/var/opt/referenz_zope', '/var/opt/intern_zope',
                  )

import sys, os
from optparse import OptionParser
import testZopeEtc


# Konfiguration
#
# hier werden rechner-abhängige Variablen konfiguriert
#
FMT_INSTANCE = '%16s'

class Instance:
    standardRootInstance = STANDARD_ROOTS
    standardConf = 'etc/zope.conf'
    semaphore = 'var/zopectlsock'
    cols = [16,8,]
    fmt = '%3s' + FMT_INSTANCE + '%18s   %s'
    head = fmt % ('','Instanz','root','Ports',)
    def __init__(self, path):
        self.path = path
        self.name,self.root = self.instName(path)
        self.conf = os.path.join(path,self.standardConf)
        self.read_ports(self.conf)
        self.running()
        return
    def instName(self, path):
        """split 'path' in 'root' and 'name' and check 'root'
against standard names"""
        root,name = os.path.split(path.rstrip('/'))
        if not root in self.standardRootInstance:
            print '!!!Warning! Strange root-instance',root
        return name,root
    def read_ports(self, conf):
        self.ports = {}
        if os.path.exists(conf):
            self.ports = testZopeEtc.ZopeConf(conf).versuch()
        else:
            print 'unlautere Instanz (=conf fehlt)', self.path
        return
    def running(self):
        status = {True:'x',False:''}
        sp = os.path.join(self.path,self.semaphore)
        self.is_up = status[os.path.exists(sp)]
        return
    def fmtOutput(self):
        ports = self.ports.values()
        ports = '%6s '*len(ports) % tuple(ports)
        return self.fmt % (self.is_up,self.name,self.root,ports)

class Instances:
    def __init__(self,instances=None):
        if instances:
            self.instances = instances
        else:
            self.instances = self.readInstances()
        return

    def readInstances(self,):
        """create a list of instances"""
        # read a list of candidates by locate-command
        liste = []
        p = os.popen("locate var/Data.fs|grep -v windows|grep 'fs$'")
        liste = [l.strip('\n') for l in p.readlines()]
        # cut of the tail; retain the path of the instance
        ende = 'var/Data.fs'
        le = len(ende)
        instances = []
        for p in liste:
            if not p.endswith(ende):
                print '!!!Warning! Strange instance not included:',p
            else:
                instances.append(Instance(p[:-le]))
        return instances

    def subset(self, choice):
        instances = self.instances
        criterion = lambda i: i.name in choice
        if choice and choice[0].startswith('^'):
            choice[0] = choice[0][1:]
            criterion = lambda i: i.name not in choice
        if not choice:
            criterion = lambda i: True
        self.chosenSet = filter(criterion, self.instances)
        return 

    def filterRunning(self, operator):
        operands = self.chosenSet
        if operator == self.START_INSTANCE:
            operands = filter(lambda i: i.is_up != 'x', operands)
        if operator == self.RESTART_INSTANCE:
            operands = filter(lambda i: i.is_up == 'x', operands)
        if operator == self.STOP_INSTANCE:
            operands = filter(lambda i: i.is_up == 'x', operands)
##        operands_names = map(lambda i: i.name, operands)
##        print operands_names
        self.chosenSet = operands
        return

    def doit(self, which, command, fkt):
        self.subset(which)
        self.filterRunning(fkt)
        for i in self.chosenSet:
            cmd = i.path+'bin/zopectl ' + command
            fmt = FMT_INSTANCE + '  %s'
            print fmt % (i.name,cmd)
            if options.test: continue
            try:
                p = os.popen(cmd)
                i.is_up = 'x'
                print p.read()
                p.close
            except:
                print 'hat nicht funktioniert'
        return

    START_INSTANCE = 'start'
    def startInstances(self, which):
        """starte alle (oder angegebene) Instanzen"""
        self.doit(which, 'start', self.START_INSTANCE)
        return

    RESTART_INSTANCE = 'restart'
    def restartInstances(self, which):
        """restarte alle (oder angegebene) Instanzen"""
        self.doit(which, 'restart', self.RESTART_INSTANCE)
        return

    STOP_INSTANCE = 'stop'
    def stopInstances(self, which):
        """stoppe alle laufenden (oder angegebene) Instanzen"""
        self.doit(which, 'stop', self.STOP_INSTANCE)
        return

    SHOW_INSTANCE = 'show'
    def showInstances(self, which):
        """Ausdruck aller vorhandenen Instanzen [default]"""
        print Instance.head
        self.subset(which)
        for l in self.chosenSet:
            print l.fmtOutput()
        return

    def do(self, command, on_instances):
        self.COMMANDS[command](self, on_instances)
        return

    COMMANDS = {
        START_INSTANCE: startInstances,
        RESTART_INSTANCE: restartInstances,
        STOP_INSTANCE:  stopInstances,    
        SHOW_INSTANCE:  showInstances,    
        }

    def commands(self,):
        return self.COMMANDS.keys()

    def usage_commands(self,):
        usg = '<command>:'
        for c in self.commands():
            usg += "\n  %8s:\t%s" % (c, self.COMMANDS[c].__doc__)
        return usg

def instances_commands():
    leer = Instances(['dummy',])
    return leer.usage_commands()

def command_args(cmd_line_args, command, commands):
    """return list of comma separated arguments to a specific command"""
    idx = cmd_line_args.index(command)
    #print args, command, idx
    myargs = ""
    if len(cmd_line_args) > idx+1 and cmd_line_args[idx+1] not in commands:
        myargs = cmd_line_args.pop(idx+1)
    if myargs:
        myargs = myargs.split(',')
    else:
        myargs = []
    return myargs

def usage():
    usg = """usage: %prog [<command>]
""" + __doc__ + '\n'
    usg += instances_commands()
    parser = OptionParser(usg)
##    parser.add_option("-v", "--verbose",
##                  action="store_true", dest="verbose", default=False,
##                  help="print status messages to stdout")
    parser.add_option("-t", "--test",
                  action="store_true", dest="test", default=False,
                  help="fake mode: only show, don't execute other operations")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    test_mode = ''  # string für die Ausgabe in der '----executing'-Zeile
    if options.test:
        test_mode = ' (nur Test-Mode!)'
    inst = Instances()
    for command in args:
        if command not in inst.commands():
            print 'command',command,'doesn\'t exist'
            continue
        else:
            chosenInstances = command_args(args, command, inst.commands())
            print '------- executing %s(%s)' % (command,chosenInstances), \
                                                test_mode
            inst.do(command,chosenInstances)
    if not len(args):
        inst.showInstances([])
