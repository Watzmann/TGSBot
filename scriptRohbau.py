"""Lexisnexis Dokumente in individuelle Dokumente aufteilen.

Die individuellen Dokumente werden fuer den Import durch
brainFiler aufbereitet.

(c) Feb 2005               Pylon AG  Dr. Andreas Hausmann
"""

import getopt, sys

_OPTION = "how:v"
_LONG_OPT = ["help", "outputpath=", "workingpath="]

nrDocuments = 0

def usage():
    print __doc__
    print """
    usage:    %s [%s] <fileName>

       -h     help
       -o:    outputpath
                Pfad, in den die Zieldokumente geschrieben werden.
                Default ist current working directory
       -w:    workingpath
                Pfad, in dem das/die Lexisnexis-Dokument liegt
""" % (sys.argv[0],_OPTION)
    print """
  example:    %s -o ..\\brainFiler\\LexisNexis alexander_falk_.txt
""" % (sys.argv[0])

def parse_cl():
    try:
        opts, args = getopt.getopt(sys.argv[1:], _OPTION, _LONG_OPT)
        print '>>',opts
        print '>>',args
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)
    global output, verbose
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
            print __doc__
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-o", "--outputpath"):
            output = a

    # pruefe auf mindestens ein Argument
    if len(args) < 1:
        usage()
        print """Es wurden keine Dokumente angegeben!
%d Dokumente verarbeitet.
""" % nrDocuments
        sys.exit()

def main():
    parse_cl()

if __name__ == "__main__":
    main()
    print 'verbose:', verbose

