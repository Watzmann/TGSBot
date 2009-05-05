#!/usr/bin/python

import sys

global_var = 9999

def outer():
    z = 42
    def inner():
	global z
	y = 666
	z = 99
	print dir()
    inner()
    print dir(), z

print dir()
outer()
print z
print dir()
