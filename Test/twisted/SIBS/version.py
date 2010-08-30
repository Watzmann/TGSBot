#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Version of SIBS."""

REV = '$Revision$'.strip('$').split(':')[1].strip()
VERSION = '.'.join(['0.1',REV])

if __name__ == "__main__":
    print VERSION
