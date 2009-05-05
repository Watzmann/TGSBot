#!C:\Programme\Python23\python.exe

"""Lexisnexis Dokumente in individuelle Dokumente aufteilen.

Die individuellen Dokumente werden fuer den Import durch
brainFiler aufbereitet.

(c) Feb 2005               Pylon AG  Dr. Andreas Hausmann

Zweck:
    Datenbank-Abfragen bei LexisNexis resultieren in Ascii-
    Dateien mit einer grossen Zahl von Einzeldokumenten. Zudem
    enthalten die LexisNexis-Dateien Metadaten zu den ein-
    zelnen Dokumenten. Fuer den brainFiler werden die Einzel-
    dokumente in einzelnen Dateien benoetigt.
    docSplit liest ein oder mehrere Files ein und spaltet sie
    nach einer fest programmierten Regel in einzelne Doku-
    mente auf.

Aufruf:
    docSplit steht im Sourcecode zur Verfuegung und wird des-
    halb mit python ausgefuehrt. Alternativ ist der Aufruf der
    mitgelieferten Windows-Exe moeglich:
      'python docSplit.py -h'
      'docSplit.py -h'
      'docSplit.exe -h'

Status:
    Ein oder mehrere Files werden eingelesen und aufgespalten.
    Die Metadaten werden (momentan) beim Dokument mit abge-
    speichert. Filenamen werden nach einer einfachen Regel ge-
    bildet (Ursprungsdokument plus Zaehler).
    Usage und Commandline-Interpretation ist vorhanden.
    Die Dokumentation ist noch ergaenzungsbeduerftig.
    Fehlerbehandlung ist nur ansatzweise vorhanden.
    Dieses Programm ist nur mit wenigen Szenarios getestet.

ToDo:
    Metadaten interpretieren und z.B. den Datumsstempel daraus
    bilden.
    Filenamen intelligenter bilden (z.B. aus dem Subject)

Usage:
    kann je nach Installation wie folgt aufgerufen werden:
      'python docSplit.py -h'
      'docSplit.py -h'
      'docSplit.exe -h'
    Die Ausgabe der Usage erfolgt auch, wenn gar keine
    Argumente angegeben werden.
    Sind Optionen durch einen ':' gekennzeichnet (z.B. '-w:'),
    so wird ein Parameter erwartet. Lange Optionen sind
    zulaessig.
    Bei Angabe des <fileName> sind Wildcards zulaessig. Dies ist
    in Kombination mit der Option 'workingpath' sinnvoll.
"""

import getopt, sys, os
sys.path.insert(1,'/home/andreas/Python')
from ahaLog import ahDebug, ahWarning, ahError, setLevel
setLevel (1)
import string

_OPTION = "ho:w:v:"
_LONG_OPT = ["help", "outputpath=", "workingpath=", "verbose="]

nrInput = 0
nrOutput = 0
progName = os.path.basename(sys.argv[0])

def usage():
    global progName
    print """
    usage:    %s [%s] <fileName>

      --help
       -h     help

      --verbose=
       -v:    LoggingLevel, auf den gesetzt werden soll ('0' - '5').
              Default ist '1' (='quiet').

      --outputpath=
       -o:    Pfad, in den die Zieldokumente geschrieben werden.
              Default ist current working directory.

      --workingpath=
       -w:    Pfad, in dem die Lexisnexis-Dokumente liegen.
""" % (progName,_OPTION)
    print """
  example:    %s -o ..\\brainFiler\\LexisNexis alexander_falk_.txt
              %s --outputpath="lexisNexis" --workingpath="lexis_DB" *.txt
""" % (progName,progName)

def statistics(nrInp, nrOut):
    idoc = 'Dokument'
    odoc = 'Dokument'
    over = 'vereinzelte'
    if nrInp != 1: idoc += 'e'
    if nrOut != 1: odoc += 'e'
    else: over += 's'
    print """%d %s verarbeitet.
%d %s %s geschrieben.
""" % (nrInp,idoc,nrOut,over,odoc)

