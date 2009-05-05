#!/usr/bin/python
# -*- coding: utf-8 -*-

print 'hier spricht', __name__

from os.path import basename as bn

def main():
    print __file__,'in main() gelandet'
    return

def test1():
    print ' ',bn(__file__),'as',__name__,'in test1() gelandet'
    return

if __name__ == '__main__':
    main()
