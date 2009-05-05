#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Bietet Interpretations-Klassen für Zeilen von Listen"""


#
#
#   Unit Testing !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
#



import sys
import os
from listen import Liste
from optparse import OptionParser

DEF_DEPTH = 2

class Line:

    delimiter = ' '
    interpretation = ['perm',
                      'user',
                      'size',
                      'date',
                      'time',
                      'path',
                      ]
    key = 'path'

    def __init__(self, line, **kw):
        self.line = line
        self.parse_line(**kw)
        for i in self.interpretation:
            exec 'self.%s = self.interpreted_line["%s"]' % (i,i)
            # TODO: 1) Diese pfiffige Konstruktion ersetzen durch
            #          setattr(self,i,self.interpreted_line[i])
            #          (wenn das so richtig ist??)
        return

    def __repr__(self,):
        return str(self.line)

    def parse_line(self, discard_contiguos_blanks=False):
        p = self.line.split(self.delimiter)
        if discard_contiguos_blanks:
            try:
                while True:
                    p.remove('')
            except ValueError:
                pass
        li = len(self.interpretation)
        if len(p) > li:
            p[li-1] = ' '.join(p[li-1:])
        if len(p) < li:
            p += ['']*(li-len(p))
        self.p = p
        self.interpreted_line = dict(zip(self.interpretation,p))

    def primary_key(self,):
        return self.interpreted_line[self.key]

    def process(self,):
        # to be overwritten

        # TODO: hier abfrage auf "ist schon processed", wenn nein, dann
        #       Aufruf von privater methode. _Die_ muss dann überschrieben werden
        return

class Entry(Line):
    """The class that takes an entry line, parses and renders information
    and methods concerning the lines contents."""
    
    types = ['tar','long','simple',]
    default = 'simple'
    
    def __init__(self, line, **kw):
        self.line_types = {'long': self.parse_long,
                          'tar': self.parse_tar,
                          'simple': self.parse_simple,
                          }
        Line.__init__(self, line)
        self.full_path = ''
        self.name = ''
        self.path = ''
        self.access = ''
        self.nr_links = ''
        self.user = ''
        self.group = ''
        self.size = 0L
        self.date = ''
        self.time = ''

        if kw.has_key('list_type'):
            self.line_type = kw['list_type']
        else:
            self.line_type = self.which_type(line)
        self.parse(line,)

    def __repr__(self,):
        return '%s %s' % (self.name, self.path)

    def print_formatted(self,):
        from StringIO import StringIO
        out = StringIO()
        for i in ('full_path', \
                  'name', \
                  'path', \
                  'access', \
                  'nr_links',
                  'user',
                  'group',
                  'size',
                  'date',
                  'time',):
            ev = eval('self.%s' % i)
            if ev:
                print >> out, '%10s:' % i, ev
        return out.getvalue()
    
    def which_type(self, line):
        # netter versuch
        # von der Idee her gut
        # das kann man ausbauen, aber
        #   - es sollte dann von unten eine eigene Exception hochgegeben werden
        #   - es sollte generalisiert werden
        #   - es sollten spezielle Versuchs-Methoden sein
        for k in self.line_types.keys():
            if k == self.default:
                continue
            print 'trying', k
            try:
                self.line_types[k](line)
                print 'tried',k,'with success'
                return k
            except:
                print 'tried',k,'no success'
                pass
        k = self.default
        try:
            self.line_types[k](line)
            print 'tried',k,'with success'
        except:
            k = 'no_parser'
        return k
    
    def parse(self, line,):
        ret = ''
        if 'no_parser' == self.line_type:
            print '! no parser available'
        else:
            try:
                ret = self.line_types[self.line_type](line)
            except:
                print 'encountered errors parsing', self.line_type
                print '>>>', line
        return ret

    def parse_simple(self, line):
        return self.parse_path(line)

    def parse_long(self, line):     # mit parse_tar zusammenlegen !
        #print line
        self.access = line[:10]
        rest = line[11:]
        a = rest.split(' ')
        while not a[0]:
            del a[0]
        #print a
        self.nr_links = int(a[0])
        self.user = a[1]
        self.group = a[2]
        del a[:3]
