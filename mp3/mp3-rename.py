#!/usr/bin/env python

"""mp3-rename.py
(c) Andreas Hausmann, 2005
"""

from tagger import *

print __doc__

def main(filename):
    id3 = ID3v2(filename)
    frame=id3.frames[0]
    print "%s (%s) %s" % (frame.fid, frame.encoding, str(frame.strings))

if __name__ == "__main__":
    filename = '/home/hausmann/Python/Download/pytagger-0.4/mp3/ha_ich_bins_ich_bins.mp3'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    main(filename)
