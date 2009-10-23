#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""verarbeitet BG-Matches zu Statistiken"""

import sys
import os
import time
from StringIO import StringIO
from listen import Liste
from el_listen import Line
from optparse import OptionParser
from mgnubg import Gnubg, Match, DEBUG, OFF
from my_matches import get_matches, TIMEFMT
from archive import Archive

QUIET = __name__ != '__main__'
    
class Matches(Liste):
    """
    Matches repräsentiert eine Liste von Backgammon Matches.
    Die Matches stammen vom:
      - Filesystem
    """

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste, **kw)
        if kw and kw.has_key('tar'):
            self.archive = Archive(kw['tar'])
        else:
            self.archive = None

    def __del__(self,):
        if not QUIET:
            print 'DELETING MATCHES'
        self.close()

    def my_filter(self, **kw):
        ls = []
        for l in self._raw_liste:
            if os.path.isfile(os.path.join(kw['root'],l)) and \
               os.path.splitext(l)[1] == kw['ext']:
                ls.append(l)
        return ls        

    def purge(self,):
        """Unvollständige Matches werden aus der Liste entfernt.
            Rückgabe ist eine Liste mit den Matches; die können dann bei
            Bedarf gelöscht werden.
        """
        purged = []
        for i in self.pliste[:]:
            if not i.is_complete():
                purged.append(i)
                self.pliste.remove(i)
        return purged

    def close(self):
        if not self.archive is None:
            self.archive.close()

class MatchEntry(Line):

    def __init__(self, line, **kw):
        self.delimiter = '.'
        self.interpretation = ['match_id', 'extension']
        self.key = 'match_id'
        self.root = kw['root']
        self.parent = kw['parent']
        self.full_path = os.path.join(self.root,line)
        Line.__init__(self, line)

    def is_complete(self,):
        f = open(self.full_path)
        l = f.readline().rstrip('\n')
        f.close()
        pos = l.find('point match')
        return pos != -1

    def archive(self, no_doubles=True, retain=True):
        talk('archiviere %s' % self.full_path)
        if not self.parent.archive is None:
            self.parent.archive.append(self.full_path, no_doubles=True)
            if not retain:
                os.remove(self.full_path)

    def _str_time(self, fsec):
        tstr = ''
        if fsec:
            tstr = time.strftime(TIMEFMT,time.localtime(fsec))
        return tstr

    def process(self,):
        """Zerlegt die match_id und ermittelt 'opponent' und 'time'"""
        il = self.interpreted_line
        mi = self.match_id
        il['time'] = ''
        il['ftime'] = 0.
        il['opponent'] = mi
        pos = mi.rfind('_')
        if pos > -1:
            t = mi[pos+1:]
            if len(t) == 13:    # TODO: es fehlt die Behandlung für die andere
                il['time'] = t  #       Notation mit 20090130......
                il['ftime'] = float(t)/1000.
                mi = mi[:pos]
                if mi.startswith('You_vs_'):
                    il['opponent'] = mi[7:]
        else:                   # wenn die Zeit nicht im stamp ist,
            try:                # wird sie aus dem fstat ermittelt
                il['ftime'] = os.stat(self.full_path).st_mtime
                il['time'] = str(long(il['ftime']))+'000'
            except OSError:
                DEBUG('match-File fehlt fuer %s' % self.full_path)
            il['missing_stamp'] = True
        il['str_time'] = self._str_time(il['ftime'])
        self.time = il['time']      # TODO: die folgenden Zeilen vielleicht durch
        self.ftime = il['ftime']    #       Methode in el_listen erledigen (loop)
        self.str_time = il['str_time']
        self.opponent = il['opponent']

    def rename_match(self, new_id):
        old_path = os.path.join(self.root, self.line)
        new_match = '.'.join([new_id,self.interpreted_line['extension']])
        new_path = os.path.join(self.root, new_match)
        try:
            os.rename(old_path, new_path)
        except OSError:
            print 'WARNING: cannot rename', old_path
        else:
            self.match_id = new_id
            self.interpreted_line['match_id'] = new_id

class Config:
    
    def __init__(self, **settings):
        self.config = {}

        self.fibs_root = settings.get('fibs_root','/opt/JavaFIBS2001')
