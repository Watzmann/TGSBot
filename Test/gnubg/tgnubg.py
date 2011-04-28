#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""analysiert BG-Matches mit Aufruf von 'gnubg -t'"""

import os
import time
import re
import types
from StringIO import StringIO
from subprocess import Popen, PIPE
from my_shelve import Shelve

OFF = True
_DEBUG = True
def DEBUG(msg, ON=True):
    if _DEBUG and ON:
        print '##', msg

class Summary(Shelve):

    def __init__(self, info, match):
        Shelve.__init__(self, 'gnubg.db')
        self.data = {}
        self.data['info'] = info
        key = info.get('match_id')
        self.data['key'] = key
        self.preset = self.has_key(key)
        if self.preset:
            self.data = self.read(key)
            DEBUG('read data from %s' % key, OFF)
        self.match = match
        self.listing = match.listing
        self.touched = False       # flag shows, whether must be written back
##        print 'LOADED', self.match.match, id(self)

    def __del__(self,):
##        print 'KILL', self.match.match, id(self)
        pass

    def compose_summary(self,):
        """Return dictionary with match summary"""
        summary = self.data
        summary['evaluation'] = self.evaluation()
        return summary

    def evaluation(self,):
        """Do special evaluations on the Summary"""
        evl = {}
        try:
            match = self.data['match']
        except KeyError:
            key = self.data['info'].get('match_id')
            DEBUG('kein Match vorhanden in %s' % (key,),)
            evl['global'] = ('kein Match vorhanden',0)
        else:
            f = lambda x: float(match['global'][x][0].rstrip('%').replace(',','.'))
            if match['global'].has_key('result') and \
               match['global'].has_key('lucky_result'):
                r = f('result')
                lr = f('lucky_result')
                summe = abs(r + lr)
                text = "Glücklich gewonnen"     # TODO: das ist noch quatsch text!!!!
                if summe >= 50:
                    evl['lucky_win'] = (0, text)
                else:
                    evl['lucky_win'] = (int((r+lr)/summe), text)
                DEBUG('res-luckres %s (%s)' % (evl['lucky_win']),OFF)
        return evl

    def update_info(self,):
        old_info = self.data.get('info')
        self.data['info'] = None
        new_info = self.match.match_info(retain=True)
        if not old_info is None:
            old_info.update(new_info)
            self.data['info'] = old_info

    def str_analysis(self, analysis):
        """Returns given analysis as string"""
        out = StringIO()
        for i,lst,part in self.listing:
            d = analysis[part]
            print >> out, '-'*7, lst.title
            for l,k in lst:
                if d.has_key(k):
                    p,o = d[k]
                    ul = l.decode('utf8')
                    up = p.decode('utf8')
                    uo = o.decode('utf8')
                    line = '%-49s% 22s |% 24s' % (ul,uo,up)
                    print >> out, line.encode('utf8')
        return out.getvalue()

    gewonnen = {True:'GEWONNEN',False:'VERLOREN',}

    def str_info(self, info=None):
        """Return match information as a formatted string"""
        if info is None:
            info = self.match.match_info(retain=True)
        out = StringIO()
        print >> out, 'Info für das Match     %s' % info['match_id']
        print >> out, 'Datum: %s' % self.match.str_time(info['match_time'])
        scr = info['score']
        print >> out, '%s  gegen  %s      %s' % (scr['player'],scr['opponent'],
                               self.gewonnen[scr['pl_score']>scr['opp_score']])
        print >> out, 'ML %s     Stand %s:%s       %s Spiele    (%s)' % \
                      (scr['matchlength'],scr['pl_score'],scr['opp_score'],
                       scr['nr_of_games'],scr['crawford'])
        return out.getvalue()

    def touch(self):
        self.touched = True

    def write(self, forced=False):
        if self.touched or forced:
            Shelve.write(self,self.data['key'],self.data)
            self.flush()
            self.touched = False
    
