#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Siehe http://wiki.python.org/moin/Twisted-Examples
"""

import getpass
import sys
import telnetlib

HOST = "localhost"
PORT = 8080

tn = telnetlib.Telnet(HOST, PORT)

for m in ("hello\r\n","and again\r\n"):
    tn.write(m)
##    time.sleep(1)
    print tn.read_lazy()
    print '--------'

tn.write("exit\n")

print '*****'
print '1'+ tn.read_all()

print '2'+ tn.read_all()
tn.close()
