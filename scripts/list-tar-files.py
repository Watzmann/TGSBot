#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liest tar-files aus (tar tf ....)


(c) 01/2006 Andreas Hausmann  AHa.Doc.
"""

import os, sys

root = '/media/usbdisk/backups'
TAR = '/bin/tar tv%sf %s'
        #os.system(TAR % akte)

def fileType(name):
    p1 = os.path.splitext(name)
    p2 = os.path.splitext(p1[0])
    if p1[1] == '.gz' and p2[1] == '.tar':
        ret = 'gz'
    elif p1[1] == '.tar':
        ret = 'tar'
    else:
        ret = ''
    return ret

compress = {'tar':'','gz':'z'}
liste = os.walk(root)

for root,dirs,files in liste:
    #print root, dirs, files
    for f in files:
        ext = fileType(f)
        tarName = os.path.join(root,f)
        print tarName
        if ext:
            #print '###',TAR % (compress[ext],tarName)
            o = f+'.list'
            if os.path.exists(o):
                print 'WARNING:',o,'exists; not clobbered'
            else:
                g = os.popen(TAR % (compress[ext],tarName),'r')
                go = open(f+'.list','w')
                go.write(g.read())
                go.close()
                g.close()