class Match:
    
    class Listing:

        splitter = re.compile('\s\s+')

        def __init__(self, title, lst):
            self.title = title
            self.listing = lst
            self.dlisting = dict(lst)

        def get(self, description, values):
            if self.dlisting.has_key(description):
                key = self.dlisting[description]
                v = values
            else:
                DEBUG('Searching# %s (%s)' % (description,values), OFF)
                for i,k in self.listing:
                    if description.startswith(i):
                        key = self.dlisting[i]
                        values = '  ' + (description+values)[len(i):]
                        DEBUG('%s (%s)' % (values,self.splitter.split(values)), OFF)
                        break
            v = self.splitter.split(values)
            try:
                ov = v[1]
                pv = v[2]
            except:
                ov = v[0]
                pv = '###'
            return key,ov.strip(),pv.strip()

        def __iter__(self,):
            return iter(self.listing)

    listing_player = Listing('Gegner',(
        ('Spieler','opponent'),
        ))
    listing_checker = Listing('Statistk des Chequer-Spiels',(
        ('Züge insgesamt','moves'),
        ('Nichtforcierte Züge','nonforced_moves'),
        ('nichtmarkierte Züge','nonmarked_moves'),
        ("Züge, die mit 'gut' bewertet wurden",'move_good'),
        ("Züge, die mit 'zweifelhaft' bewertet wurden",'move_doubt'),
        ("Züge, die mit 'schlecht' bewertet wurden",'move_bad'),
        ("Züge, die mit 'sehr schlecht' bewertet wurden",'move_rotten'),
        ("Fehler-Rate (insgesamt)",'error_rate'),
        ("Fehler-Rate (pro Zug)",'error_per_move'),
        ('Rating des Chequer-Spiels','rating_checker'),
        ))
    listing_luck = Listing('Statistiken des Glücks',(
        ("Würfe, die mit 'sehr glücklich' bewertet wurden",'very_lucky_move'),
        ("Würfe, die mit 'glücklich' bewertet wurden",'lucky_move'),
        ("Nichtbewertete Würfe",'unrated_move'),
        ("Würfe, die mit 'unglücklich' bewertet wurden",'unlucky_move'),
        ("Würfe, die mit 'sehr unglücklich' bewertet wurden",'very_unlucky_move'),
        ("Glücks-Rate (insgesamt)",'luck_rate'),
        ("Glücks-Rate (pro Zug)",'luck_per_move'),
        ("Glücks-Rate",'luck_rating'),
        ))
    listing_cube = Listing('Doppler-Statistiken',(
        ("Alle Doppler-Entscheidungen:",'all_cube_decisions'),
        ("Knappe oder tatsächliche Doppler-Entscheidungen",'cube_decisions'),
        ("Doppel",'double'),
        ("Annahmen",'take'),
        ("Aufgaben",'drop'),
        ("Verpasste Doppel (unter CP)",'missed_under'),
        ("Verpasste Doppel (über CP)",'missed_above'),
        ("Falsche Doppel (unter DP)",'wrong_under'),
        ("Falsche Doppel (über TG)",'wrong_above'),
        ("Falsche Annahmen",'wrong_take'),
        ("Falsche Ablehnungen",'wrong_drop'),
        ("Fehler-Rate (insgesamt)",'double_rate'),
        ("Fehler-Rate (pro Doppler-Entscheidung)",'error_per_decision'),
        ("Rating der Doppler-Entscheidungen",'double_rating'),
        ))
    listing_global = Listing('Gesamtstatistiken',(
        ("Fehler-Rate (insgesamt)",'global_error'),
        ("Fehler-Rate (pro Entscheidung)",'global_rate'),
        ("Gleichw. 'Snowie Error rate'",'snowie_rate'),
        ("Rating (insgesamt)",'global_rating'),
        ("Tatsächliches Resultat",'result'),
        ("Resultat korrigiert um die Glücks-Rate",'lucky_result'),
        ("Glücksbasierter Unterschied im FIBS Rating",'fibs_rating_luck'),
        ("Fehlerbasiertes absolutes FIBS Rating",'fibs_rating_error'),
        ("Ratingverlust durch Chequer-Spiel",'checker_loss'),
        ("Ratingverlust durch Doppler-Entscheidungen",'cube_loss'),
        ))
    listing = (((0,1),listing_player,'info'),
               ((2,14),listing_checker,'checker'),
               ((16,26),listing_luck,'luck'),
               ((28,44),listing_cube,'cube'),
               ((46,58),listing_global,'global'),
               )

    def __init__(self, match=None, gnubg=None, match_id=None):
