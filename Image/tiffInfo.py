#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Liest die Info von TIFF-Images aus.
Verwendet PIL.Image
(c) 2006 Andreas Hausmann
"""

__TODOS__="""Todos:
"""

import Image
import sys, os


def info(fn):
    i = Image.open(fn)
    a0,a1 = i.size
    mode = i.mode
    format = i.format
    inf = i.palette
    #print 'size %dx%d' % (a0,a1),'  mode',mode,'  format',format,'   info',inf
    return mode

def parseTiffInfo(info):
    width,length,res,bit,smpl,photo,planar = (0,0,'','','','','',)
    for i in info:
        p = i.split()
        if 'Width' in i:
            width = int(p[2])
            length = int(p[5])
            continue
        if 'Resolution' in i:
            res = ' '.join(p[1:])
            continue
        if 'Bits' in i:
            bit = p[1]
            continue
        if 'Samples' in i:
            smpl = p[1]
            continue
        if 'Photometric' in i:
            photo = ' '.join(p[2:])
            continue
        if 'Planar' in i:
            planar = ' '.join(p[2:])
            continue
    return width,length,res,bit,smpl,photo,planar

def maxLenNames(files):
    maxLen = 0
    for i in files:
        maxLen = max(maxLen,len(i))
    return maxLen

def tiffHeading(nameLen):
    print 'Datei'.ljust(nameLen),'Abmessung'.ljust(9), \
          'Auflösung'.ljust(22)+'#','bit'.ljust(3),'?'.ljust(3), \
          'mode'.ljust(7),'photo'.ljust(15),'planar'
    return

def tiffInfo(fn):
    p = os.popen('tiffinfo "%s"' % fn)
    l = p.readlines()
    p.close()
    width,length,res,bit,smpl,photo,planar = parseTiffInfo(l)
    mode = info(fn)
    print ('%4dx%d'%(width,length)).ljust(9),res.ljust(22), \
          bit.ljust(3),smpl.ljust(3),mode.ljust(7),photo.ljust(15),planar
    return

def usage(progname):
    print progname," {files}"
    print 'print different sorts of tiff-infos of tiff-files'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage(os.path.basename(sys.argv[0]))
        sys.exit(0)
    listofFiles = sys.argv[1:]
    printLen = maxLenNames(listofFiles) + 4
    tiffHeading(printLen)
    for l in listofFiles:
        lu = l.decode('utf-8','replace')
        if not os.path.splitext(lu)[1] == '.tif': continue
        print lu.ljust(printLen).encode('utf-8','replace'),
        i = tiffInfo(l)
    sys.exit(0)

