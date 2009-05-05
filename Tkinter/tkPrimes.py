#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test zu TKinter
tkPrimes  (7.8 Beispiele) S.314
"""

from Tkinter import *
import tkMessageBox
#import sys
#if not '.' in sys.path: sys.path.insert(0,'.')
#print sys.path
from primzahlen import *

class tkPrimes:
    def __init__(self, master):
        self.master = master
        self.labEingabe = Label(master, text="Gib eine Zahl >1 ein!")
        self.entEingabe = Entry()
        self.v_rdb = IntVar()
        self.v_chb = IntVar()
        Checkbutton(master, text="Ausgabe in primes.txt umleiten?",
                    bd=1,variable=self.v_chb).grid(column=1,row=3,rowspan=3)
        self.result = StringVar()
        self.msg = Message(master,textvariable=self.result)
        self.entEingabe.grid(column=2,row=1)
        self.labEingabe.grid(column=1,row=1)
        self.msg.grid(column=1,row=2,columnspan=2)
        Radiobutton(master,text="prüfen, ob Primzahl",
                    variable=self.v_rdb,value=1,bd=1).grid(column=2,row=3)
        Radiobutton(master,text="Liste der Primzahlen angeben",
                    variable=self.v_rdb,value=0,bd=2).grid(column=2,row=4)
        Button(master, text="Berechnen",
               command=self.do,bd=1).grid(column=1,row=5)
        Button(master, text="Beenden",
               command=master.quit,bd=1).grid(column=2,row=5)
        return

    def do(self):
        global result
        try:
            a = int(self.entEingabe.get())
            if self.v_rdb.get():
                s = '%d ist %sPrimzahl' % (a,{0:'keine ',1:''}[p(a)])
                self.result.set(s)
                result = s
            else:
                result = "Primzahlen bis "+str(a)+":\n\n"+str(pListe(a))[1:-1]
                self.result.set(result)
            if self.v_chb.get():
                f = file("primes.txt",'w')
                f.write(result)
                f.close()
        except:
            tkMessageBox.showwarning("Warnung",
                        "Bitte gib erneut ein Integer >1 ein!")
            self.entEingabe.delete(0,END)

root=Tk()
primes = tkPrimes(root)
root.mainloop()
