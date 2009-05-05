#!/usr/bin/python
# -*- coding: utf-8 -*-
"""dient als Modul; Test durch modules.py"""

class Klasse:
    def __init__(self,):
        self.tuwas()

    def tuwas(self, msg='das ist ja Klasse'):
        print msg

def usage():
    print 'usage() in', __name__

if __name__ == "__main__":
    usage()
    klasse = Klasse()
    klasse.tuwas('ich tu ja was')
    print 'Ende'