##        OFF = True
        self.match = match
        self.gnubg = gnubg
        if not match is None:
            self.match_id = os.path.splitext(os.path.basename(match))[0]
        else:
            self.match_id = match_id
        self.match_time = self.time(self.match_id)
        self.score = {}   #self.gnubg.score
        self.match_summary = {}
        self.match_info()
        if not gnubg is None:
            gnubg.loaded_match = False
##        print self.match_summary['info']
        if self.match_summary['info']['score'] == {}:
            self.load_match()
        DEBUG('MATCH::info erstellt (%s)' % id(self), OFF)

    def __del__(self,):
        print 'DELETING',self.match
        del self.summary

    def save(self,):
        self.summary.write(forced=True)     # TODO: diesen 'forced' hack überprüfen
        DEBUG('MATCH::saved %s' % self.match, OFF)

    def load_match(self,):
        if not ((self.gnubg is None) or (self.match is None)):
            info = self.gnubg.load(self.match)
            DEBUG('MATCH::loaded', OFF)
            self.score = self.gnubg.score
            self.match_summary['info'] = None
            self.match_info()
            self.match_summary['info']['Warnings'] = len(self.gnubg.warnings) > 0
            self.save()
        else:
            # kann sein, dass diese Abfrage überflüssig ist; sie wurde eingefügt,
            # um einen Fehler in eval_db zu korrigieren; danach wurde dort der
            # Fehler behoben.
            DEBUG('tried to load with gnubg==%s::match==%s' % (self.gnubg,self.match), )
        
    def analysis(self, typ='game'):
        if not self.match_loaded():
            self.load_match()
        analysis_text = self.gnubg.analyse(typ=typ)
        analysis = {}
        if _DEBUG and False:
            for e,s in enumerate(analysis_text):
                print e,s,
        for i,lst,part in self.listing:
            analysis[part] = {}
            ansys = analysis[part]
            b,e = i
            at = analysis_text[b:e]
            for e,s in enumerate(at):
                r = s.find('  ')
                key = '+++'
                v = '\n'
                if r > -1:
                    a,v = s[:r],s[r:]
                    key,ov,pv = lst.get(a,v)
                    ansys[key] = (pv,ov)
                    v = '>>>%s::%s<<<\n' % (ov,pv)
                if _DEBUG and False:
                    print e,key,v,
        self.format(analysis)
        return analysis

    format_strings = {'Mehr Gl':5,'Du soll':7}

    def format(self, analysis):
        d = analysis['cube']
        p,o = d['missed_under']
        d['missed_under'] = (p.rstrip('\n'),o)
        p,o = d['missed_above']
        d['missed_above'] = (p.rstrip('\n'),o)
        
        d = analysis['luck']
        v = d.get('luck_rating',)
        if not v is None:
            p,o = v
            if self.format_strings.has_key(o[:7]):
                l = self.format_strings[o[:7]]
                a = o.split()
                o = ' '.join(a[:l])
                p = ' '.join(a[l:])
            d['luck_rating'] = (p,o)

    def analyse_games(self, retain=False):
        games = self.match_summary.get('games')
        if not retain or games is None:
            games = []
            for g in range(1,int(self.score['nr_of_games'])+1):
                DEBUG('Analyse Spiel', OFF)
                analysis = self.analysis(typ='game')
                analysis['info']['game'] = g
                DEBUG('das war das %d. Spiel' % g, OFF)
                games.append(analysis)
            self.match_summary['games'] = games
            self.save()
        return games

    def analyse_match(self, retain=False):
        match = self.match_summary.get('match')
        if not retain or match is None:
            DEBUG('Analyse Match', OFF)
            match = self.analysis(typ='match')
            match['info']['match'] = True
            self.match_summary['match'] = match
            self.save()
        return match

    def match_info(self, retain=False):
        """Return dictionary with match information"""
