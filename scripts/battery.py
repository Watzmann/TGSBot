#!/usr/bin/env python

from termcolor import cprint

state = open("/proc/acpi/battery/BAT0/state")
lines = state.read().splitlines()
state.close()

for l in lines:
    if l.startswith('present rate:'):
        present_rate = l.split()[2]
        print present_rate

for l in lines:
    if l.startswith('remaining capacity:'):
        capacity = l.split()[2]
        print capacity

a,b = float(capacity)//float(present_rate),float(capacity)/float(present_rate)
b = b - a
a,b = 0,.2

remains = '%d:%02d' % (a,b*60)
text = 'remains %s h' % (remains,)

if a > 0 or (a == 0 and b > .5):
    print text
elif b > .25:
    cprint(text, 'red',)
else:
    cprint(text, 'green', 'on_red')

for l in lines:
    print l
