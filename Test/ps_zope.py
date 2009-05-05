#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Liest aus 'ps' die Zope-Prozesse aus und macht entsprechende Ausgaben."""

import sys
import os

class Prozesse:

    SEMANTICS = "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"
    semantics = SEMANTICS.lower().split()
    com_idx = 10                        # index of COMMAND-Field
    com_key = semantics[com_idx]        # key of COMMAND-Field

    def __init__(self,):
        command = "ps aux|grep -e '[S]tartup/run.py'"
        #command = "ps aux"
        p = os.popen(command)
        liste = [l.strip('\n') for l in p.readlines()]
        command = "ps aux|grep -e '[Z]EO/runzeo.py'"
        p = os.popen(command)
        liste += [l.strip('\n') for l in p.readlines()]
        self.read_processes(liste)

    def read_processes(self,liste):
        self.processes = []
        for l in liste:
            z = l.split()
            z[self.com_idx] = ' '.join(z[self.com_idx:])
            del z[self.com_idx+1:]
            line = dict(zip(self.semantics,z))
##            for k in line.keys():
##                print k,line[k]
            line['line'] = l
            line['instance'] = self.instance_from_command(line[self.com_key])
            self.processes.append(line)
        return

    def instance_from_command(self,command):
        a = command.split()[-1]   #.split('-C')[1]
        a = a.split(os.sep)[-3]
        #split('etc'
        return a

    def print_instances(self,):
        for l in self.processes:
            print l['pid'],l['instance']
        return
    
    def test_print(self,):
        for l in self.processes:
            print l['line']
            for i in self.semantics:
                print l[i],
            print

if __name__ == "__main__":
    p = Prozesse()
    #p.test_print()
    p.print_instances()