##        OFF = True
## TODO
##    - die match_time wird für alle als second since epoch abgespeichert
##      sie kann von dort leicht umgerechnet werden
##    - es werden die zugehoerigen ratings (hinterher) abgespeichert
##    - in den my_matches werden die ratings und matches verwaltet
##      - sie sollten beide die gleiche get_match-funktion haben, mit der man
##        die Zuordnung machen kann
##    - die match_id kann vielleicht nach gnubg.pdf kap. 11.7 geschnitzt werden
        info = self.match_summary.get('info')
        if info is None:
            info = {}
            info['match_id'] = self.match_id
            info['match_time'] = self.match_time
            info['score'] = self.score
            DEBUG('match_info 1', OFF)
            if not retain:
                DEBUG('match_info 2', OFF)
                self.summary = Summary(info, self)
                self.match_summary = self.summary.data
                self.score = self.match_summary['info'].get('score')
                DEBUG('match_info 3', OFF)
        return info

    def str_time(self, mtime=''):
        if not mtime:
            mtime = self.match_time
        DEBUG('mtime: %s' % (mtime,), OFF)
        if len(mtime) == 5:
            (year,month,day,hour,mnt) = mtime
            return '%02d.%02d.%4d %02d:%02d' % (day,month,year,hour,mnt)
        else:
            return '- kein Datum -'
    
    def time(self, stamp):
        p = stamp.rfind('_')
        if p == -1:
            return ''
        stamp = stamp[p+1:]
        if len(stamp) < 13:
            return ''
        DEBUG('in time: stamp %s' % stamp, OFF)
        if stamp[0] == '2':         # Diese einfache Abfrage gilt bis April 2033
            year = int(stamp[:4])
            month = int(stamp[4:6])
            day = int(stamp[6:8])
            hour = int(stamp[8:10])
            mnt = int(stamp[10:12])
        else:
            t = float('%s.%s' % (stamp[:-3],stamp[-3:]))
            year,month,day,hour,mnt,z,z,z,z = time.gmtime(t)
        DEBUG('Datum: %d.%d.%d %d:%d' % (day,month,year,hour,mnt),OFF)
        return (year,month,day,hour,mnt)

    def set_match_time_from_gmtime(self, stamp):
        if type(stamp) is types.StringType:
            stamp = float('%s.%s' % (stamp[:-3],stamp[-3:]))
        year,month,day,hour,mnt,z,z,z,z = time.gmtime(stamp)
        self.match_time = (year,month,day,hour,mnt)

    def _compose_match_id(self, tags):
        return 'You_vs_%(opponent)s_%(time)s' % tags

    def rename_match(self, new_tags):
        # TODO: das hier sollte mitsamt _compose_match_id() nach
        # control.MatchEntry.rename_match() wandern.
        # Was ist dann mit dem update von self.summary.update_info()
        new_id = self._compose_match_id(new_tags)
        old_path = self.match
        path = os.path.dirname(old_path)
        ext = os.path.splitext(old_path)[1]
        new_path = os.path.join(path,new_id+ext)
        DEBUG('match %s # match_id %s\nnew_id %s\nnew_match %s' %(self.match,self.match_id,new_id,new_path), OFF)
        try:
            os.rename(old_path, new_path)
        except OSError:
            print 'WARNING: cannot rename', old_path
        else:
            self.match = new_path
            self.match_id = new_id
            self.summary.update_info()

    def match_loaded(self):
        return self.gnubg.loaded_match

