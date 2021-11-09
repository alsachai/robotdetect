from tkinter import *
import threading
import os

class Dialog(Toplevel):

    def __init__(self, parent, title = None):

        Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = None
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        #self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks

    def validate(self):

        return 1 # override

    def apply(self):

        pass # override

class MyDialog(Dialog):

    def body(self, master):
       master.grid_columnconfigure(0, weight=1)
       self.e1 = Entry(master)
       self.e1.grid(column=0,row=0,columnspan = 4)
       self.buttons = {}
       self.buttons['previous'] = Button(master,text =u'/')
       self.buttons['previous'].grid(column=0,row =1,columnspan = 2)

       self.buttons['next'] = Button(master,text =u'*')
       self.buttons['next'].grid(column=2,row =1,columnspan = 2)

       self.buttons['minus'] = Button(master,text =u'-')
       self.buttons['minus'].grid(column=3,row =2)

       self.buttons['plus'] = Button(master,text =u'+')
       self.buttons['plus'].grid(column=3,row =3)

       self.buttons['enter'] = Button(master,text =u'Enter')
       self.buttons['enter'].grid(column=3,row =4,rowspan = 2)

       self.buttons['zero'] = Button(master,text =u'0')
       self.buttons['zero'].grid(column=0,row =5)

       self.buttons['del'] = Button(master,text =u'←')
       self.buttons['del'].grid(column=1,row =5)
       rows = range(4,1,-1)
       columns = range(0,3)

       i = 1
       for row in rows:
              for column in columns:
                     Button(master,text = i).grid(row= row,column = column)
                     i+=1
       return self.e1 # initial focus

def leftClick():
        print('add one')

def longerClick(): #if the timer ends this will run
              d = MyDialog(master) #create dialog
              print('longerClick')

def handleButtonPress(event):
              global t
              t = threading.Timer(0.8,longerClick) #setTimer
              t.start()
              print(t)
def handleButtonRelease(event): #here is a problem probably
              global t
              t.cancel()
              leftClick()

master = Tk()
t = None
master.geometry('{}x{}'.format(300, 300))
button = Button(master, text = 'Stlac')
button.pack()
button.bind('<ButtonPress-1>',handleButtonPress)
button.bind('<ButtonRelease-1>',handleButtonRelease)
mainloop()