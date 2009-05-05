#!/usr/bin/python
# -*- coding: utf-8 -*-
"""teste Argumente von der Befehlszeile


(c) 10/2005 Andreas Hausmann
"""

from optparse import OptionParser

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    print "options",options
    print "args",args

