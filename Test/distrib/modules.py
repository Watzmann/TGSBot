#!/usr/bin/python
# -*- coding: utf-8 -*-
"""testet die Aspekte von Programmierung mit Modulen und Distribution"""

import sys
from optparse import OptionParser

import mymodule
import Mypackage
#import Mypackage.test2

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 0:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    print __doc__
    separator = '-'*50
    print separator, 'jetzt die Tests'
    mymodule.usage()
    klasse = mymodule.Klasse()
    klasse.tuwas('das Importieren geht')
    print dir(Mypackage)
    print Mypackage.__path__
    print Mypackage.comment1
    test = Mypackage.test1.Test1()
    data = test
    test = Mypackage.test2.Test2()
    print separator, 'Ende der Tests'
    print separator, 'Test von Data'
    data.tables()
    data.spoons()
    print separator, 'Ende der Tests'