def parse_cl():
    global args, progName
    try:
        opts, args = getopt.getopt(sys.argv[1:], _OPTION, _LONG_OPT)
    except getopt.GetoptError:
        # print help information and exit:
        print """Die Argumente wurden fehlerhaft angegeben.
Bitte ueberpruefen Sie die Argumente und starten Sie %s erneut.
""" % progName
        usage()
        sys.exit(2)
    global output, working
    output = None
    working = None
    for o, a in opts:
        if o in ("-v", "--verbose"):
            print __doc__
            setLevel (int(a))
        if o in ("-h", "--help"):
            print __doc__
            usage()
            sys.exit()
        if o in ("-o", "--outputpath"):
            output = a
        if o in ("-w", "--workingpath"):
            working = a

    ahDebug (4, 'opts:', opts) 
    ahDebug (4, 'args:', args) 

    # pruefe auf mindestens ein Argument
    if len(args) < 1:
        usage()
        print """Es wurden keine Dokumente angegeben!
Es wurden keine Dokumente verarbeitet!
"""
        sys.exit()

def expandList(args):
    import glob
    list = []
    global working
    for name in args:
        if working is not None and len(working) > 0:
            fname = os.path.join (working, name)
        else:
            fname = name
        # pruefe einfach auf Wildcards (i.e. '*')
        if '*' in name:
            list[len(list):] = glob.glob(fname)
        else:
            list.append(fname)
    #ahDebug (3,'expandList 1',list)
    return list

# ------------------------------------------------------------

class compoundDoc:
    
    def __init__(self, compoundFile):
        self.fileName = compoundFile
        self.firstLine = None
        self.ofDocuments = -1
        try:
            self.file = open(compoundFile, 'r')
        except IOError:
            print """
FEHLER: File '%s' wurde nicht gefunden!
""" % compoundFile

    def writeSingle(self,fileName,path=''):
        fullPath = os.path.join (path, fileName)
        f = open(fullPath, 'w')
        for line in self.single:
            #ahDebug (3, 'writeSingle:', line)
            f.write(line)
        f.close()
        ahDebug (2, 'geschrieben:', fullPath)
        return

# -------
# catchSingle()
#
#   Ein einzelnes Dokument wird eingelesen.
#   Delimiter ist die Erfuellung der Bedingungen:
#      1) die Zeile enthaelt "DOCUMENTS"
#      2) isDelimiter() == True
#         d.h.: der Aufbau der Zeile ist
#           '<numeric1> of <numeric1> DOCUMENTS'
#         <numeric2> muss immer die gleiche Zahl sein.
  
    def catchSingle(self):
        if self.firstLine is not None:
            self.single = [self.firstLine]
            self.firstLine = None
        else:
            self.single = []
        #ahDebug(3,'erste Zeile',self.single)
        while 1:
            line = self.file.readline()
            if len(line) == 0: break
            ahDebug (5, line[:-2])
            if "DOCUMENTS" in line and self.isDelimiter(line):
                self.firstLine = line
                break
            self.single.append(line)
        return len(self.single) == 0

    def isDelimiter (self, line):
        isDel = False
        parts = string.split(line)
        if parts[1] == 'of' and parts[3] == 'DOCUMENTS':
            try:
                i = int(parts[0])
                j = int(parts[2])
                if self.ofDocuments == -1: self.ofDocuments = j
                isDel = self.ofDocuments == j
                #ahDebug (3, 'Die Entscheidung: %s, %d' % (isDel,self.ofDocuments))
            except ValueError:
                pass
        ahDebug (3, 'isDelimiter:', '%d, ,%s, %s' % (nrOutput,isDel,line))
        return isDel
    
    #def extractDoc
    #def name

# ------------------------------------------------------------

def main():
    global output
    
    parse_cl()
    if output is None: output = ''

    ahDebug (3, 'output: %s' % output) 
    ahDebug (3, 'working: %s' % working) 

    global nrInput, nrOutput

    inFiles = expandList(args)
    ahDebug (3,'workingList',inFiles)
    for name in inFiles:
        cd = compoundDoc(name)
        try:
            cd.catchSingle()      # den Vorspann verwerfen (= Absender/Empfaenger)
            ahDebug (1, 'reading:', name)
            nrInput += 1
            while not cd.catchSingle():
                ahDebug (4, 'file:', cd.single) 
                nrOutput += 1
                p = os.path.basename(name).split('.')[0]
                oName = '%s_%d.txt' % (p,nrOutput)
                cd.writeSingle (oName,output)
                #if nrOutput == 1: break
        except:
            pass

if __name__ == "__main__":
    main()
    statistics (nrInput, nrOutput)

