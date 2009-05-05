#!/usr/bin/python
"""multiPageTiff.py tests Image-lib for use with multipage-Tiffs.
Employs PIL.Image

(c) 2006 Andreas Hausmann
"""

"""Todos:
- 
"""

import sys, os, os.path
import Image

def test(fname):
    im = Image.open(fname)
    print im.info
    #sys.exit(0)
    
    i = 0
    try:
        im.seek(0)
        im.seek(1)
        im.seek(0)
        multip = True
    except:
        multip = False

    print 'mp',multip

    while 1:
        try:
            im.seek(i)
            im.save('test-multi/test%d.tif' % i)
            print 'wrote',i
            #im.show()
            i += 1
        except:
            print 'Abbruch at',i
            break

def usage(progname):
    print progname,"<file>"

if __name__ == '__main__':
    try:
        fn = sys.argv[1]
    except:
        fn = 'Multipage_TIF_Test.tif'
        #print 'kein File angegeben'
        #usage(sys.argv[0])
        #sys.exit(1)
    test(fn)
