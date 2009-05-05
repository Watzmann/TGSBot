#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Autor: Andreas Hausmann
#  (c) 2007: AHa.Doc. GmbH
#
__svn_date__ = "$Date: 2007-10-22 22:02:44 +0200 (Mo, 22 Okt 2007) $"
__version__ = "$Revision: 203 $"[11:-2]
__svn_url__ = "$URL: svn+ssh://BIC/srv/svn/repositories/Entwicklung/Python/trunk/InstallZope/install_zope.py $"
__author__ = "$Author: hausmann $"
__release__ = "0.1"	# Eintragung per Hand (vielleicht geht das auch über svn)

import sys
import os.path
from subprocess import Popen, PIPE, call
from ConfigParser import ConfigParser
import general

BUFSIZE = 4096

class Zope:

    labels = {'2.8.6':'86'
#             ,'2.10.4':'104'
              }

    def __init__(self, version,):
        self.exist = ''
        self.version = version
        self.settings = general.read_settings(sections=['zope','packets',])
        if not version:
            return
        if not self.labels.has_key(version):
            print 'ERROR: no label information for', version
            sys.exit(2)

        self.force_installation = False

        self.all_those_different_names()
        print version, 'label', self.label
            # Installationen von zope ermitteln
            # beachtet wird nur <dirname(self.prefix)>
        cmd = 'find %s -name version.txt | grep "lib/python/version"' % \
                                    os.path.dirname(self.settings['prefix'])
        #print cmd
        p = Popen(cmd, shell=True, bufsize=BUFSIZE, stdout=PIPE,).stdout
        zopes = p.read().splitlines()
        p.close()
        
        found_versions = self.existing_zope_versions(zopes)
        ret = self.version_exists(self.version, found_versions)
        if ret != ('', ''):
            self.exist = True
            self.version, self.exist_path = ret
            #print 'version %s, path %s' % ret

    def all_those_different_names(self,):
        self.label = self.labels[self.version]    # 2.8.6 -> 86
        st = self.settings
        st['prefix'] = st['prefix'] + self.label
        key = 'zope-%s' % self.version
        if not st.has_key(key):
            print 'ERROR: no package information for', key
            sys.exit(2)
        packet_label = st[key]
        packet = os.path.join(st['sources'],packet_label)
        st['packet'] = packet
        st['name'] = general.tar_path(packet)
        st['this_install_root'] = os.path.join( \
                        self.settings['install_root'], st['name'])
        st['logfile_root'] = \
            os.path.join(self.settings['log_dir'], st['name'].lower())
        return

    def print_settings(self,):
        general.print_settings(self.settings)

    def version_exists(self, version, zope_versions):
        ret = ('', '')
        for k in zope_versions.keys():
            if version in k:
                path = os.sep.join(zope_versions[k].split(os.sep)[:-3])
                ret = (k, path)
        return ret
    
    def existing_zope_versions(self, all_zopes):
        zope_versions = {}
        for z in all_zopes:
            version = self.read_version_information(z)
            zope_versions[version] = z
        return zope_versions

    def read_version_information(self, zope):
        cmd = 'cat %s' % zope    # Tatsächliche Version ermitteln
        p = Popen(cmd, shell=True, bufsize=BUFSIZE, stdout=PIPE,).stdout
        version = p.read()
        p.close()
        return version

    def install(self):
        if self.exist and not self.force_installation:
            print 'found existing version', self.version
            return
        else:
            print 'Installing Zope', self.version
            general.preparations(self.settings)
            #self.print_settings()
            if self.exist:
                self.uninstall()
            self.unpack()
            self.configure()
            self.make()
            self.make_install()

    def unpack(self, check=False):
        st = self.settings
        packet = st['packet']
        ok = os.path.exists(packet)
        retcode = 0
        if not ok:
            print 'ERROR: cannot find', packet
            sys.exit(1)
        elif check:
            print 'found', packet
            retcode = 0
        else:
            print 'unpacking', packet
            #general.print_settings(st)
            if os.path.exists(st['this_install_root']):
                cmd = 'rm -rf %(this_install_root)s' % st
                #print cmd
                retcode = call(cmd.split())
                #print retcode, '(for >%s...)' % cmd[:15]
            cmd = 'tar xzf %(packet)s -C %(install_root)s' % st
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
        #print cmd
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
        #print cmd
        retcode = call(cmd, shell=True)
        #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def make_install(self,):
        print 'about to install Zope', self.version
        #return
        params = self.settings.copy()
        params['logfile'] = params['logfile_root'] + '-install'
        #general.print_settings(params)
        cmd = 'cd %(this_install_root)s; make install > %(logfile)s 2>&1' % params
        #print cmd
        retcode = call(cmd, shell=True)
        #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return retcode
        
    def uninstall(self,):
        if self.exist and self.exist_path and os.path.exists(self.exist_path):
            print 'uninstalling', self.exist_path
            cmd = 'rm -rf %s' % self.exist_path
            #print cmd
            retcode = call(cmd, shell=True)
            #print retcode, '(for >%s...)' % cmd[:15]
            if retcode > 0:
                sys.exit(1)

    def make_instance(self, instance_name='default', user='admin', passwd='ahadoc'):
        print 'in make_instance', instance_name
        print 'version %s, path %s' % (self.version, self.exist_path)
        mkzi = os.path.join(self.exist_path,'bin','mkzopeinstance.py')
        cmd = '%s -d /var/opt/zope/%s -u %s:%s' % (mkzi,instance_name,user,passwd)
        print cmd
        retcode = call(cmd, shell=True)
        #print retcode, '(for >%s...)' % cmd[:15]
        if retcode > 0:
            sys.exit(1)
        return


if __name__ == '__main__':
    Zope('').print_settings()
    #sys.exit()
    
##    for v in ['2.8.6','2.10.4',]:  #'2.6.1',]:
##        f = Zope(v)
##        if f.exist:
##            print 'found', f.version, '(looking for %s)' % v
##        else:
##            f.install()

    f = Zope('2.8.6')
    #f.force_installation = True
    f.install()
    f.make_instance()