##        self.fibs_root = '/var/develop/Python/Test/gnubg'
        self.matches_root = os.path.join(self.fibs_root,'matches')
        self.set_matches()

        self.archives_root = settings.get('archives_root','')
        self.set_archives()

        self.user = settings.get('user','sorrytigger')
        self.set_user(self.user)

    def set_user(self, user):
        fibs_files_root = os.path.join(self.fibs_root,'user',user)
        matches,ratings = get_matches(fibs_files_root)
        self.add_config('matches',matches)
        self.add_config('ratings',ratings)

    def set_archives(self,):
        path = os.path.join(self.archives_root,'internal_matches.tar')
        self.add_config('internal_tar', path)
        path = os.path.join(self.archives_root,'jellyfish_matches.tar')
        self.add_config('jellyfish_tar', path)

    def set_matches(self,):
        path = os.path.join(self.matches_root,'internal')
        self.add_config('internal_matches', path)
        path = os.path.join(self.matches_root,'jellyfish')
        self.add_config('jellyfish_matches', path)

    def add_config(self, k, v):
        self.config[k] = v

    def get(self, k,):
        return self.config[k]

    def __repr__(self,):
        cfg = self.config
        out = StringIO()
        for c in cfg:
            print >> out, "%20s :: %s" % (c, cfg[c])
        return out.getvalue()

    def settings_correct(self,):
        msg = 'Config::Fehler::'
        ret = True
##        val = self.get('internal_tar')
##        val = self.get('jellyfish_tar')
##        val = self.get('ratings')
        val = self.get('matches')
        if not os.path.exists(val.full_path):
            talk('%smatches gibt es nicht (%s)' % (msg,val.full_path))
            ret = False
        for i in ('internal_matches','jellyfish_matches'):
            val = self.get(i)
            if not os.path.isdir(val):
                talk('%s%s gibt es nicht (%s)' % (msg,i,val))
                ret = False
        return ret

class Information:

    def __init__(self, config):
        self.config = config
        kw = {'ext':'.match', 'tar':config.get('internal_tar')}
        self.internal_matches = self.load_match('internal_matches', **kw)
        kw = {'ext':'.mat',}
        self.jellyfish_matches = self.load_match('jellyfish_matches', **kw)

    def __del__(self,):
        if not QUIET:
            print 'DELETING INFORMATION'
        self.internal_matches.close()
##        del self.internal_matches       # das macht er nicht, weil links auf
                                          #   parent in allen MatchEntries

    def load_match(self, matches, **kw):
        path = self.config.get(matches)
        kw['root'] = path
        match = Matches(os.listdir(path), **kw)
        match.info = path               # ist einfach der root-Pfad
##  TODO: vorige zeile finde ich überflüssig; das sollte in Matches.__init__()
##        oder sogar in Liste.__init__() (dort kw speichern) erledigt werden.
##        Das Ganze durch UNITTESTs absichern.
        match.interpret(MatchEntry,**{'root':match.info,'parent':match})
        match.list2hash()
        return match

    def mark_for_deletion(self, with_partner=False):
        """Führt intern eine Liste von Matches, die gelöscht werden sollen.
            Bei Option --delete werden diese Matches physikalisch gelöscht.
        """
        pass        # TODO: muss noch geschrieben werden

    def delete_matches(self, to_delete, delete_partner=False):
        """Verarbeitet eine Liste von MatchEntries.
            Ist die delete-Option gesetzt, so werden sie entsprechend gelöscht.
            Ist delete_partner=True, so wird der jeweilige Buddy auch gelöscht.
        """
        if not options.delete or not len(to_delete):
            return
        jellyfish = self.jellyfish_matches
        for d in to_delete[:]:
