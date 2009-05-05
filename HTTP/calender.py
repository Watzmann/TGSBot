#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

from datetime import datetime, date, timedelta
import calendar

class Days:
    "Iterator for days starting from a first day"

    def __init__(self, first_day=date.today(), last_day=date.today()):
        self.day = first_day
        self.end = last_day
        self.delta = timedelta(1)

    def __iter__(self):
        return self

    def next(self):
        if self.day > self.end:
            raise StopIteration
        ret = self.day
        self.day += self.delta
        return ret
        
if __name__ == '__main__':
    d1 = date(2004,1,1)
    d2 = d1 + timedelta(365)
    for d in Days(d1,d2):
        print d
