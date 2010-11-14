#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool to get alarmed about users logging in.

    Example: tail -f /srv/SIBS/sibstest/server.log| ./watch_beep.py
"""

import sys
import os.path
import subprocess

sounds = "/opt/JavaFIBS2001/sound"
friend = os.path.join(sounds,"friend.wav")

if __name__ == '__main__':
    while 1:
        line = sys.stdin.readline(160)
        if not 'auth' in line:
            continue
        print line,
        subprocess.call(["play","-q",friend])
        