## TODO: Partner finden auslagern; das kann so von anderen auch verwendet werden
##       Außerdem: Partner in Liste schreiben und nicht hier global annehmen;
##                 damit erhält man höhere Flexibilität
##       >>Unittest!!
                                # finde den Partner in jellyfish
            jf = jellyfish.dliste.get(d.match_id)
            if jf is None:      # Wenn nicht in 'jellyfish', dann ist er
                                # incomplete (die wurden raussortiert)
                jf = MatchEntry(d.match_id+'.mat',
                            **{'root':self.config.get('jellyfish_matches'),
                               'parent':None})
                if os.path.exists(jf.full_path):
                    to_delete.append(jf)
            else:
                if not jf.is_complete():
                    to_delete.append(jf)
        for i in to_delete:
            print i.full_path
        print "Sollen die vorstehenden Matches gelöscht werden?"
        print "(Von 'saved games' muss eine Sicherheitskopie gemacht werden.)"
        ret = raw_input("Hast du an die 'saved games' gedacht? (j/J)")
        if ret.lower() in 'jy':
            for i in to_delete:
                os.remove(i.full_path)

    def clear_matches(self,):
        """Untersucht die internal/matches auf dem Filesystem auf
            'nicht in user/../matches' vorhandene.
        """
        internal = self.internal_matches
        to_delete = []
        delete_msg = {True:'und lösche ',False:''}[options.delete]
        talk("Suche %sKuckuckseier in %s" % (delete_msg,internal.info))
        for k in internal.pliste:
            k.process()
                                # identifiziere das Match in user/../matches
            jm = self.config.get('matches').match_candidates(k.opponent, k.ftime)
            if len(jm) == 0 and options.delete:
## TODO: Problem: verschone saved games
## TODO: Es ist nicht das _und_ realisiert, wie in der Anforderung beschrieben;
##        Im Moment wird das *.match hart gelöscht.
                talk("gefunden: %s" % k)
                to_delete.append(k)
            elif len(jm) > 1:
                talk('%d Kandidat(en) für %s' %(len(jm),k.match_id))
        return to_delete

    def check_matches(self,archive=False):
        """Untersucht die Matches auf dem Filesystem (i.A. internal und jellyfish)
            auf 'nicht konvertierte'. Konvertierte können archiviert werden.
        """
##    TODO:
##        - Partner auch archivieren
##        x siehe TODO archive: auf "bereits vorhanden" checken
        internal = self.internal_matches
        jellyfish = self.jellyfish_matches
        talk( """Abgleich der Verzeichnisse
  %s  (%d)
  %s  (%d)""" % (internal.info, len(internal), jellyfish.info, len(jellyfish)))
        for k in internal.pliste:
            km = k.match_id
            if not jellyfish.dliste.has_key(km):
                talk('noch nicht konvertiert: %s' % k)
            else:
                if jellyfish.dliste[km].is_complete() and archive:
                                # internal match wird nur zur Konvertierung
                                # gebraucht und kann danach gelöscht werden
                    internal.dliste[km].archive(retain=False,)
                                # jellyfish match wird noch zur Analyse
                                # gebraucht und kann daher nicht gelöscht werden
                    #jellyfish.dliste[km].archive()

    def purge_matches(self,):
        """Untersucht die Matches auf dem Filesystem (i.A. internal und jellyfish)
            auf 'unvollständige'. Treffer können gelöscht werden.
        """
        internal = self.internal_matches
        jellyfish = self.jellyfish_matches
        purged = jellyfish.purge()          # matches auf Completeness testen
        jellyfish.list2hash()               # ... und neu verschlagworten
        for p in purged:        # bei --delete hier jetzt löschen (beide matches)
            talk('purged %s' % p)
        base = os.path.basename
        split = os.path.splitext
        match_ids = map(lambda f: base(split(f.full_path)[0]), purged)
        match_ids = [m for m in match_ids if internal.dliste.has_key(m)]
        internal.remove(match_ids)          # matches aus internal löschen

    def match_time(self, match):
##        print 'keine Zeit:',
                            # TODO: match_time() sollte die neuen Methoden
                            # zur Ermittlung des Matches verwenden
                            # z.B. .....process()
                            # vielleicht auch match_candidates()
        DEBUG('match_time 1', OFF)
        fname = os.path.join(self.config.get('internal_matches'),
                             '.'.join([match.match_id, 'match']))
        mss = match.match_summary['info']['score']
        score = (mss['pl_score'],mss['opp_score'])
        opponent = mss['opponent']
        DEBUG('match_time 2', OFF)
        try:
            mtime = os.stat(fname).st_mtime
        except OSError:
