import tkinter as tk
from tkinter import ttk, Button, Listbox, Entry

import pandas as pd
import numpy as np
import math
import json
import yaml
import operator

from itertools import combinations
from collections import Counter as ctr

#from nltk.corpus import stopwords
#from nltk.stem import WordNetLemmatizer
#from nltk.tokenize import word_tokenize
#from nltk.corpus import wordnet

#from numba import jit, cuda

#import query_suggestions as qs
#import candidate_resources_ranking as crr
import suggestion

LARGE_FONT = ("Verdana", 12)

#Inherits from tk.Tk
class GoFind(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        tk.Tk.wm_title(self, "GoFind")

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in(StartPage, SearchPage):
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)

        label = tk.Label(self, text="GoFind", font=LARGE_FONT)
        label.grid(row=0, column=0, sticky="w")

        self.entry = Autocomplete(self)
        #self.entry = Entry(self)
        self.entry.grid(row=1, column=0, ipadx=50, padx=.75)

        search_button = ttk.Button(self, text="Search", command=self.input_handler)#lambda: controller.show_frame(SearchPage))
        search_button.grid(row=1, column=1, padx=10)

        #self.label2 = tk.Label(self)
        #self.label2.grid(row=2, column=0, padx=.75)

    def input_handler(self):
        query = self.entry.get()
        # cand_res = crr.get_candidate_resources(query)
        # top_five = crr.relevance_ranking(query, cand_res)
        # i = 1
        # for docID in top_five:
        #     label = tk.Label(self, text=str(docID))
        #     label.grid(row=1+i, column=0)

class Autocomplete(Entry):
    def __init__(self, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()
        self.lb_up = False
        self.bind("<space>", self.changed)

    def changed(self, args):
        if self.var.get() == '':
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True

                #self.lb.delete(0, 'end')
                for w in words:
                    self.lb.insert('end', w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def comparison(self):
        pattern = self.var.get()
        return [sug for sug in suggestion.suggest(pattern)]



class SearchPage(tk.Frame):

    def __init__(self, master, controller):
        tk.Frame.__init__(self, master)
        label = tk.Label(self, text="Results", font=LARGE_FONT)
        label.grid(row=0, column=0, sticky="w")

        entry = Entry(self)
        entry.grid(row=1, column=0, ipadx=50, padx=.75) #ipadx=how long the entry is, padx=padding on the x axis

        search_button = ttk.Button(self, text="Search", command=lambda: controller.show_frame(StartPage))
        search_button.grid(row=1, column=1, padx=10)

app = GoFind()
app.geometry("1280x640")
app.mainloop()