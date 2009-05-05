#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Komfortable Benutzung der Kommandozeile (vgl. mit optparse!)

#############

(c) Sep 2005, Andreas Hausmann
"""

import sys, getopt, os.path

def progname():
    return os.path.basename(sys.argv[0])

def usage(opts):
    print __doc__
    print """
    usage:    %s [%s] <files|folder>

       -h, --help (diese Ausgabe)
       -i, --inputpath
                Pfad, auf den sich die angegebenen Folder/Dateien beziehen.
       -o, --outputpath
                Pfad auf USB-Device.
                Default ist /media/usbdisk/mp3
       -v, --verbose

       long options werden unterstützt.
""" % (progname(),opts.listOptions())
    pp = (progname(),)*4
    print """
  examples:

    %s -v \\path...\\komponist\\album1
    %s -o \\media\\usbdisk\\mp3\\album -i \\var\\export\\Musik\\interpret\\album1 stück1 stück3 stück7
    %s -i \\var\\export\\Musik komponist\\album1
    %s -i \\var\\export\\Musik\\interpret album1 album2
""" % pp

def short_usage(opts):
    print """
    usage:    %s [%s] <files|folder>
""" % (progname(),opts.listOptions())

class commandLine:
    def __init__(self,o,argv):
        self.options = o
        try:
            if o.listOptions('longoption'):
                self.opts, self.args = \
                    getopt.getopt(argv, o.listOptions(),
                                  o.listOptions('longoption'))
            else:
                self.opts, self.args = \
                    getopt.getopt(argv, o.listOptions())
            #print '>>',o.listOptions()
            #print '>>',o.listOptions('longoption')
            #print '>>',self.opts
            #print '>>',self.args
            o.args = self.args
        except getopt.GetoptError:
            # print help information and exit:
            usage(o)
            sys.exit(2)
        self.readOptions(self.opts)
        o.optValues()

    def readOptions(self,opts):
        shortOptActions = self.options.listActions()
        #print '='*20,shortOptActions
        longOptActions = self.options.listActions('longoption')
        #print '='*20,longOptActions
        for o, a in opts:
            o = o.lstrip('-')
            action = None
            if shortOptActions.has_key(o):
                action = shortOptActions[o]
            elif longOptActions.has_key(o):
                action = longOptActions[o]
            #print '##### action #####',o,action
            if not action is None:
                if action == 'usage':
                    usage(self.options)
                else:
                    if action == 'set':
                        p = a
                    elif action == 'setTrue':
                        p = True
                    elif action == 'toggle':
                        p = not self.options.getValueByOpt(o)
                    self.options.setOptionByOpt(o,p)

    def Arguments(self):
        return self.args

    def Options(self):
        return self.options

#class commandLine(commandLineRoot):

class availableOptions:
    """Objekte dieser Klasse enthalten Informationen über die möglichen Optionen,
ihre Bezeichnungen und Texte für die usage().
Außerdem werden hier die auf der Kommondozeile tatsächlich angegebenen Optionen
eingetragen.
"""
    #todo
    # es sollten die Statusvariablen (haupt-keys von _OPTIONS) auch als
    # richtige attribute gesetzt werden
    ##ist jetzt implementiert, sollte aber noch konsistent gemacht werden
    #
    def __init__(self,options):
        self.options = options
        self.opts = {'option':"",'longoption':[]}
        self.seps = {'option':':','longoption':'='}
        self.actions = {'option':{},'longoption':{}}
        self.values = {}
        
    def listOptions(self,optType='option'):
        """Bau eine Liste von Optionen, wie sie für den getopt-Aufruf
gebraucht wird.
Mit dem Parameter 'optType' wird bestimmt, ob die Liste aus 'option' oder
'longoption' besteht (default 'option').
Bsp:
    options:  "ho:i:v"
    longopts: ["help", "outputpath=", "inputpath=", "verbose"]
"""
        opts = self.opts[optType]
        if not opts:
            sep = self.seps[optType]
            for o in self.options.keys():
                if self.options[o].has_key(optType):
                    t = self.options[o][optType]
                else:
                    continue
                if self.options[o]['arg']:
                    t += sep
                if optType == 'option':
                    opts += t
                else:
                    opts += [t]
            self.opts[optType] = opts
        return opts

    def listActions(self,optType='option'):
        """Bau eine Liste von Aktionen, wie sie für die Auswertung der
Kommandozeile gebraucht wird.
Mit dem Parameter 'optType' wird bestimmt, ob die Liste aus 'option' oder
'longoption' besteht (default 'option').
"""
        acts = self.actions[optType]
        if not acts:
            for o in self.options.keys():
                if self.options[o].has_key(optType):
                    t = self.options[o][optType]
                    a = self.options[o]['action']
                    acts[t] = a
                else:
                    continue
            self.actions[optType] = acts
        return acts

    def optValues(self,verbose=False):
        """Bau aus den Optionen und ihren Werten ein dict.
Setz die Optionen gleichzeitig als Attribute..
Damit kann aus der Anwendung heraus jederzeit die aktuelle Belegung von Status-
Variablen abgefragt werden. Diese Status-Variablen werden von beim Start über
die Kommandozeile mit Hilfe von Optionen gesetzt. Sie haben alle Defaultwerte.
Mit dem Keyword 'verbose=True' werden die Werte gleichzeitig gelistet.
"""
        values = {}
        for o in self.options.keys():
            values[o] = self.options[o]['value']
            self.__dict__[o] = self.options[o]['value']
            if verbose: print o,':',values[o]
        return values

    def getKeyByOpt(self,opt):
        key = None
        for o in self.options.keys():
            if opt == self.options[o]['option']:
                key = o
                break
            if self.options[o].has_key('longoption') and \
                        opt == self.options[o]['longoption']:
                key = o
                break
        return key

    def setOptionByOpt(self,opt,value):
        k = self.getKeyByOpt(opt)
        if k:
            self.options[k]['value'] = value
            self.__dict__[k] = value
    
    def getValueByOpt(self,opt):
        val = None
        k = self.getKeyByOpt(opt)
        if k:
            val = self.options[k]['value']
        return val
    
    def getValue(self,key):
        val = None
        if self.options.has_key(key):
            val = self.options[key]['value']
        return val
    
