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

Nr = -1

def client(msg):
    try:
        nr = msg.split(':',1)[0].split()[1]
    except:
        print 'Problems splitting', nr
        nr = -2
    if nr != Nr:
        print 'Client Nr. %d; wrong ID %d!' % (Nr, nr)
    return nr
        
tn = telnetlib.Telnet(HOST, PORT)
time.sleep(1)
res = tn.read_eager().strip('\r\n')
try:
    Nr = res.split(':',1)[0].split()[1]
    print 'nr %s started' % Nr
except:
    print 'Problems splitting', res
print 'received a:', res

for m in ("hello","and again","shuffle halligalli"):
    tn.write(m+'\r\n')
    time.sleep(1)
    try:
        s = tn.read_eager().strip('\r\n')
        nr = client(s)
    except:
        print 'Problems processing', s

tn.write("exit\n")
time.sleep(1)

nr = client(tn.read_all())
tn.close()
print 'nr %s stopped' % Nr
