#!/usr/bin/env python
"""This script converts time.time() stamps to comprehensible format."""

import sys
import time

def convert_time(stamp):
    return time.asctime(time.localtime(float(stamp)))

a = time.time()
print str(a), len(str(a)), convert_time(a)

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        sys.exit(0)
    for a in args:
        print a, convert_time(a)
