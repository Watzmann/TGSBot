#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities around timezones."""

# might be available from the python world, but I wanted a quick and fast.....

REV = '$Revision: 246 $'

import os
import time
import datetime
import pytz
import logging
from version import Version

v = Version()
v.register(__name__, REV)

logging.basicConfig(level=logging.DEBUG,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('tz_utils')

def date_from_timestamp(stamp=time.time()):
    return datetime.datetime.fromtimestamp(stamp, pytz.utc)

class TZ:
    
    fmt = "%A, %B %d %H:%M:%S %Z"
    sfmt = "%c %Z"
    
    def __init__(self,):
        self.text = self._all_zones_text()

    def is_valid(self, tz):
        return tz in pytz.all_timezones

    def long_time(self, utc_dt=date_from_timestamp(), zone=None):
        _utc = utc_dt.strftime(self.sfmt) 
        return '%s   ( %s )' % (self.fmt_time(utc_dt, zone), _utc)

    def fmt_time(self, utc_dt=date_from_timestamp(), zone=None):
        if zone is None:
            ret = utc_dt.strftime(self.fmt)
        else:
            try:
                loc = pytz.timezone(zone)
                loc_dt = utc_dt.astimezone(loc)
                ret = loc_dt.strftime(self.fmt)
            except pytz.UnknownTimeZoneError:
                logger.error('TZ.fmt_time(): Unknown Time Zone Error %s' % zone)
                ret = utc_dt.strftime(self.fmt)
        return ret

    def _all_zones_text(self,):
        text = ''
        c = []
        l = 0
        for zi in pytz.all_timezones:
            c.append(zi)
            l += len(zi)
            if l < 77 - len(c)*2:
                continue
            text += ', '.join(c[:-1]) + '\n'
            c = [zi,]
            l = len(zi)
        if not text[-1] == '\n':
            text += '\n'
        return text

    def max_line_width(self, from_file=False):
        max_w = 0                   # original version results in 77
        if from_file:
            with open('ressources/timezones') as tz:
                for line in tz:
                    max_w = max(max_w, len(line))
            max_w -= 1
        else:
            for line in self.text.splitlines():
                max_w = max(max_w, len(line))
        return max_w

def test(zi):
    #fmt="%Y-%m-%d %H:%M:%S %Z%z"
    for i in pytz.all_timezones:
        print zi.fmt_time(zone=i), i
    print zi.fmt_time(), 'UTC'

if __name__ == "__main__":
    tz = TZ()
#    print pytz.all_timezones
#    print tz.text,
    test(tz)
    print tz.fmt_time(zone='CEST'), 'CEST'
#    print 'line length', tz.max_line_width()
    print tz.fmt_time()
    print tz.long_time(zone='CET')
    print tz.long_time(zone='MET')
