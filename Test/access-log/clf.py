#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Classes for inspecting access files according to common log format"""

import sys
import re

class CommonLogFormat:
    ip = re.compile(r'^(\d{1,3}\.){3}(\d{1,3}) ')
    ts = re.compile(r'\[.{26}\]')
    keys = ('line_number', 'host', 'rfc931', 'authuser', 'time',
            'request', 'status', 'size',)
    fmt_line = '%(line_number)3d: %(host)16s %(time)s %(status)s %(request)s'
    xfmt_line = '%(line_number)3d: %(authuser)s %(host)16s %(time)s %(status)s %(request)s'
    
    def __init__(self, fname):
        f = open(fname)
        l = f.read().splitlines()
        f.close()
        if options.verbose and False:
            print len(l), 'Zeilen gelesen'
        li = []
        for e,i in enumerate(l):
            line = self.parse_line(i, e)
            li.append(line)
        self.lines = li

    def parse_line(self, line, line_number):
        ipm = self.ip.search(line)
        s,e = ipm.span()
        rest = line[e:].split()
        ip = ipm.string[s:e-1]
        time = ' '.join(rest[2:4])
        a2rest = rest.pop()
        a2code = rest.pop()
        rest = ' '.join(rest[4:])
        #print ip, time, '##', a2code, a2rest, '##', rest
        values = (line_number, ip, time, a2code, a2rest, rest)
        line_interpreted = dict(zip(self.keys,values))
        return line_interpreted

    def print_lines(self, liste=[]):
        if not liste:
            liste = self.lines
        for i in liste:
            print self.fmt_line % i

    def my_filter(self, key, value):
        self.reduced_list = filter(lambda x: x[key] == value, self.lines)
        return self.reduced_list

    def group_access(self):
        self.my_filter('code','302')
        self.sessions = []
        a = self.reduced_list[0]['line_number']
        for r in self.reduced_list[1:]:
            b = r['line_number']
            self.sessions.append(self.lines[a:b])
            a = b
class AccessLog:
    ip = re.compile(r'^(\d{1,3}\.){3}(\d{1,3}) ')
    ts = re.compile(r'\[.{26}\]')
    keys = ('line_number','ip','time','code','size','client_cmd')
    fmt_line = '%(line_number)3d: %(ip)16s %(time)s %(code)s %(client_cmd)s'
    
    def __init__(self, fname):
        f = open(fname)
        l = f.read().splitlines()
        f.close()
        if options.verbose and False:
            print len(l), 'Zeilen gelesen'
            for e,i in enumerate(l):
                s = self.ip.search(i)
##                if s is not None:
##                    print i
                if s is None:
                    print e,i
        li = []
        for e,i in enumerate(l):
            line = self.parse_line(i, e)
            li.append(line)
        self.lines = li

    def parse_line(self, line, line_number):
        ipm = self.ip.search(line)
        s,e = ipm.span()
        rest = line[e:].split()
        ip = ipm.string[s:e-1]
##        print '*'.join(rest)
##        print rest[2:4]
        time = ' '.join(rest[2:4])
        a2rest = rest.pop()
        a2code = rest.pop()
        rest = ' '.join(rest[4:])
        #print ip, time, '##', a2code, a2rest, '##', rest
        values = (line_number, ip, time, a2code, a2rest, rest)
        line_interpreted = dict(zip(self.keys,values))
        return line_interpreted

    def print_lines(self, liste=[]):
        if not liste:
            liste = self.lines
        for i in liste:
            print self.fmt_line % i

    def my_filter(self, key, value):
        self.reduced_list = filter(lambda x: x[key] == value, self.lines)
        return self.reduced_list

    def group_access(self):
        self.my_filter('code','302')
        self.sessions = []
        a = self.reduced_list[0]['line_number']
        for r in self.reduced_list[1:]:
            b = r['line_number']
            self.sessions.append(self.lines[a:b])
            a = b
        
def usage(progname):
    usg = """usage: %s [options] <apache-access-log> <Z2.log>
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
    if len(args) < 2:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)

    al = AccessLog(args[0])
    #al.print_lines()
    al.group_access()
    for g in al.sessions:
        print str(len(g)).rjust(4),al.fmt_line % g[0]
