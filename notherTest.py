#!/usr/bin/python
# -*- coding: utf-8 -*-

# hier is ein ä

"""Hier wird nur ein bisschen gespielt.
Hauptsaechlich soll die Arbeit mit Kate ausprobiert werden."""

import sys
import os
import getopt

def main():
    print os.getcwd()
    os.chdir('Test')
    print os.getcwd()

    print sys.argv
    print os.path.abspath(sys.argv[0])
    print 'before try'

    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hu:d:s:",
            ["help", "user=", "dir=", "skelsrc="]
            )
    except getopt.GetoptError, msg:
        usage(sys.stderr, msg)
        sys.exit(2)

    print 'opts',opts
    print 'args',args

##    for opt, arg in opts:
##        print opt,'hep',arg
##
    for opt, arg in opts:
        if opt in ("-d", "--dir"):
            skeltarget = os.path.expanduser(arg)
            if not skeltarget:
                usage(sys.stderr, "dir must not be empty")
                sys.exit(2)
            print 'skeltarget',skeltarget
        if opt in ("-s", "--skelsrc"):
            skelsrc = os.path.abspath(os.path.expanduser(arg))
            if not skelsrc:
                usage(sys.stderr, "skelsrc must not be empty")
                sys.exit(2)
            print 'skelsrc',skelsrc
        if opt in ("-h", "--help"):
            usage(sys.stdout)
            sys.exit()
        if opt in ("-u", "--user"):
            if not arg:
                usage(sys.stderr, "user must not be empty")
                sys.exit(2)
            if not ":" in arg:
                usage(sys.stderr, "user must be specified as name:password")
                sys.exit(2)
            user, password = arg.split(":", 1)

    import pwd
    print pwd.getpwnam('hausmann')
    print 'eins zwei drei'
    print 'done all main()'

def usage(stream, msg=None):
    if msg:
        print >>stream, msg
        print >>stream
    program = os.path.basename(sys.argv[0])
    print >>stream, __doc__ % {"program": program}

if __name__ == '__main__':
    main()
