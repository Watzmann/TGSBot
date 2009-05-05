#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tkinter explorieren und testen;
nach dem Buch Python 2.x von Uzak."""

from Tkinter import *

class Book:
    def __init__(self, root):
        self.tk = root

    def label1(self, tk):
        tk.label = Label(tk,width=30,text="Demonstration-Label")
        tk.label.pack()
        return tk.label

    def label2(self, tk):
        labels = ['eins','zwei','drei','vier']
        packs = ['','side=LEFT','side=RIGHT','side=BOTTOM,fill=X',]
        both = dict(zip(labels,packs))
        for i in both:
            exec "tk.%s = Label(tk,text='%s',relief=RIDGE)" % (i,i)
            exec "tk.%s.pack(%s)" % (i,both[i])
        return

    def message(self, tk):
        string = 'langer Text, \n\n \
                    der über mehrere Zeilen geht!'
        tk.message = Message(tk, text=string)
        tk.message.pack()
        return

    def radiobut(self, tk):
        tk.value = IntVar(tk)
        v = tk.value
        Radiobutton(tk, text='Option 1', variable=v, value=0).pack()
        Radiobutton(tk, text='Option 2', variable=v, value=1).pack()
        return

    def checkbut(self, tk):
        tk.v1 = IntVar(tk)
        tk.v2 = IntVar(tk)
        tk.v3 = IntVar(tk)
        Checkbutton(tk, text='Option 1', variable=tk.v1).pack()
        Checkbutton(tk, text='Option 2', variable=tk.v2).pack()
        Checkbutton(tk, text='Option 3', variable=tk.v3).pack()
        return

    def image(self, tk):
        img = '/home/hausmann/Bilder/AHa.Doc/STE/Logo-STE-v-1/STE-Logo-198x121.gif'
        tk.grafik = PhotoImage(file=img)
        tk.image = Label(tk,image=tk.grafik)
        tk.image.pack()
        return

# Funktionen für den Button ---------------------------------------------

    def fun1(self):
        tk = self.tk
        e = tk.entry.get()
        tk.descr.set(e)
##        print 'ich setze e',e
        return 2

    def fun2(self):
        tk = self.tk
        e = tk.value.get()
        tk.descr.set('Wahl: %d' % e)
##        print 'hello World!:',e
        return 2

    def fun3(self):
        tk = self.tk
        e1 = tk.v1.get()
        e2 = tk.v2.get()
        e3 = tk.v3.get()
        tk.descr.set('Set: %d %d %d' % (e1,e2,e3))
##        print 'hello World!:',e
        return 2

    def init_stepper(self,new_steps):
        # new_steps ist eine Liste von Sätzen von Kommandos (Zugriffe
        # auf die Optionen, ...) für den stepper()
        # bei jedem Button-Press wird der nächste Satz (per exec) ausgeführt
        self.steps = dict(zip(range(len(new_steps)),new_steps))
        self.step = 0

    def stepper(self):
        tk = self.tk
        if self.steps.has_key(self.step):
            for a in self.steps[self.step]:
                exec a
        self.step += 1
        return 2

# -----------------------------------------------------------------

    def button(self, tk, fun=None):
        if fun:
            tk.button = Button(tk, text="Say Hello!", command=fun)
            # hier darf 'fun' nicht mit Klammern geschrieben werden 'fun()'!!
            # dann wird natürlich der return-Wert für command eingesetzt
        else:
            tk.button = Label(tk, text="kein FUN definiert!")
        tk.button.pack(side=BOTTOM,fill=X)
        return

    def entry(self, tk):
        tk.entry = Entry(tk,width=30)
        tk.entry.pack()
        return

    def strvar(self, tk):
        tk.descr = StringVar(tk)
        tk.labelstr = Label(tk, textvariable=tk.descr)
        tk.labelstr.pack()
        return

    def grid(self, tk):
        Label(tk,text='Benutzername').grid(row=1,column=1)
        Label(tk,text='Passwort').grid(row=2,column=1)
        Entry(tk).grid(row=1,column=2,columnspan=3)
        Entry(tk).grid(row=2,column=2,columnspan=3)
        Checkbutton(tk,text='Passwort speichern?').grid(row=3,column=1)
        Button(tk,text='Abbrechen').grid(row=3,column=4)
        Button(tk,text='Bestätigen').grid(row=3,column=3)
        return

    def frame(self, tk):
        tk.links = Frame(tk)
        tk.rechts = Frame(tk)
        tk.links.pack(side=LEFT)
        tk.rechts.pack(side=RIGHT)
        Label(tk.links,text='Benutzername').grid(row=1,column=1)
        Label(tk.links,text='Passwort').grid(row=2,column=1)
        Entry(tk.links).grid(row=1,column=2,columnspan=3)
        Entry(tk.links).grid(row=2,column=2,columnspan=3)
        Message(tk.rechts,text='Info ...').pack()
        Button(tk.rechts,text='Bestätigen').pack()
        Button(tk.rechts,text='Abbrechen').pack()
        return

    def toplevel(self, tk):
        Label(tk,text="Tk()",width=30).pack()
        self.tk2 = Toplevel()
        Label(self.tk2,text="Toplevel()",width=30).pack()
        Button(self.tk2,text='Quit',command=tk.quit).pack()
        # Toplevel is a child of TK
        return
#-----
    def handler(self, event):
        print "Ereignisart:",event.type

    def event1(self, tk):
        tk.event1_label = Label(tk,text="Klick mich")
        r = tk.event1_label.bind("<Button-1>", self.handler)
        tk.event1_label.pack()
        return r
#-----
    def descrEvent(self, event):
        print "Koordinaten: %sx, %sy" % (event.x, event.y)
        print "Taste %s" % event.char
        print "MausTaste %s" % str(event.num)
        print "Höhe: %s\tBreite: %s" % (event.width, event.height)
        print type(event.width)
    
    def testEvent(self,tk):
        tk.event2_label = Label(tk,text="Demo Label",width=30)
        tk.event2_label.bind("<Button-1>", self.descrEvent)
        tk.event2_label.bind_all("<space>", self.descrEvent)
        tk.event2_label.bind_all("<Control-q>", self.descrEvent)
        tk.event2_label.bind_all("<a>", self.descrEvent)
        tk.event2_label.pack()
        return
#-----
    def handler2(self, event):
        print "Wahl: %s (%s)" % (self.tk.listbox.get(ACTIVE),`self.tk.listbox.curselection()`)

    def listbox(self,tk):
        tk.listbox = Listbox(tk,selectmode=SINGLE)
        tk.listbox.insert(END,"Anfang")
        for a in ['eins','zwei','drei','vier']:
            tk.listbox.insert(END,a)
        tk.listbox.see(4)
        tk.listbox.bind("<Double-Button-1>", self.handler2)
        tk.listbox.pack()
        return
#-----
    def text1(self,tk,hght=10):
        tk.text = Text(tk,width=80,height=hght)
        tk.text.pack()
        return
#-----
    def callback(self,event):
        print "... Aktion ..."
        return
#-----
    def canvas(self,tk,):
        tk.canvas = Canvas(tk,width=400,height=400,bg="white")
        tk.canvas.pack()
        return
#-----
    def scrollbar(self,tk,):
        tk.scrollbar = Scrollbar(tk)
        tk.scrollbar.pack(side=RIGHT,fill=Y)
        return

    def listbox2(self,tk,sc):
        tk.listbox2 = Listbox(tk,yscrollcommand=sc.set)
        for a in range(1000):
            tk.listbox2.insert(END,str(a))
        tk.listbox2.pack(side=LEFT,fill=BOTH)
        return
#-----
    def scrollbar_x(self,tk,):
        tk.scroll_x = Scrollbar(tk,orient=HORIZONTAL)
        tk.scroll_x.pack(side=BOTTOM,fill=X)
        return
    
    def text2(self,tk,sx,sy):
        tk.text2 = Text(tk,width=30,height=15,bg="white",wrap=NONE,
                       yscrollcommand=sy.set,xscrollcommand=sx.set)
        tk.text2.pack(side=LEFT,fill=BOTH)
        return
#-----

def do_strvar(book):
    root = book.tk
    book.strvar(root)
    book.entry(root)
    book.button(root, book.fun1)
    return

def do_radio(book):
    root = book.tk
    book.strvar(root)
    book.radiobut(root)
    book.button(root, book.fun2)
    return

def do_check(book):
    root = book.tk
    book.strvar(root)
    book.checkbut(root)
    book.button(root, book.fun3)
    return

def do_options(book):
    root = book.tk
    book.strvar(root)
    label = book.label1(root)
    steps = [
        ["e = tk.label.cget('text')","tk.descr.set('Text: %s' % e)"],
        ["tk.label.config(width=40)",
         "tk.label['height']=20",
         "tk.descr.set('Dimensionen gesetzt')"],
        ["tk.label['text']='Bunter Demo String'",
         "tk.label['fg']='red'",
         "tk.label['bg']='blue'",
         "tk.descr.set('Farben gesetzt')"],
        ["tk.label['font']=('helvetica',18,'italic','bold')",
         "tk.descr.set('Schnitt, ... gesetzt')"],
        ["tk.label['bd']=7",
         "tk.label['relief']=GROOVE",
         "tk.descr.set('Rahmen gesetzt')"],
        ["tk.descr.set('Feddich')","tk.quit()"],
        ]
    book.init_stepper(steps)
    book.button(root, book.stepper)
    return

def do_layout_pack(book):
    """7.4 Layout-Manager (Pack) 275"""
    root = book.tk
    book.strvar(root)
    book.label2(root)
    steps = [
        ["tk.eins.pack_configure(fill=BOTH)",
         "tk.descr.set('eins.pack_configure(fill=BOTH)')"],
        ["tk.zwei['height']=5",
         "tk.descr.set(\"zwei['height']=5\")"],
        ["tk.drei.pack_configure(fill=Y)",
         "tk.descr.set('frei.pack_configure(fill=Y)')"],
        ["tk.descr.set('Feddich')","tk.quit()"],
        ]
    book.init_stepper(steps)
    book.button(root, book.stepper)
    # keine Layout-Manager (z.B. pack und grid) mischen!!!!
    return

def do_layout_grid(book):
    """7.4 Layout-Manager (Grid) 278"""
    root = book.tk
    # keine Layout-Manager (z.B. pack und grid) mischen!!!!
    book.grid(root)
    # jetzt die slaves lesen und für alle relief=ridge setzen
    return

def do_frame(book):
    """7.5 Oberflächen (Frame) 281"""
    root = book.tk
    book.frame(root)
    # jetzt die slaves lesen und für alle relief=ridge setzen
    return

def do_toplevel(book):
    """7.5 Oberflächen (Toplevel) 282"""
    root = book.tk
    book.toplevel(root)
    root.iconify()
    root.title("Tk()-Oberfläche")
    print root.geometry()
    print book.tk2.geometry()
    return

def do_messageBox():
    """7.5 Oberflächen (Dialogfelder) 283"""
    import tkMessageBox
    # nicht in den gleichen Namensraum mit Tkinter importieren
    # ... also beide mit from....import *
    fname=r"noneexistent.file"
    tkMessageBox.showwarning("Datei öffnen",
                             "Datei kann nicht geöffnet werden\n(%s)" % fname)
    return

def do_fileDialog():
    """7.5 Oberflächen (Dialogfelder) 285"""
    import tkFileDialog, tkMessageBox
    # nicht in den gleichen Namensraum mit Tkinter importieren
    # ... also beide mit from....import *
    r = tkFileDialog.askopenfilename()
    r = tkMessageBox.showinfo("Ergebnis", "gewählte Datei ist\n%s" % r)
    print r
    return

def do_event1(book):
    """7.6 Ereignisse 287"""
    import tkFileDialog, tkMessageBox
    root = book.tk
    r = book.event1(root)
    r = tkMessageBox.showinfo("Ergebnis", "Returnwert ist\n%s" % r)
    print r
    return

def do_descrEvent(book):
    """7.6 Ereignisse 290"""
    root = book.tk
    book.testEvent(root)
    return

def do_listbox(book):
    """7.7 Komplexe Widgets (ListBox) 292"""
    root = book.tk
    book.listbox(root)
    print root.listbox.size()
    print root.listbox.get(1)
    return

def do_text(book):
    """7.7 Komplexe Widgets (Text) 294"""
    root = book.tk
    book.strvar(root)
    book.text1(root)
    tx = root.text
    for a in range(10):
        tx.insert(END,">\n")
    tx.insert("1.end","Erste Zeile")
    tx.insert("3.end","Dritte Zeile")
    tx.insert(END,"Letzte Zeile")
    steps = [
        ["tk.text.delete('3.0','3.end')",
         "tk.descr.set('text.delete(3.0,3.end)')"],
        ["b = tk.text.get('1.0','1.end')",
         "tk.descr.set('text.get(1.0-end): %s' % b)"],
        ["tk.text.see(END)",
         "tk.descr.set('text.see(END)')"],
        ["tk.descr.set('ENDE')"],
        ["tk.quit()"],
        ]
    book.init_stepper(steps)
    book.button(root, book.stepper)
    return

def do_marke(book):
    """7.7 Komplexe Widgets (Text Marken) 297"""
    root = book.tk
    book.strvar(root)
    book.text1(root,25)
    tx = root.text
    for a in range(24):
        tx.insert(END,"%03d" % (a+1) + ". Zeile\n")
    tx.mark_set("eins","1.end")
    tx.mark_set("drei","3.5")
    steps = [
        ["tk.text.insert('drei','-'*20)",
         "tk.descr.set('text.insert(`drei`,`-`*20)')"],
        ["tk.text.delete('1.0','eins')",
         "tk.descr.set('text.delete(1.0,eins)')"],
        ["print tk.text.mark_names()",
         "print tk.text.index('current')"],
        ["tk.descr.set('ENDE')"],
        ["tk.quit()"],
        ]
    book.init_stepper(steps)
    book.button(root, book.stepper)
    return

def do_tags(book):
    """7.7 Komplexe Widgets (Text Tags) 299"""
    root = book.tk
    book.text1(root,15)
    tx = root.text
    for a in range(24):
        tx.insert(END,"%03d" % (a+1) + ". Zeile\n")
    tx.tag_add("eins","1.0","1.end")
    tx.tag_add("zwei","2.0","2.end")
    tx.tag_add("drei","3.0","3.end")
    tx.tag_add("vier","4.0","4.end")
    tx.tag_add("funf","5.0","5.end")
    tx.tag_add("rest","6.0",END)
    tx.tag_add("alls","0.0",END)
    font = "Helvetica 14 bold"
    tx.tag_config("alls",background="aliceblue")
    tx.tag_config("eins",foreground="red")
    tx.tag_config("eins",font=font)
    tx.tag_config("zwei",lmargin1=10)
    tx.tag_config("drei",justify=CENTER,font=font)
    tx.tag_config("drei",overstrike=1)
    tx.tag_config("vier",rmargin=30,justify=RIGHT)
    tx.tag_config("rest",lmargin1=10,spacing1=5)
    tx.tag_bind("alls","<Button-1>",book.callback)
    return

def do_canvas(book):
    """7.7 Komplexe Widgets (Canvas) 302"""
    root = book.tk
    book.strvar(root)
    book.canvas(root,)
    tx = root.canvas
    tx.bogen = tx.create_arc(2,2,200,200,fill="red")
    tx.linie = tx.create_line(100,150,250,150)
    tx.ei = tx.create_oval(180,180,120,320,fill="orange")
    tx.viereck = tx.create_rectangle(250,250,350,350)
    tx.label1 = tx.create_text(300,300,text="4eck",font="Helvetica 10 bold")
    label2 = tx.create_text(150,140,text="linie")
    steps = [
        ["tk.descr.set('NEXT: canvas.delete(ei)')"],
        ["tk.canvas.delete(tk.canvas.ei)",
         "r = tk.canvas.itemcget(tk.canvas.bogen,'fill')",
         "tk.descr.set('canvas.itemcget(bogen,`fill`) %s' % r)"],
        ["tk.descr.set('NEXT: canvas.itemconfig(viereck,fill=`green`)')"],
        ["tk.canvas.itemconfig(tk.canvas.viereck,fill='green')",
         "r = tk.canvas.coords(tk.canvas.bogen)",
         "tk.descr.set('canvas.coords(bogen) %s' % str(r))"],
        ["tk.descr.set('canvas.coords(bogen,150,150,400,400)')"],
        ["r = tk.canvas.coords(tk.canvas.bogen,150,150,400,400)",
         "tk.descr.set('canvas.lift(bogen)')"],
        ["r = tk.canvas.lift(tk.canvas.bogen)",
         "tk.descr.set('canvas.lower(label1)')"],
        ["r = tk.canvas.lower(tk.canvas.label1)",
         "tk.descr.set('canvas.move(linie,-30,50)')"],
        ["r = tk.canvas.move(tk.canvas.linie,-30,50)",
         "tk.descr.set('ENDE')"],
        ["tk.quit()"],
        ]
    book.init_stepper(steps)
    book.button(root, book.stepper)
    return

def do_scrollbar(book):
    """7.7 Komplexe Widgets (Scrollbar) 306"""
    root = book.tk
    book.scrollbar(root,)
    scbar = root.scrollbar
    book.listbox2(root,scbar)
    scbar.config(command=root.listbox2.yview)
    return

def do_xscroll(book):
    """7.7 Komplexe Widgets (Scrollbar in X-Richtung) 308"""
    root = book.tk
    book.scrollbar_x(root,)
    book.scrollbar(root,)
    sx = root.scroll_x
    sy = root.scrollbar
    book.text2(root,sx,sy)
    sx.config(command=root.text2.xview)
    sy.config(command=root.text2.yview)
    data = file("/etc/hosts").read()
    root.text2.insert(END,data)
    return

# -------------------------------------------------------

def do_menu(book):
    """7.7 Komplexe Widgets (Menu) 309"""
##    root = book.tk
##    book.scrollbar_x(root,)
##    book.scrollbar(root,)
##    sx = root.scroll_x
##    sy = root.scrollbar
##    book.text2(root,sx,sy)
##    sx.config(command=root.text2.xview)
##    sy.config(command=root.text2.yview)
##    data = file("/etc/hosts").read()
##    root.text2.insert(END,data)
    return

class Docs:
    """Sammelt Doc-Strings aus einer dir()-Liste nach bestimmten Kriterien.
