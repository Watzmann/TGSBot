#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Autor: Andreas Hausmann
#  (c) 2007: AHa.Doc. GmbH
#
__svn_date__ = "$Date: 2007-10-22 22:02:44 +0200 (Mo, 22 Okt 2007) $"
__version__ = "$Revision: 203 $"[11:-2]
__svn_url__ = "$URL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/InstallZope/general.py $"
__author__ = "$Author: hausmann $"
__release__ = "0.1"	# Eintragung per Hand (vielleicht geht das auch über svn)

import os
import sys
from subprocess import call, Popen, PIPE
from ConfigParser import ConfigParser

BUFSIZE = 4096

def preparations(settings):
    instdir = settings.get('install_root', False)
    logdir = settings.get('log_dir', False)
    for d in (instdir, logdir):
        if d and not os.path.exists(d):
            os.makedirs(d)
            print 'created', d
        elif d and os.path.exists(d) and not os.path.isdir(d):
            print 'ERROR:', d, 'exists and no directory!!!'
            sys.exit(1)
        if not write_permission(d):
            print 'ERROR: no write permission in %s' % d
            sys.exit(1)
    
def read_settings(sections=[]):
    config = ConfigParser()
    # hier fehlt noch das directory fuer installzope.conf
    files = ['installzope.conf', os.path.expanduser('~/.installzope'),] # /etc/installzope.conf
    config.read(files)
    settings = dict(config.items('general'))
    for s in sections:
        settings.update(dict(config.items(s)))
    return settings

def print_settings(settings):
    keys = settings.keys()
    keys.sort()
    print '- settings ' + '-'*20
    for k in keys:
        print k,'=',settings[k]
    print '-'*30

def write_permission(path):
    if path and os.path.exists(path) and not os.path.isdir(path):
        print 'WARNING: path is not a directory (%s)' % path
        return False
    ah = os.path.join(path,'ah')
    cmd = 'touch %s > /dev/null 2>&1' % ah
    ret = call(cmd, shell=True)
    if os.path.exists(ah):
        os.remove(ah)
    return ret == 0

def tar_path(packet):
    cmd = 'tar tzf %s | head -1' % packet
    #print 'tar_path', cmd
    p = Popen(cmd, shell=True, bufsize=BUFSIZE, stdout=PIPE, stderr=PIPE).stdout
    zope = os.path.dirname(p.read().splitlines()[0])
    p.close()
    #print 'Dirname',zope
    return zope
        
