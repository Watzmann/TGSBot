#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Gibt den eigenen Pfad PATH in leserlichem Format aus."""

import os

p=os.environ['PATH'].split(':')
for i in p:
    print i
