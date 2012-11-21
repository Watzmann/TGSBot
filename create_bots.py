#!/usr/bin/env python
"""Create a command-file for use of bulk registering bots with tgs.

  Output is a command-file-structure like
      register_user <prefix>I <password>
      set_field <prefix>I special bot
      register_user <prefix>II <password>
      set_field <prefix>II special bot
"""

import sys
from optparse import OptionParser

def int2roman(number):
    numerals = { 1 : "I", 4 : "IV", 5 : "V", 9 : "IX", 10 : "X", 40 : "XL",
                50 : "L", 90 : "XC", 100 : "C", 400 : "CD", 500 : "D",
               900 : "CM", 1000 : "M" }
    result = ""
    for value, numeral in sorted(numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result

def create_entry(prefix, n, password, output):
    bot = '%s%s' % (prefix, int2roman(n))
    output.write('register_user %s %s\n' % (bot, password))
    output.write('set_field %s special bot\n' % bot)

def usage(progname):
    usg = """usage: %prog <prefix> <passwd>
  %prog """ + __doc__
    parser = OptionParser(usg)
    #parser.add_option("-v", "--verbose",
                  #action="store_true", dest="verbose", default=False,
                  #help="print full entries to stdout")
    parser.add_option("-o", "--output",
                  action="store", dest="output",
                  help="output to file (command-file).")
    parser.add_option("-c", "--count", default=200, type='int',
                  action="store", dest="count",
                  help="register <count> bots. (200)")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()

    if len(args) < 2:
        print 'ERROR: argument <passwd> and maybe <prefix> is missing.'
        sys.exit(1)

    prefix = args[0]
    password = args[1]

    if not options.output is None:
        output = open(options.output, 'w+')
    else:
        output = sys.stdout

    for n in range(options.count):
        create_entry(prefix, n+1, password, output)

    if not options.output is None:
        output.close()
