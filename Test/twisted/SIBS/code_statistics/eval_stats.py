#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient der Auswertung der code_statistics.
"""

class Entry:
    
    keys_4 = ('date', 'revision', 'nr_commands', 'nr_todos', )
    keys_5 = ('date', 'revision', 'nr_commands', 'nr_lines', 'nr_todos', )
    
    def __init__(self, lines):
        entry = lines.splitlines()
        nr = len(entry)
        if nr == 4:
            self.__dict__.update(zip(self.keys_4, entry))
            self.nr_lines = -1
        elif nr == 5:
            self.__dict__.update(zip(self.keys_5, entry))
            self.nr_lines = int(self.nr_lines.split()[0])
        else:
            print '!!', nr

        self.revision = int(self.revision.split()[1])
        self.nr_commands = int(self.nr_commands.split()[0])
        self.nr_todos = int(self.nr_todos.split()[0])

    def __raw__(self,):
        return '%(date)s r%(revision)d\t%(nr_commands)d\t%(nr_lines)d\t%(nr_todos)d' % self.__dict__

    __str__ = __raw__
    
def read(name):
    entry = ''
    entries = []
    with open(name) as f:
        for line in f:
            entry += line
            if line.find('TODO') != -1:
                entries.append(Entry(entry))
                entry = ''
    return entries

if __name__ == "__main__":
    entries = read('statistics')
    print len(entries)
    for e in entries:
        print e
