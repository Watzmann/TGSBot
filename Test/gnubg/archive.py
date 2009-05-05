#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Unterstützt das Archivieren von Einzeldateien in Tarballs.

>>> arc = Archive('test.tar')
>>> arc.append('ah_1')
>>> arc.append('ah_2')
>>> arc.append('ah_1')
>>> arc.append('ah_2', no_doubles=True)
>>> arc.append('ah_3', no_doubles=True)
>>> arc.is_member('ah_3')
True
>>> arc.is_member('ah_4')
False
>>> arc.tar.getnames()
['ah_1', 'ah_2', 'ah_1', 'ah_3']
>>> arc.close()
>>> os.remove('test.tar.gz')
"""

import sys
import os
import tarfile
import subprocess

class Archive:
    # TODOs:
    #       - UNITTESTs
    #
    def __init__(self, archive):
        self.archive = archive
        self.compressed_archive = archive + '.gz'
        self.opened = False

    def load_on_demand(self,):
        if os.path.exists(self.compressed_archive):
            retcode = subprocess.call(["gzip","-d",self.compressed_archive])
            self.tar = tarfile.open(self.archive, 'a')
        else:
            self.tar = tarfile.open(self.archive, 'w')
        self.opened = True

    def append(self, fname, no_doubles=False):
        if not self.opened:
            self.load_on_demand()
        if not (no_doubles and self.is_member(fname)):
            self.tar.add(fname)

    def is_member(self, fname):
        return self.opened and fname in self.tar.getnames()

    def close(self,):
        if self.opened:
            self.tar.close()
            retcode = subprocess.call(["gzip",self.archive])
##  TODO: Fehler abprüfen
        self.opened = False

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
    
    
