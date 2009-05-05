#!/usr/bin/python

print "pseude 'du' fest auf USB-Device"

import os
from os.path import join, getsize
S = 0
for root, dirs, files in os.walk('/media/usbdisk'):
    print root, "consumes",
    S = S + int(sum(getsize(join(root, name)) for name in files),)
    print "bytes in", len(files), "non-directory files"
    if 'CVS' in dirs:
        dirs.remove('CVS')  # don't visit CVS directories
print 'du:',S/1024./1024.
