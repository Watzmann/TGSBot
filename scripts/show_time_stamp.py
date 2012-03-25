#!/usr/bin/env python
"""Print nicely timestamps like 1295819287535659."""

import sys
import time

def convert(stamp):
    return time.asctime(time.localtime(float(stamp)/1000000.))

if __name__ == "__main__":
    if len(sys.argv) < 2:
	print __doc__
        print "Please give timestamp in commmandline."
        sys.exit(1)

    stamp = sys.argv[1]
    print convert(stamp)