class Gnubg:

    load_cmd = """import mat %s
show score\n"""
    analyse_cmd = """analyse match\n"""
    statistics_cmd = {'match':(61,"""show statistics match\n"""),
                      'game':(57,"""show statistics game\n"""),
                      }
    reset_cmd = """previous game %s\n"""
    next_cmd = """next game %s\n"""
    score_line = re.compile("Der Spielstand \(nach (\d+?) Partien?\) ist: (\D+) (\d+), (\D+) (\d+) \(Match auf (\d+) Punkte?(, )?(\D*)\)")
    score_interpretation = ('nr_of_games','opponent','opp_score',
                            'player','pl_score','matchlength','xxx','crawford',)

    def __init__(self,):
        arg = 'gnubg -tq'
        DEBUG('starting gnubg', OFF)
        self.gnubg = Popen(arg,shell=True,stdin=PIPE,stdout=PIPE,stderr=PIPE)
        DEBUG('setting Pipes', OFF)
        self.stdin = self.gnubg.stdin
        self.stdout = self.gnubg.stdout
        self.stderr = self.gnubg.stderr
        DEBUG('reading', OFF)
        self.start_output = self.start()
        DEBUG("gnubg running with '%s'" % (arg,), OFF)
        self.alive = True
        self.loaded_match = False
        self.score = {}
##        err = self.err()
##        print 'error?', err

    def load(self, match):
        #OFF = True
        DEBUG('loading %s' % match, OFF)
        self.warnings = []
        cmd = self.load_cmd % match
        DEBUG('command: %s' % cmd, OFF)
        self.write(cmd)
        ret = self.read(17)
        self.loaded_match = True
        DEBUG('done loading', OFF)
        DEBUG('info: %s' % ret[-1], OFF)
        self.score = self.scores(ret[-1])
        DEBUG('score: %s' % self.score, OFF)
        self.analysed_match = False
        self.reset()
        return ret

    def analyse(self, typ='game'):
        DEBUG('in Gnubg().analyse', OFF)
        ret = []
        if not self.loaded_match:
            DEBUG('nothing to analyse')
            return ret
        if not self.analysed_match:
            DEBUG('analysing', OFF)
            self.write(self.analyse_cmd)
            self.analysed_match = True
        nr,cmd = self.statistics_cmd[typ]
        DEBUG('analyse cmd: %s' % cmd, OFF)
        self.write(cmd)
        ret = self.read(nr)
        self.write(self.next_cmd % 1)
        return ret

    def scores(self, score):
        scr = self.score_line.search(score)
        if scr is not None:
            ret = scr.groups()
            DEBUG('scr:: %s' % scr,OFF)
        else:
            ret = []
            DEBUG('score:: %s' % score)
        if len(ret) != len(self.score_interpretation):
            DEBUG('STRANGE SCORE: %s' % (ret,))
            ret = {}
        else:
            ret = dict(zip(self.score_interpretation,ret))
            del ret['xxx']
        return ret

    def reset(self,):
        nr = self.score.get('nr_of_games',0)
        DEBUG('reset: %s' % (nr,), OFF)
        if self.loaded_match and nr > 0:
            cmd = self.reset_cmd % nr
            self.write(cmd)
        return

    def write(self, msg):
        self.stdin.write(msg)
 
    def start(self,stop="ESD"):
        OFF = False
        ret = []
        while True:
            r = self.stdout.readline()
            ret.append(r)
            DEBUG('##%s##' % (r,), OFF)
            if r.startswith(stop):
                break
        return ret

    def read(self,n=0,stop="Keine Partie"):
        #OFF = True
        ret = []
        last_line_empty = False
        last_lines = 0
        i = n
        while i > 0:
            DEBUG('%d reading' % i, OFF)
            i -= 1
            r = self.stdout.readline()
            while r.startswith('WARNUNG: ') or \
                  r.startswith('Nicht erkannter Zug '):
                w = r.rstrip('\n')
                self.warnings.append(w)
                DEBUG('!! %s' % w, OFF)
                r = self.stdout.readline()
            if r.startswith('Bist Du sicher'):
                self.write('y\n')
                self.write('show score\n')
                self.stdout.readline()
                self.stdout.readline()
                self.stdout.readline()
                r = self.stdout.readline()
            if r.startswith(' +13-14-15-16-17-18'):
                if r.rstrip('\n').endswith('You'):
                    i = 2
            ret.append(r)
            DEBUG('## (%d) %s##' % (last_lines,r), OFF)
            if len(r) == 1:
                if last_line_empty:
                    if last_lines == 2:
                        self.warnings.append('SELBSTSTÄNDIG LESEVORGANG ABGEBROCHEN')
                        return ret
                    last_lines += 1
                else:
                    last_line_empty = True
                    last_lines = 1
            else:
                last_line_empty = False
                last_lines = 0
        return ret

