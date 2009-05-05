#!/usr/bin/python
# -*- coding: utf-8 -*-
"""resize.py changes sizes of images. It is best suited for
processing in batch-manner. One major application of resize.py is
production of thumbnails on large sets of images for use in HTML-
pages.
Globbing is used, so quote {files} with ''.
Uses PIL.Image.

(c) 2005 Andreas Hausmann
"""

__svn_date__ = "$Date: 2007-03-08 18:43:07 +0100 (Do, 08 Mär 2007) $"
__version__ = "$Revision: 83 $"[11:-2]
__svn_url__ = "$URL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/Image/resize.py $"


"""Todos:
- Commandline
- --test modus
- --in/outputpath
- different resizing modes
- resize selbst als Klasse (resize.save())
"""

import Image
import os, os.path
import sys
import glob
from cmdparse import CommandParser

FACTOR = 100.

def commandUsage():
    ret = 'commands:'
    for i in COMMANDS.keys():
        ret += '\n' + COMMANDS[i][0].__doc__ % i
    return ret

def push_commands():
    parser = CommandParser()
    for i in COMMANDS.keys():
        parser.add_command(i,COMMANDS[i][1])
    return parser

def getOutPath(path, preserve=True):
    if preserve:
        start = path
        i = 1
        while os.path.exists(path):
            path = start + '-%03d' % i
            i += 1
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def special(image,fc=FACTOR):
    """      %-11s'<filenames>' [<new height>]
                 convert images to mode '1'
                 half height preserving aspect;
                 output is directed to ./special
    """
    a0,a1 = image.size
    b=(int(a0/2),int(a1/2))
    j=image.resize(b).convert('1')
    return j

def mode(image,new_mode):
    """      %-11s'<filenames> [<new mode>]'
                 convert images to given mode;
                 output is directed to ./mode
    """
    #print 'in mode',image,new_mode
    j=image.convert(new_mode)
    #print 'converted to',new_mode
    return j

def resize(image,fc):
    """      %-11s'<filenames>' [<new height>]
                 resize images to new height preserving aspect;
                 output is directed to ./resize[-iii]
    """
    fc = float(fc)
    a0,a1 = image.size
    f = fc/a1
    b=(int(f*a0),int(f*a1))
    j=image.resize(b)
    return j

def rotate(image,qu='180'):
    """      %-11s'<filenames>' [{90|180|270}]
                 rotate images clockwise;
                 output is directed to ./rotate
    """
    print qu
    if qu in ('90','180','270'):
        ro = eval('Image.ROTATE_%s' % qu)
    j=image.transpose(ro)
    return j

def usage(progname):
    print progname,"[-f:] '{files}'"
    print __doc__
    print commandUsage()

COMMANDS = {
    # entries look like this:
    #   'cmd_name':(<cmd_fct>,<cmd_argument according to cmdparse>,
    #                                           <flag: preserve folder>)
    'special':(special,[('filename',False,'string',''),
                           ('height',True,'float',FACTOR),],False),
    'mode':(mode,[('filename',False,'string',''),
                           ('mode',False,'string','1'),],False),
    'resize':(resize,[('filename',False,'string',''),
                           ('height',True,'float',FACTOR),],True),
    'rotate':(rotate,[('filename',False,'string',''),
                           ('quarters',True,'string','180'),],False),
    }  # übergib ihm auch die Funktion, die ausgeführt werden soll

if __name__ == '__main__':
    args = sys.argv[1:]

    # usage
    if len(args) < 1 or args[0] == '-h' or args[0] == '--help':
        usage(os.path.basename(sys.argv[0]))
        sys.exit()
    
    cmdParser = push_commands()
    commands, left_over = cmdParser.parse_args(args)
    if left_over:
        print "Argumente übrig!!!!", left_over

    cmd, cargs = commands.pop_command()
    while cmd:
        # create output path (existing paths are preserved)
        outP = getOutPath('./'+cmd, preserve=COMMANDS[cmd][2])
        fileI = cargs.pop(0)
        for fileName in glob.glob(fileI):
            # compose output file name
            outFile = os.path.basename(fileName)
            out = os.path.join(outP,outFile)
            #print cargs,fargs
            if os.path.exists(fileName):
                try:
                    cnt = 0
                    image = Image.open(fileName)
                    cnt = 1
                    #print 'cargs',cargs
                    little = COMMANDS[cmd][0](image,*cargs)
                    cnt = 2
                    little.save(out)
                    print '==>', out
                except:
                    print sys.exc_info()[0]
                    print "Can't proceed %s (%d)" % (fileName,cnt)
            else:
                print "Can't find", fileName
                continue
        cmd, cargs = commands.pop_command()

