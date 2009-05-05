#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Autor: Andreas Hausmann
#  (c) 2007: AHa.Doc. GmbH
#
__svn_date__ = "$Date: 2007-10-22 22:02:44 +0200 (Mo, 22 Okt 2007) $"
__version__ = "$Revision: 203 $"[11:-2]
__svn_url__ = "$URL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/InstallZope/install_python.py $"
__author__ = "$Author: hausmann $"
__release__ = "0.1"	# Eintragung per Hand (vielleicht geht das auch über svn)

import sys
import os.path
from subprocess import Popen, PIPE, call
from ConfigParser import ConfigParser
import general

BUFSIZE = 4096

class Python:

    def __init__(self, version, pil='pil-1.1.6'):
        self.exist = ''
        self.version = version
        self.pil_version = pil
        self.settings = general.read_settings(sections=['python','packets',])
        if not version:
            return

        self.force_installation = False
        
        self.label = '.'.join(version.split('.')[:2])    # 2.3.5 -> 2.3
        cmd = 'which python'    # Installationspfad von python ermitteln
        p = Popen(cmd, shell=True, bufsize=BUFSIZE, stdout=PIPE,).stdout
        python = p.read().splitlines()[0] + self.label
        self.python_exe_name = os.path.basename(python)
        p.close()

        # Annahme:
        #   wenn zu "version" (z.B. 2.3.5) eine Installation existiert,
        #   dann existiert ein <prefix>/python2.x (z.B. <prefix>/python2.3)
        if os.path.exists(python):
            cmd = python + ' -V'    # Tatsächliche Version ermitteln
            p = Popen(cmd, shell=True, bufsize=BUFSIZE, stderr=PIPE,).stderr
            python = p.read().splitlines()[0].split()[1]
            p.close()
            self.exist = True
            self.version = python

    def print_settings(self,):
        general.print_settings(self.settings)

    def install(self):
        if self.exist and not self.force_installation:
            print 'found existing version', self.version
            return
        else:
            print 'Installing Python', self.version
            general.preparations(self.settings)
            self.settings['this_install_root'] = \
                os.path.join(self.settings['install_root'],'Python-'+self.version)
            self.settings['logfile_root'] = \
                os.path.join(self.settings['log_dir'],'python-'+self.version)
##            if self.exist:
##                self.uninstall()
            self.unpack()
            self.configure()
            self.make()
            self.make_test()
            self.make_install()

    def install_pil(self, version=''):
        if version == '':
            version = self.pil_version
        if not version.startswith('pil-'):
            version = 'pil-' + version
        #...
        
    def unpack(self, check=False):
        st = self.settings
        key = 'python-%s' % self.version
        if not st.has_key(key):
            print 'ERROR: no package information for', key
            retcode = 2
        else:
            packet_label = st[key]
            packet = os.path.join(st['sources'],packet_label)
            st['packet'] = packet
            ok = os.path.exists(packet)
            if not ok:
                print 'ERROR: cannot find', packet
                sys.exit(1)
            elif check:
                print 'found', packet
                retcode = 0
            else:
                print 'unpacking', packet_label
                #general.print_settings(st)
                if os.path.exists(st['this_install_root']):
                    cmd = 'rm -rf %(this_install_root)s' % st
                    #print cmd
                    retcode = call(cmd.split())
                    #print retcode, '(for >%s...)' % cmd[:15]
                cmd = 'tar xjf %(packet)s -C %(install_root)s' % st
                #print cmd
                retcode = call(cmd.split())
                #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode

    def configure(self,):
        print 'about to configure ...'
        params = self.settings.copy()
        params['logfile'] = params['logfile_root'] + '-configure'
        #general.print_settings(params)
        cmd = 'cd %(this_install_root)s; ./configure --prefix=%(prefix)s > %(logfile)s 2>&1' % params
        print cmd
        retcode = call(cmd, shell=True)
        #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def make(self,):
        print 'about to make ...'
        params = self.settings.copy()
        params['logfile'] = params['logfile_root'] + '-make'
        #general.print_settings(params)
        cmd = 'cd %(this_install_root)s; make > %(logfile)s 2>&1' % params
        print cmd
        retcode = call(cmd, shell=True)
        #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def make_test(self,):
        print 'about to test ...'
        params = self.settings.copy()
        params['logfile'] = params['logfile_root'] + '-make-test'
        #general.print_settings(params)
        cmd = 'cd %(this_install_root)s; make test > %(logfile)s 2>&1' % params
        print cmd
        retcode = call(cmd, shell=True)
        print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def make_install(self,):
        print 'about to install Python', self.version
        #return
        params = self.settings.copy()
        params['logfile'] = params['logfile_root'] + '-install'
        #general.print_settings(params)
        cmd = 'cd %(this_install_root)s; make altinstall > %(logfile)s 2>&1' % params
        print cmd
        retcode = call(cmd, shell=True)
        print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def uninstall(self,):
        python = self.python_exe_name
        liste = [os.path.join('/usr',p,python) for p in ['bin','lib','include',]]
        for l in liste:
            print 'uninstalling', l
            cmd = 'rm -rf %s' % l
            print cmd
            #continue
            retcode = call(cmd, shell=True)
            print retcode, '(for >%s...)' % cmd[:15]
            if retcode > 0:
                sys.exit(1)
        return
        
if __name__ == '__main__':
    Python('').print_settings()
    
    for v in ['2.3','2.4.4','2.5',]:  #'2.6.1',]:
        f = Python(v)
        if f.exist:
            print 'found', f.version, '(looking for %s)' % v
        else:
            f.install()

##    f = Python('2.3.5')
##    f.force_installation = True
##    f.install()