##
##  TODO:
##    FEHLER: obwohl matchfile fehlt, wird die time berechnet
##            (in my_matches.get_match())
##            bitte mal überprüfen! dazu z.B. bertos.match weg moven und dann
##            test_matches laufen lassen
##
            DEBUG('match-File fehlt fuer %s' % fname)
            DEBUG('%s' % match.match_summary['info'])
            mtime = None
        jm = self.config.get('matches').get_match(opponent, mtime, score)
        DEBUG('match_time 3', OFF)
        if not jm is None:
            match.set_match_time_from_gmtime(jm.time)
            match.summary.update_info()
            msg = '%s %s %s' % (opponent, score, mtime,)
            if match.match_summary['info']['Warnings']:
                msg += ' ###'
            new_name = {'opp':jm.opponent,'time':jm.time,}
            msg += ' # You_vs_%(opp)s_%(time)s.mat' % new_name
            DEBUG(msg, OFF)
        else:
            DEBUG('++++++++++ jm is none')
        DEBUG('match_time 4', OFF)
        return jm

    def rename_time_stamp(self, gnubg, rename=False):
##        rename_time_stamps läuft nur, wenn vorher die anderen Services
##        'purge', 'check' und 'clear' durchgelaufen sind.
##        Das liegt an 'analyse = Match(...'
##
##        ich mach unten bei kommentaren mal n "A", wenn es
##        nur ein "Analyse"-Kommentar ist :)
##
        root = self.jellyfish_matches.info
        DEBUG('test_mach 1', OFF)
        matches_to_rename = []
        for match in self.jellyfish_matches.pliste:
            DEBUG('test_mach 2', OFF)
            analyse = Match(os.path.join(root,match.line), gnubg)  # match laden
            match.process()
            print match, analyse.match_time
            if analyse.match_time == '':
                jm = self.match_time(analyse)
                has_warnings = analyse.match_summary['info'].get('Warnings')
                talk('time %s, %s (%s)' % (match,jm,has_warnings))
                if not jm is None and not has_warnings:
                    internal = self.internal_matches.dliste[analyse.match_id]
                    new_tags = {'opponent':jm.opponent,'time':jm.time,}
                    analyse.rename_match(new_tags)
                    new_key = analyse.match_id
                    matches_to_rename.append(new_key)
                    if rename:
                        internal.rename_match(new_key)   # A   ist gut so
            DEBUG('test_mach 5', OFF)
            DEBUG('about to delete %s (%s)' % (analyse.match,id(analyse)), OFF)
            del analyse         # TODO: bleibt die Frage, warum das nicht gelöscht wird
##            print '-'*90
        return matches_to_rename

    def test_matches(self, gnubg):
##        test_matches läuft nur, wenn vorher die anderen Services
##        'purge', 'check' und 'clear' durchgelaufen sind
##        Das liegt an 'analyse = Match(...'
##
##        ich mach unten bei kommentaren mal n "A", wenn es
##        nur ein "Analyse"-Kommentar ist :)
##
        root = self.jellyfish_matches.info
        DEBUG('test_mach 1', OFF)
        for match in self.jellyfish_matches.pliste:
##            talk('Lade %s' % (match,))
            DEBUG('test_mach 2', OFF)
            analyse = Match(os.path.join(root,match.line), gnubg)  # match laden
##            games = analyse.analyse_games(retain=True)    # .... Spiele analysieren
##            match = analyse.analyse_match(retain=True)    # .... Match analysieren
##            DEBUG('test_mach 3', OFF)
            has_warnings = analyse.match_summary['info'].get('Warnings')
            if has_warnings:
                talk('Warnings in %s' % analyse.match)
##            DEBUG('test_mach 4', OFF)
            match.process()
##            print match.interpreted_line
            if analyse.match_time == '':
                jm = self.match_time(analyse)
                talk('time %s, %s' % (match,jm))
                if options.rename and not jm is None and not has_warnings:
                    internal = self.internal_matches.dliste[analyse.match_id]
                    new_tags = {'opponent':jm.opponent,'time':jm.time,}
                    analyse.rename_match(new_tags)
                    new_key = analyse.match_id
                    internal.rename_match(new_key)   # A   ist gut so
            DEBUG('test_mach 5', OFF)
            DEBUG('about to delete %s (%s)' % (analyse.match,id(analyse)), OFF)
            del analyse         # TODO: bleibt die Frage, warum das nicht gelöscht wird
