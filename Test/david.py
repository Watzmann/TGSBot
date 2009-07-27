#!/usr/bin/python
# -*- coding: utf-8 -*-

liste = [('andreas','david'),
         ('andreas','helena'),
         ('andreas','annabelle'),
         ('hermann','monika'),
         ('frank','pascal'),
         ('stefan','winnie'),
         ('wilhelm','andreas')]

# Texte kommen hier hin
eingabe_text = 'gib einen Namen ein oder schreib "xxx ist der Vater von yyy": '
papa_text = 'ist der Papa von'

def print_vater_liste():
    for paar in liste:
        print '>',paar[0].capitalize(),papa_text,paar[1].capitalize()+'.'

print_vater_liste()

def vatervon(sohn):
    vater = 'unbekannt'
    for paar in liste:
        if sohn==paar[1]:
            vater = paar[0]
            break
    return vater

inp = raw_input(eingabe_text)
#print inp
while not inp == '':
    if 'vater' in inp.lower():
        a = inp.lower().split()
        print a
        print 'der Vater heißt',a[0].capitalize()
        print 'das Kind heißt',a[-1].capitalize()
        liste.append((a[0],a[-1]))
        print 'Hey - ich hab was Neues gelernt!!'
        print_vater_liste()
        inp = a[-1]
    print vatervon(inp).capitalize(),papa_text,inp.capitalize()+'.'
    inp=raw_input(eingabe_text)

    
