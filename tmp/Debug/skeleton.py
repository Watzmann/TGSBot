#!/usr/bin/python2.3
# -*- coding: utf-8 -*-
"""teste Argumente von der Befehlszeile


(c) 10/2005 Andreas Hausmann
"""

import pdb

def test(c):
    print c

print 'hello'
test('hallo')
pdb.set_trace()
print test.func_code
