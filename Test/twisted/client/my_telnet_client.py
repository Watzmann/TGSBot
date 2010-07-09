#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

#from telnetlib import Telnet

import getpass
import sys
import telnetlib
import time

HOST = "localhost"
PORT = 8080

tn = telnetlib.Telnet(HOST, PORT)
time.sleep(1)
res = tn.read_eager().strip('\r\n')
Nr = res.split(':',1)[0].split()[1]

for m in ("hello","and again","shuffle halligalli"):
    tn.write(m+'\r\n')
    time.sleep(1)
    res = tn.read_eager().strip('\r\n')
    nr = res.split(':',1)[0].split()[1]
    print nr,'#',res

tn.write("exit\n")

print '*****'
time.sleep(1)

print tn.read_all()
tn.close()
