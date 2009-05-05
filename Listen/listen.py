#!/usr/bin/python
# -*- coding: utf-8 -*-
"""listen.py stellt Klassen zur Listenbearbeitung zur Verfügung"""

import sys
import os
from types import *
from optparse import OptionParser

# TODOs
#
### 1) über Listen-Objekte sollte man direkt iterieren können (also __iter__()
###    einfügen)
# 2) Liste() sollte doch durch Vererbung die Eigenschaft erhalten, von
#    den Quellen 'Liste', 'stdin' und 'file' automatisch zu lesen.
#    Das Objekt muss gebaut werden und hier rein-vererbt.
#

LT_LIST = 'list'
LT_FILE = 'file'
LT_STDIN = 'stdin'
LT_EMPTY = None

class Liste:
    """Constructor:
      reads list from
        - parameter
        - file if parameter is existing file
        - stdin if parameter is '-'
    Issues Warning if nothing to read.
    """

    def __init__(self, liste, **kw):
        if type(liste) is ListType:
            #print 'is list:', type(liste)
            self._raw_liste = liste[:]
            self._list_type = LT_LIST
        elif liste == '-':
            #print 'reading stdin'
            self._raw_liste = sys.stdin.read().splitlines()
            self._list_type = LT_STDIN
        elif type(liste) is StringType and os.path.exists(liste):
            #print 'reading file', liste
            self._raw_liste = self.read_liste_from_file(liste)
            self._list_type = LT_FILE
            self.full_path = liste
        else:
            #print "keine Liste gefunden"
            self._raw_liste = []
            self._list_type = LT_EMPTY
            self.full_path = liste
##            print 'WARNING:Liste:Keine Liste gefunden: %s' % liste
        self.liste = self.my_filter(**kw)

    def __iter__(self,):
        """Lässt über pliste iterieren, wenn vorhanden; sonst liste"""
        return getattr(self, 'pliste', self.liste).__iter__()

    def __len__(self,):
        """Liefert die Länge von pliste, wenn vorhanden; sonst liste"""
        return len(getattr(self, 'pliste', self.liste))

    def list_type(self,):
        """Returns the type of which list was read from."""
        return self._list_type

    def read_liste_from_file(self, fname):
        """Read and render as list"""
        f = open(fname)
        l = f.read().splitlines()
        f.close()
        return l

    def my_filter(self, **kw):
        """
        Applies filter to list; launched in constructor;
        optional arguments can be supplied in dictionary self.filter_args;
        to be overridden by subclass;
        """
        return self._raw_liste

    def remove(self, sequence_of_keys):
        """
        Removes entries with keys given in 'sequence_of_keys' from dliste
        and pliste.
        If <key> is not in dliste it is ignored.
        If no self.dliste is available, returns with no effect.
        Sideeffect! Sorting of pliste is not preserved.
        """
        if hasattr(self,'dliste'):
            dl = self.dliste
            if not type(sequence_of_keys) is ListType:
                sequence_of_keys = [sequence_of_keys]
            for s in sequence_of_keys:
                try:
                    del dl[s]
                except KeyError:
                    pass
            self.pliste = dl.values()

    def interpret(self, klasse, **kw):
        """
        Loads a line object for each line;
        the class should come (or be derived) from el_listen.py;
        can be overridden by subclass;
        """
        self.pliste = []
        for i in self.liste:
            self.pliste.append(klasse(i, **kw))
            # TODO: hier könnte man (über **kw) direkt process() aufrufen
        return self.pliste

    def list2hash(self,):
        """
        Builds a dictionary for this list;
        the key is supplied by the interpretation class (see self.interpret());
        values are the interpreted lines;
        """
        self.dliste = {}
        for i in self.pliste:
            self.dliste[i.primary_key()] = i
        return self.dliste

    def process(self, **kw):
        """
        calls process() for each line;
        this requires a method process() in the line classes;
        """
        for line in self.pliste:
            line.process(**kw)

    def print_lines(self, start = -1, end = -1):
        """
        calls __repr__() for each line;
        this requires some __repr__() in the line classes;
        """
        if (start,end) == (-1,-1):
            liste = self.liste
        elif start > -1 and end < 0:
            liste = self.liste[start:]
        elif end > -1 and start < 0:
            liste = self.liste[:end]
        elif start > -1 and end > -1:
            liste = self.liste[start:end]

        for line in liste:
            print line

if __name__ == "__main__":

    arg = sys.argv[1]
    print 'reading', arg
    l = Liste(arg)
    l.print_lines()
