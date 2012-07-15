#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Testing some features used in proto_proxy.py."""

import re

pattern = re.compile("There are [0123456789]* users logged on.")
the_number = re.compile("[0123456789]*")

def test(s, n, hit):
    found = pattern.match(s)
    if found is None:
        if hit:
            print 'ERROR @', s, n, hit
        return
    found = [f for f in the_number.findall(s) if f]
    if found:
        number = int(found[0])
    if number != n:
        print 'ERROR @', s, n, number
    
for n in range(2500):
    s = "There are %d users logged on." % n
    test(s, n, True)
    t = "Te are %d users logged on." % n
    test(t, n, False)

interval_groups = {150: (500., 850.), #150
                   200: (350., 550.), #200
                   220: (250., 400.), #220
                   300: (150., 250.),} #300

def test_grouping(number):
    groups = interval_groups.keys()
    groups.sort()
    for n in groups:
        if n >= number:
            print number,'->',n
            break

for n in range(28):
    test_grouping(n*10)