##        for i in (self.access,`self.nr_links`,self.user,self.group):
##            print '#'+i+'#',
        while not a[0]:
            del a[0]
        self.size = long(a[0])
        self.date = a[1]
        self.time = a[2]
##        for i in (`self.size`,self.date,self.time):
##            print '#'+i+'#',
        a = self.parse_path(a[3])
##        for i in (self.path,self.name,self.full_path):
##            print '#'+i+'#',
##        print
        return line

    def parse_tar(self, line):
        self.access = line[:10]
        rest = line[11:]
        a = rest.split(' ')
        users = a[0].split('/')
        self.user = users[0]
        self.group = users[1]
        del a[0]
        while not a[0]:
            del a[0]
##        print line
##        for i in (self.access,self.user,self.group):
##            print '#'+i+'#',
        self.size = long(a[0])
        self.date = a[1]
        self.time = a[2]
##        for i in (`self.size`,self.date,self.time):
##            print '#'+i+'#',
        a = self.parse_path(a[3])
##        print a
        return line

    def parse_path(self, fullname):
        a = os.path.split(fullname)
        self.path = a[0]
        self.name = a[1]
        self.full_path = fullname
        return fullname

    def is_directory(self,):
#        print self.access
        return self.access and 'd' == self.access[0]

    def process(self,**kw):
        # das hier wurde eine Zeilen-Methode aus einer Listen-Methode;
        # kann sein, dass jetzt die Denke noch umstrukturiert werden muss
        dic = kw['dic']
        #liste = kw['liste']        # liste (Referenz auf Liste) nicht gebraucht
        b_entry = self.name
        if not b_entry or ':' == b_entry:
            return          # untersuche _nicht_ Files wie '/home/andreas/:'
        found_list = list(self.find_entry(b_entry))
        #print 'fl',entry.name,found_list
        #print entry
        if self.full_path in found_list:
            found_list.remove(self.full_path)
        equal_list = [self.equal_entry(self.full_path,c_entry) for c_entry in found_list]
        #print 'el',equal_list
        dic[self.full_path] = {'found':found_list,'equal':equal_list,
                      'diffs':'different' in equal_list}
        #print 'dic',dic[self.full_path]
        return
    def find_entry(self,entry):
        # hier könnte speed tuning Sinn machen
        #
        # Das sollte selber wieder eine Liste sein
        p = os.popen('locate -b "%s"' % entry)
        lines = p.read().splitlines()
        p.close()
        #print entry,':?:',lines
        return [a for a in lines if not '/.svn' in a]      # masking off .svn
    def equal_entry(self,entry,companion):
        # hier sollten lieber zwei Entries verglichen werden, statt
        # name <-> entry
        r = 'equal'
        if os.path.basename(companion) <> os.path.basename(entry):
            return r
        p = os.popen('cmp "%s" "%s" 2>/dev/null' % (entry,companion))
        lines = p.read()
        p.close()
        if lines:
            r = 'different'
        return r

class Entry_simple(Entry):
    """The class that takes an entry line, parses and renders information
    and methods concerning the lines contents."""

    def __init__(self, line, **kw):
        Entry.__init__(self, line, **kw)
    
    def parse_line(self, line,):
        ret = ''
        if 'no_parser' == self.line_type:
            print '! no parser available'
        else:
            try:
                ret = self.line_types[self.line_type](line)
            except:
                print 'encountered errors parsing', self.line_type
                print '>>>', line
        return ret

if __name__ == "__main__":

    examples = ['help= set listing depth;',
                'help= set listing depth; default is %d. % def_depth)'
                ]
    
    for i in examples:
        print '-'*60
        l = Line(i)
        print l
        print 'Pfad',l.path
        v = vars(l)
        for k in v.keys():
            print k, v[k]
#        print l.interpreted_line