Ausgabe ist sortiert und unsortiert möglich.
"""
    # Utility-würdig!!!!!!!!
    
    def __init__(self,symbols):
        """Nimmt eine Liste aus dir(), filtert nach einem Kriterium
(hier noch fest ".startswith('do_')" und legt ein dict an.
"""
        d = {}
        for i in symbols:
            if not i.startswith('do_'): continue
            try:
                exec "d['"+i+"']="+i+".__doc__"
            except:
                pass
        self._docs = d

    def list_docs(self,):
        """Ausgabe der Liste von Doc-Strings"""
        for i in self._docs.keys():
            print '%15s:  %s' % (i,self._docs[i])

    def list_docs_sorted(self,):
        """Sortierte Ausgabe der Liste von Doc-Strings"""
        d = {}
        r = []
        for i in self._docs.keys():
            if self._docs[i]:
                a = self._docs[i].split()
                try:
                    d[a[-1]] = i
                except:
                    pass
            else:
                r.append(i)
        a = d.keys()
        a.sort()
        for i in r:
            print '%15s:  None' % (i,)
        for i in a:
            print '%15s:  %s' % (d[i],self._docs[d[i]])

if __name__ == "__main__":
    Docs(dir()).list_docs_sorted()
    root = Tk()
    book = Book(root)
    do_xscroll(book)
    root.mainloop()
