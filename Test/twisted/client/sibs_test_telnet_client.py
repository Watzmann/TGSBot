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

def client(msg):
    nr = msg.split(':',1)[0].split()[1]
    if nr != Nr:
        print 'Client Nr. %d; wrong ID %d!' % (Nr, nr)
    return nr
        
tn = telnetlib.Telnet(HOST, PORT)
time.sleep(1)
res = tn.read_eager().strip('\r\n')
Nr = res.split(':',1)[0].split()[1]
print 'nr %s started' % Nr

for m in ("hello","and again","shuffle halligalli"):
    tn.write(m+'\r\n')
    time.sleep(1)
    nr = client(tn.read_eager().strip('\r\n'))

tn.write("exit\n")
time.sleep(1)

nr = client(tn.read_all())
tn.close()
print 'nr %s stopped' % Nr
