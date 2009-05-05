#!/usr/bin/python
# -*- coding: utf-8 -*-
"""  stellt eine Reihe von Routinen zum Umbenennen von Image-Dateien
  zur Verfügung. Nicht Image-Dateien (Mime-Type) werden ignoriert."""

__svn_date__ = "$Date: 2007-02-07 09:01:48 +0100 (Mi, 07 Feb 2007) $"
__version__ = "$Revision: 62 $"[11:-2]
__svn_url__ = "$Url$"
__release__ = "0.5" # @ rev 50

__TODO__="""Liste der Todos:
  - UI und Kommentare auf rein Englisch umstellen;
  - Unittest exemplarisch einrichten;
"""

import sys
import os
import shutil
from optparse import OptionParser
from mimetypes import guess_type
import re

from cmdparse import CommandParser

def commandUsage():
    ret = ''
    for i in COMMANDS.keys():
        ret += '\n' + COMMANDS[i][0].__doc__ % i
    return ret

def push_commands():
    parser = CommandParser()
    for i in COMMANDS.keys():
        parser.add_command(i,COMMANDS[i][1])
    return parser

def version(progname):
    print "%s, v%s (rev%s)" % (progname,__release__,__version__)
    if options.verbose:
        print __svn_date__
        print __svn_url__
        print __TODO__
    sys.exit(0)

def usage(progname):
    usg = """usage: %s [options] <command> [args]
%s""" % (progname,__doc__)
    usg += "\n\ncommands:" + commandUsage()
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-V", "--version",
                  action="store_true", dest="version", default=False,
                  help="print version information and exit")
    parser.add_option("-t", "--test",
                  action="store_true", dest="test", default=False,
                  help="do not change anything (just check)")
    return parser,usg

def addPrefix(prefix):
    """      %-11s<prefix>
                 benennt alle Dateien im aktuellen Verzeichnis um; hängt
                 <prefix> vorne dran."""
    liste = os.listdir('.')
    for fn in liste:
        mt = guess_type(fn)
        #print 'Mimetype:',mt
        if 'image' in mt[0]:
            j = prefix + fn
            print fn,'->',j
            if not options.test:
                os.rename(fn,j)
    return

def addRunning(filename, nrstring):
    """      %-11s<filename> <nr>
                 nimmt die Datei <filename> und kopiert sie in <nr> neue.
                 Schema: dokument_01.tif und zusätzlich
                 dokument_010001.tif ... dokument_01<nr>.tif"""
    nr = int(nrstring)
    for l in range(1,nr+1):
        a = os.path.splitext(filename)
        j = '%s%4.4d%s' % (a[0],l,a[1])
        print filename,'->',j
        if not options.test:
            shutil.copyfile(filename,j)
    return

def rnrCollapse(filename):
    """      %-11snummeriert ein Schema dokument_01.tif dokument_010001.tif
                 dokument_010002.tif ...
                 neu: dokument_01.tif dokument_02.tif dokument_03.tif ...
                 <filename>:=:dokument_01.tif"""
    # #??# return, if <filename> doesn't exist
    
    # create list of files in cwd; <filename> is excluded
    liste = os.listdir('.')
    if filename in liste:
        liste.remove(filename)
    liste.sort()

    # find number (sequence of digits) at the end of 'dok'
    # and set variables, necessary for formating
    dok = os.path.splitext(filename)
    len_dok = len(dok[0])
    mo = re.search('[0-9]*$',dok[0])
    index = mo.start()
    try:
        start_number = int(dok[0][index:])
        name_base = dok[0][:index]
        nr_fmt = '%0' + str(len_dok-index) + '.d'
    except:
        start_number = 1
        name_base = dok[0]
        nr_fmt = '%02.d'
        os.rename(filename,'%s%02.d%s'%(name_base,1,dok[1]))
##        print filename,"ist nicht im Format 'dokument_01.*'!"
##        print '0 Dateien umbenannt'
##        return
    #print 'dok', dok, name_base, start_number, nr_fmt

    # process list of files; files that match pattern are renamed
    nr_renamed = 0
    for src in liste:
        name, ext = os.path.splitext(src)
        if not name.startswith(dok[0]):
            continue
        nr = name[len_dok:]
        try:
            decimal = int(nr)
        except ValueError:
            if options.verbose:
                print src, "doesn't match pattern"
            continue
        dest =  name_base + nr_fmt % (decimal + start_number,) + ext
        try:
            os.rename(src,dest)
            nr_renamed += 1
            if options.verbose:
                print src,'->',dest
        except:
            print "couldn't rename", src
    print nr_renamed, 'Dateien umbenannt'
    return

COMMANDS = {
    'prefix':(addPrefix,[('prefix',False,'string',''),]),
    'running':(addRunning,[('filename',False,'string',''),
                           ('nrstring',False,'int',10),]),
    'collapse':(rnrCollapse,[('filename',False,'string',''),]),
    }  # übergib ihm auch die Funktion, die ausgeführt werden soll

##def doit(command,arg):
##    liste = os.listdir('.')
##    for i in liste:
##        mt = guess_type(i)
##        #print 'Mimetype:',mt
##        if 'image' in mt[0]:
##            command(i,arg)
##    return
##
if __name__ == "__main__":
    parser,usg = usage(os.path.basename(sys.argv[0]))
    (options, args) = parser.parse_args()
    if options.version:
        version(os.path.basename(sys.argv[0]))
    if len(args) < 1:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    if options.verbose:
        print options,args
    #sys.exit(0)
    cmdParser = push_commands()
    commands, left_over = cmdParser.parse_args(args)
    if left_over:
        print "Argumente übrig!!!!", left_over
    cmd, cargs = commands.pop_command()
    while cmd:
        print "%s(%s)" % (cmd,str(cargs))
        COMMANDS[cmd][0](*cargs)
        cmd, cargs = commands.pop_command()
    if left_over:
        print 'Left over',left_over
