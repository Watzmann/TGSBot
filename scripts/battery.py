#!/usr/bin/env python

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

for l in lines:
    print l

a,b = float(capacity)//float(present_rate),float(capacity)/float(present_rate)
b = b - a
remains = '%d:%02d' % (a,b*60)

print 'remains %s h' % (remains,)
