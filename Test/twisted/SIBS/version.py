#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Version of SIBS."""

revs = []

from sibs_utils import REV
revs.append(REV)
from persistency import REV
revs.append(REV)
from sibs_user import REV
revs.append(REV)
from telnet_server import REV
revs.append(REV)
from clip import REV
revs.append(REV)
from command import REV
revs.append(REV)

REV = '$Revision$'
revs.append(REV)

revs = [int(i.strip('$').split(':')[1].strip()) for i in revs]
max_rev = str(max(revs))
VERSION = '.'.join(['0.1',max_rev])

if __name__ == "__main__":
    print VERSION
