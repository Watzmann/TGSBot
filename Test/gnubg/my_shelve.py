#!/usr/bin/python
# -*- coding: utf-8 -*-

# 

import shelve
import time

class Singleton:

    __instance = None

    def __init__(self,):
        si = Singleton.__dict__['_Singleton__instance']
##        print '-',si,id(si)
        if si is None:
##            print 'n',self,si
            Singleton.__dict__['_Singleton__instance'] = self
##            print 'n',self,si
            self.id = time.time()
##            print 'n',self,si
##        print Singleton.__dict__

    def handle(self,):
        return self.__instance

##    def __getattr__(self, attr):
##        """ Delegate access to implementation """
##        print 'in getattr with',attr
##        return getattr(self.__instance, attr)
##
##    def __setattr__(self, attr, value):
##        """ Delegate access to implementation """
##        print 'in setattr with',attr,value
##        return setattr(self.__instance, attr, value)
        
class DB(Singleton):

    __db = None

    def __init__(self, db_path='local_shelve'):
        Singleton.__init__(self)
        if self.__db is None:
            self.__db = shelve.open(db_path)
            
##    def __del__(self):
##        """Destruktor; DB schließen."""
##        print 'DB WIRD NICHT GESCHLOSSEN'
##        self.db.close()

    def db(self,):
        return self.__db
        
class Shelve:
    
    def __init__(self, db_name):
        """
        Öffnet die Datenbank und stellt sie über die folgenden Methoden zur
        Verfügung.
        """
        self.db = DB(db_name).handle().db()
##        print 'erstelle DB mit der id',id(self.db)
##        print 'und den keys', self.db.keys()

    def __del__(self,):
        print 'deleting shelve $$$$$$$$$$$$$$$$$$$$$$$$$$$'
        
    def read(self, key):
        """
        Holt den Datensatz zu 'key' aus der DB;
        gibt Datensatz oder 'None' zurück.
        """
        return self.db[key]
        
    def write(self, key, value):
        """Schreibt den Datensatz unter 'key' in die DB"""
##        print key,value
##        print 'Id der DB',id(self.db),type(self.db)
        self.db[key] = value
        
    def delete(self, key):
        """Löscht den Datensatz unter 'key' in der DB"""
        del self.db[key]

    def keys(self,):
        """Gibt eine Liste von 'keys' zurück"""
        return self.db.keys()

    def has_key(self, key):
        return self.db.has_key(key)

    def flush(self,):
        self.db.sync()

class PersDict(Shelve):

    def __init__(self, key=None, data=None, db_name='dbshelve'):
        Shelve.__init__(self, db_name)
        if data is None:
            if not key is None:
                self.data = self.read(key)
        else:
            if key is None:
                key = getattr(data,'key')
            print 'schreibe',key,data
            self.write(key,data)
            self.data = data

    def __del__(self,):
        print 'DB WIRD GESYNCT'
        self.db.sync()        

def explore():
    filename = 'dbshelve'

    d = shelve.open(filename) # open -- file may get suffix added by low-level
                              # library

    data1 = {'a': [1, 2.0, 3, 4+6j],
             'b': ('string', u'Unicode string'),
             'c': None}

    selfref_list = [1, 2, 3]
    selfref_list.append(selfref_list)

    key = 'data1'
    data = data1

    d[key] = data   # store data at key (overwrites old data if
                    # using an existing key)
    data = d[key]   # retrieve a COPY of data at key (raise KeyError if no
                    # such key)
    flag = d.has_key(key)   # true if the key exists
    klist = d.keys() # a list of all existing keys (slow!)

    del d[key]      # delete data stored at key (raises KeyError
                    # if no such key)

    # as d was opened WITHOUT writeback=True, beware:
    d['xx'] = range(4)  # this works as expected, but...
    d['xx'].append(5)   # *this doesn't!* -- d['xx'] is STILL range(4)!!!

    # having opened d without writeback=True, you need to code carefully:
    temp = d['xx']      # extracts the copy
    temp.append(5)      # mutates the copy
    d['xx'] = temp      # stores the copy right back, to persist it

    # or, d=shelve.open(filename,writeback=True) would let you just code
    # d['xx'].append(5) and have it work as expected, BUT it would also
    # consume more memory and make the d.close() operation slower.

    d.close()       # close it

def test_shelve():
    print 'DB anlegen'
    db = Shelve('dbshelve')
    
    data1 = {'a': [1, 2.0, 3, 4+6j],
             'b': ('string', u'Unicode string'),
             'c': None}

    selfref_list = [1, 2, 3]
    selfref_list.append(selfref_list)

    key = 'data1'
    data = data1
    db.write(key,data)
    print db.read(key)

    db.write('selfref',selfref_list)
    print db.read('selfref')
    try:
        print db.read('selfre')
    except KeyError:
        print 'nicht gefunden'
    for k in db.keys():
        print k
        print db.read(k)
    
    #del db

def test_persist():
    d = PersDict(key='hallo', data={'hallo':1,'beta':4})
    print 'data', d.data
    print id(d.db)
    print d.db.keys()
    #d.db.close()
##    del d.db    

if __name__ == "__main__":

##    explore()
    
##    h1 = DB().singleton()
##    print '+'*70
##    time.sleep(2)
##    h2 = DB().singleton()
##
##    print h1.id, id(h1)
##    print h2.id, id(h2)

    test_shelve()
    test_persist()
    d = PersDict(key='hallo', data={'hallo':7,'beta':4})
    print d.db.keys()
