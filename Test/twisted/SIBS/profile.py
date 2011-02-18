#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool for evaluation of SIBS-profiling information."""

import sys
import math
from optparse import OptionParser
from listen import Liste
from el_listen import Line

class Profile(Liste):
    identifier = 'time used for'
    
    def my_filter(self, **kw):
        return [entry for entry in self._raw_liste \
                                if entry.find(self.identifier) != -1]

    def list2hash(self,):
        self.dliste = {}
        for i in self.pliste:
            pk = i.primary_key()
            if self.dliste.has_key(pk):
                self.dliste[pk]['raw'].append(i)
            else:
                self.dliste[pk] = {'raw': [i,]}
        return self.dliste

    def averages(self,):
        for d in self.dliste:
            nr = len(self.dliste[d]['raw'])
            sum_used = reduce(lambda x,y: x + y.interpreted_line['used'],
                              self.dliste[d]['raw'], 0.0)
            self.dliste[d]['sum_used'] = sum_used
            self.dliste[d]['avg_used'] = sum_used/nr

            mini = maxi = sdiff = .0
            for u in self.dliste[d]['raw']:
                mini = min(mini, u.used)
                maxi = min(maxi, u.used)
                diff = u.used - sum_used
                sdiff = sdiff + diff*diff
            self.dliste[d]['mean_used'] = math.sqrt(sdiff)/nr

class LogEntry(Line):
    
    delimiter = ' '
    interpretation = ['date',
                      'time',
                      'client',
                      'token1', 'token2', 'token3',
                      'command',
                      'used',
                      'token4',
                      'nr_users',
                      'token5',
                      ]
    key = 'command'

    def __repr__(self,):
        return '%(command)s: %(used).6f (%(nr_users)d users) (%(time)s)' \
                                                               % self.__dict__

    def process(self,):
        self.interpreted_line["used"] = float(self.used)
        self.interpreted_line["nr_users"] = int(self.nr_users.lstrip('('))
        self.interpreted_line["command"] = self.command.rstrip(':')
        for i in self.interpretation:
            setattr(self, i, self.interpreted_line[i])

def usage(progname):
    usg = """usage: %prog [<logfile>]
  %prog """ + __doc__ + """

  If <logfile> is not give, stdin is read."""
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print full entries to stdout")
    parser.add_option("-a", "--average",
                  action="store_true", dest="average", default=False,
                  help="print average values to stdout")
    parser.add_option("-s", "--show_command",
                  action="store", dest="show_command", default='',
                  help="show data for command (comma separated list)")
    return parser,usg

if __name__ == '__main__':
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        logfile = args[0]
    else:
        logfile = '-'

    profile = Profile(logfile)
    #profile.print_lines(end=20)
    print 'len(profile) =', len(profile)
    profile.interpret(LogEntry)
    profile.process()
    profile.list2hash()
    print profile.dliste.keys()
    profile.averages()
##    print profile.pliste[0].__dict__
    for p in profile.dliste:
        print '%10s %2d (%10.3f)%8.3f  +-%8.3f' % \
                                  (p, len(profile.dliste[p]['raw']),
                                    profile.dliste[p]['sum_used']*1000.,
                                    profile.dliste[p]['avg_used']*1000.,
                                    profile.dliste[p]['mean_used']*1000.,
                                          )
    if options.show_command:
        cmd_list = options.show_command.split(',')
        for c in cmd_list:
            if not c in profile.dliste:
                print c, 'does not exist'
                continue
            data = profile.dliste[c]['raw']
            print 'data for', c
            for d in data:
                print d
            