##    def _prompt(self, output):
##        p = output.rfind('(')
##        if p > -1:
##            DEBUG('found: %s' % output[p:])
##        ret = p > -1 and 'Partie' in output[p:]
##        return ret
##
##    def read_experimental(self,n=0):
##        ret = StringIO()
##        WRITE=False
##        while True:
##            r = self.stdout.read(1)
##            ret.write(r)
##            DEBUG(ret.getvalue(),WRITE)
##            if r == ')':
##                WRITE=True
##            if r == ')' and self._prompt(ret.getvalue()):
##                break
##        return ret.getvalue()

    def err(self,):
        return self.stderr.readline()

    def close(self):
        DEBUG('CLOSING GNUBG')
        self.write('quit\n')
        self.write('exit\n')

    def __del__(self):
        self.close()

if __name__ == '__main__':
    root = '/opt/JavaFIBS2001/matches/jellyfish'
    my_match = 'You_vs_Zauberin______1223657045028.mat'
    root = '/opt/JavaFIBS2001/matches/jellyfish/old'
    my_match = 'You_vs_zumsel_20090508152945242.mat'
    #my_match = 'mrekeles.mat'
##    my_match = 'You_vs_yup_1219395387151.mat'   LESEFEHLER
    match = os.path.join(root,my_match)
##    match = '/opt/JavaFIBS2001/matches/jellyfish/You_vs_ANAHITA_1214292435807.mat'
##    match = '/share/XFer/fibs/share/jellyfish/You_vs_maria_20090102132552563.mat'
##    print 'instantiate Gnubg()'
    gnubg = Gnubg()                         # gnubg starten
    if OFF and _DEBUG and gnubg.alive:
        for o in gnubg.start_output:
            print o,
##    print 'errors?', gnubg.err()
##    analyse = Match(match, gnubg)           # match laden
##    my_match = 'You_vs_zulu_1224540880473.mat'
##    match = os.path.join(root,my_match)
    analyse = Match(match, gnubg)           # match laden
    games = analyse.analyse_games(retain=True)  # .... Spiele analysieren
    match = analyse.analyse_match(retain=True)  # .... Match analysieren
    summary = analyse.summary
    print summary.str_info()
    DEBUG('analysierte %d Games' % len(games))
    print '='*90
    smry = summary.compose_summary()
    for g in smry['games']:
        print summary.str_analysis(g)
        print '-'*90
    print '='*90
    print summary.str_analysis(smry['match'])
##    print '='*90
##    print 'The keys of Summary',smry.keys()
    del analyse.gnubg
    del gnubg
##    time.sleep(8)
