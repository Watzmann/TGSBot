#!/usr/bin/python
"""resize.py changes sizes of images. It is best suited for
processing in batch-manner. One major application of resize.py is
production of thumbnails on large sets of images for use in HTML-
pages.
Uses PIL.Image

(c) 2005 Andreas Hausmann
"""

"""Todos:
- Commandline
- --test modus
- --in/outputpath
- different resizing modes
- resize selbst als Klasse (resize.save())
"""

import Image, os, os.path, sys, glob

FACTOR = 100.

def getOutPath(path):
    start = path
    i = 1
    while os.path.exists(path):
        path = start + '-%03d' % i
        i += 1
    os.mkdir(path)
    return path

def remode(fn,mode):
    i = Image.open(fn)
    j=i.convert(mode)
    return j

def usage(progname):
    print progname,"[-f:] '{files}'"
    print '    -f:    new height [%d]' % int(FACTOR)
    print "globbing is used, so quote {files} with ''"
    print 'output is directed to ./resize[-iii]'

if __name__ == '__main__':
    fileI = sys.argv[1]
#                                               usage
    if fileI == '-h' or fileI == '--help':
        usage(os.path.basename(sys.argv[0]))
        sys.exit()
#                                               new height (default is FACTOR)
    if fileI == '-f':
        height = float(sys.argv[2])
        fileI = sys.argv[3]
    else:
        height = FACTOR
#                                               print infos
    print fileI, height
    print 'ALL',glob.glob(fileI)
#                                               create output path
#                                                   (existing paths are preserved)
    outP = getOutPath('./remode')
    for fileName in glob.glob(fileI):
#                                               compose output file name
        outFile = os.path.basename(fileName)
        out = os.path.join(outP,outFile)
#                                               remode
        try:
            new = remode(fileName,'1')
            new.save(out,'TIFF')
            print '==>', out
        except:
            print "Can't find", fileName

