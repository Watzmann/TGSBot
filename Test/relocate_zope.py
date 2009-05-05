#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""relocate_zope unterstützt bei unterschiedlichen 'Verschiebungs-Operationen'
von Zope-Instanzen:
"""

## Todo:
#
# 1) Unicode Fehler bei Aufruf relocate... -h auf jupiter
# 2) bei rename: INSTANCE in zope.conf wird nicht korrekt gesetzt
#
#


import sys
import os
from optparse import OptionParser

class ScriptFile:

    def __init__(self, path):
        self.path = path
        f = open(path,)
        self.text = f.read() #.splitlines()
        f.close()
        return

    def replace(self, old, new):
        self.text = self.text.replace(old, new)
        return

    def write_file(self,):
        path = self.path
        if options.test:
            path += '.neu'
        f = open(path,'w')
        f.writelines(self.text)
        f.close()
        return
    
    def print_file(self,):
        print self.text
##        for l in self.text:
##            print l

class Instance:
    def __init__(self,path="",instance=None):
        self.instance = {'files':{},'path':path}
        if instance:
            self.instance = instance
        else:
            self.readInstance()
        return

    def read_file(self,name,path):
        full_path = os.path.join(path,name)
        self.instance['files'][name] = s = ScriptFile(full_path)
        if options.verbose:
            print 'reading', full_path
        return
        
    def readInstance(self,):
        """gather information about instance"""
        # read runzope and zopectl
        path = os.path.join(self.instance['path'],'bin')
        self.read_file('runzope',path)
        self.read_file('zopectl',path)
        path = os.path.join(self.instance['path'],'etc')
        self.read_file('zope.conf',path)
        return

    RENAME_INSTANCE = 'rename'
    def rename_instance(self, which):
        """Instanz umbenennen (z.B. von "ste-devel" nach "ste-old")"""
        self.process_files(['runzope','zopectl','zope.conf'], which)
        return

    MOVE_PORTS = 'ports'
    def move_ports(self, which):
        u"""setze alle geöffneten Ports auf neuen Wert
                (z.B. "17380" auf "17480")"""
        w = tuple(which)
        if options.verbose:
             print 'setting ports','(%s -> %s)' % w
        print 'move ports ist noch nicht implementiert'
        return

    MOVE_ZOPE = 'zope'
    def move_zope(self, which):
        """setze auf eine neue Zope-Installation um
                (z.B. "/opt/zope" auf "/opt/zope81")"""
        self.process_files(['runzope','zopectl','zope.conf'], which)
        print '!'*10,'ACHTUNG', '!'*10
        print 'zu kurz gesprungen: /opt/zope kommt auch in /var/opt/zope vor'
        print '!'*10,'ACHTUNG', '!'*10
        return

    def process_files(self, pfiles, which):
        files = self.instance['files']
        src,dest = which
        for k in pfiles:
            if not files.has_key(k):
                continue
            f = files[k]
            if options.verbose:
                 print 'processing',f.path,'(%s -> %s)' % (src,dest)
            f.replace(src,dest)
            #f.print_file()
            f.write_file()
        return

    SHOW_INSTANCE = 'show'
    def show_instance(self, which):
        """Zusammenfassung der Daten dieser Instanz ausgeben"""
        print Instance.head
        self.subset(which)
        for l in self.chosenSet:
            print l.fmtOutput()
        return

    def do(self, command, on_instances):
        self.COMMANDS[command](self, on_instances)
        return

    COMMANDS = {
        RENAME_INSTANCE:    rename_instance,
        MOVE_PORTS:         move_ports,
        MOVE_ZOPE:          move_zope,
        SHOW_INSTANCE:      show_instance,    
        }

    def commands(self,):
        return self.COMMANDS.keys()

    def usage_commands(self,):
        usg = '<command>:'
        for c in self.commands():
            usg += "\n  %8s:\t%s" % (c, self.COMMANDS[c].__doc__)
        return usg

def instances_commands():
    leer = Instance('',['dummy',])
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

def usage(progname):
    usg = """usage: %prog <instance> [<commands>]
    ports <port-alt>,<port-neu>
    zope <zope-alt>,<zope-neu>
    rename <instance-alt>,<instance-neu>
""" + __doc__ + '\n'
    usg += instances_commands()
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-t", "--test",
                  action="store_true", dest="test", default=False,
                  help="fake mode: only show, don't execute other operations")
    return parser,usg

if __name__ == "__main__":

    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()

    test_mode = ''  # string für die Ausgabe in der '----executing'-Zeile
    if options.test:
        test_mode = ' (nur Test-Mode!)'

    if options.verbose:
        print options,args

    if len(args) < 1:
        print usg
        print "!! Keine Instanz angegeben"
        sys.exit(1)

    inst = Instance(args[0],)

    rest = args[1:]
    for command in rest:
        if command not in inst.commands():
            print 'command',command,'doesn\'t exist'
            continue
        else:
            chosenInstances = command_args(rest, command, inst.commands())
            if options.verbose:
                print '------- executing %s(%s)' % (command,chosenInstances), \
                                                test_mode
            inst.do(command,chosenInstances)
