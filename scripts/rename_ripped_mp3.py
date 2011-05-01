#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob

m3u = open('/home/hausmann/mp3/rolling_stones-sticky_fingers.m3u',)
liste = m3u.read().splitlines()
m3u.close()

liste = [os.path.basename(l) for l in liste]
print liste

os.chdir('rolling_stones/sticky_fingers')

tracks = glob.glob('track_??.mp3')
tracks.sort()

for t in tracks:
    l = liste.pop(0)
    print t, '->', l
    os.rename(t,l)
