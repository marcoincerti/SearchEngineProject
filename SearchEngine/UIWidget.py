import tkinter as tk
from tkinter import ttk

WIDTH = 800
HEIGHT = 500


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=2, relief="solid")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

class MyDialog:

    def __init__(self, parent):

        top = self.top = tk.Toplevel(parent)

        tk.Label(top, text="Search Engine Help").pack()
        tk.Label(top, text="Il linguaggio delle query di default del search engine è il seguente").pack()
        tk.Label(top, text="[(title:token_1 OR content:token_1) AND "
                           "(title:token_2 OR content:token_2) AND "
                           "... AND (title:token_n OR content:token_n)]").pack()
        tk.Label(top, text="Ma l'utente può creare delle query personalizzate").pack()
        tk.Label(top, text="Ad esempio, se vuole effettuare una ricerca solo sul contenuto o sul titolo, "
                           "La query può essere scritta in questo modo").pack()
        tk.Label(top, text="title:query, content:query, o se vuole cercare in tutti e due, title:query OR/AND content:query").pack()
        tk.Label(top, text="Alcuni esempi di ricerca").pack()
        tk.Label(top, text="title:DNA").pack()
        tk.Label(top, text="content:Computer").pack()
        tk.Label(top, text="title:film OR content:netflix").pack()
        tk.Label(top, text="E' possibile effettuare ricerche di frasi, utilizzando la struttura \"query\"").pack()
        tk.Label(top, text="Ovvero racchiudendo tra \"\" la query dell'utente").pack()
        tk.Label(top, text="Ad esempio \"Computer Programming\" restituisce tutte le pagine che contengono Computer Programming in sequenza").pack()

        b = tk.Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):
        self.top.destroy()