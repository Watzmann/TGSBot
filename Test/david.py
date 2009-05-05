#!/usr/bin/python

liste = [('andreas','david'),
         ('andreas','helena'),
         ('andreas','annabelle'),
         ('hermann','monika'),
         ('frank','pascal'),
         ('stefan','winnie')]

for paar in liste:
    print paar[0].capitalize(),'ist der Papa von',paar[1].capitalize()+'.'

def vatervon(sohn):
    vater = 'unbekannt'
    for paar in liste:
        if sohn==paar[1]:
            vater = paar[0]
            break
    return vater

inp=raw_input('gib Namen ein: ')
print inp
while not inp == '':
    print vatervon(inp).capitalize(),'ist der Papa von',inp.capitalize()+'.'
    inp=raw_input('gib Namen ein: ')

    