##            print '-'*90

def talk(msg):
    if not QUIET and 'options' in globals():
        if options.verbose:
            print msg

def directory_services(information, gnubg=None):
    talk('v'*40+' purging')
    information.purge_matches()
    talk('v'*40+' check_matches()')
    information.check_matches(archive=options.archive)
    talk('v'*40+' clear_matches()')
    td = information.clear_matches()
    information.delete_matches(td, delete_partner=True)
##    return
    if not gnubg is None:
        talk('v'*40+' test_matches()')
        information.rename_time_stamp(gnubg, options.rename)
        information.internal_matches.list2hash()   # ... und neu verschlagworten
        information.jellyfish_matches.list2hash()  # ... und     WARUM?

def usage(progname):
    usg = """usage: %prog <...>
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-r", "--rename",
                  action="store_true", dest="rename", default=False,
                  help="rename matches to a name with timestamp")
    parser.add_option("-u", "--user",
                  action="store", type="string", dest="user",
                  help="base on this users matches and ratings")
    parser.add_option("-a", "--archive",
                  action="store_true", dest="archive", default=False,
                  help="archive matches that are processed already")
    parser.add_option("-c", "--config",
                  action="store_true", dest="config", default=False,
                  help="print config and exit")
    parser.add_option("-d", "--delete",
                  action="store_true", dest="delete", default=False,
                  help="delete erroneous matches")
    parser.add_option("-t", "--testing",
                  action="store_true", dest="testing", default=False,
                  help="using test configuration")
    return parser,usg

def test_configuration():       # TODO: warum liegt das nicht in tests? zB utils
    kw = {'fibs_root':'tests',
          'archives_root':'tests',
          'user':'sorrytigger'}
    return kw

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        print 'Argumente werden ignoriert'

##    if options.verbose:
##        print 'QUIET =', QUIET
##
    if options.user:
        user = options.user
    else:
        user = 'sorrytigger'

    if options.testing:
        tc = test_configuration()
        tc['user'] = user
        config = Config(**tc)
    else:
        config = Config(**{'user':user})
    if options.config:
        print config
        sys.exit(0)
    if not config.settings_correct():
        print 'Fehler in Config()'
        sys.exit(1)
    
    kdb = Information(config)
    talk('Matches geladen; internal (%d) jellyfish (%d)' % \
              (len(kdb.internal_matches), len(kdb.jellyfish_matches)))

    gnubg = None
    gnubg = Gnubg()                         # gnubg starten
##    if OFF and _DEBUG and gnubg.alive:
##        for o in gnubg.start_output:
##            print o,
####    print 'errors?', gnubg.err()

    directory_services(kdb,gnubg)

    del kdb
    del gnubg
##    time.sleep(8)


## TODOs
##
## 1) für alle Dateien in dem Directory "matches/internal":
##    wenn nicht in den user/matches zu identifizieren
##    und wenn jellyfish datei nicht is_complete
##    löschen
## 2) für alle Matches in user/matches (Option -u --user):
##    zugehörige matches/internal und jellyfish löschen (oder weglegen)
## 3) Unittests - verdammt noch mal
##    Ich hab ewig nach dem Fehler gesucht, warum der in 'matches' keine
##    Treffer mehr findet. Am Schluss wars dann die Umstellung von JavaMatches
##    auf sowohl 'matches' als auch 'ratings' (Vorbereitung). Dabei wurde ich
##    unterbrochen und hatte zwar my_matches.get_matches() bereits umgestellt,
##    aber nicht seine Aufrufe ://
##    So was müsste ein Unittest aufdecken.
####    VOR ALLEM! hatte ich auch die Config verändert. Die sollte bei jedem
####    Lauf implizit gecheckt werden!!!!!!!
## 4) Beginnen, einen Anschluss an fibs zu realisieren.
##    1) saved-games-Liste z.B. für clear_matches()
    

