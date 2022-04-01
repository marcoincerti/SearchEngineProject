import json
import sys
import time

import nltk
import tkinter as tk
import site
import os
from tkinter.scrolledtext import ScrolledText

from whoosh.qparser import QueryParser

from SearchEngine.Index import CustomIndex
from SearchEngine.Searcher import Searcher
from SearchEngine.function import AVG, ndgc_score
from SearchEngine.UIWidget import onFrameConfigure, MyDialog

ndoc = 0
size_query = 10
GO_IDCG = 14.8277  # google
WIDTH = 800
HEIGHT = 700


GO_static_rel_dict = {
    1: 6,
    2: 5,
    3: 4,
    4: 3,
    5: 2,
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 1
}

GO_id_rel_dict = {}
GO_id_list = [] * 10
SE_id_list = [] * 10
SE_title_list = [] * 10
SE_rel_list = [] * 10


def getIdGoogle(query):
    tmp_hit = 0
    index = 1
    for line in open('src/Google_data_set.json', encoding='utf8'):
        document = json.loads(line)
        if document['Query'].lower() == query.lower():
            for x in range(30):
                if tmp_hit == 10:
                    break
                if document['URL'][x][0] == "-1":
                    continue
                GO_id_list.append(document['URL'][x][0])
                GO_id_rel_dict.update({document['URL'][tmp_hit][0]: GO_static_rel_dict.get(tmp_hit + 1)})
                index += 1
                tmp_hit += 1
            break


def search_query(searcher, user_input, SE_listbox, debug=False, debug_query=None):
    GO_id_list.clear()
    GO_id_rel_dict.clear()
    SE_rel_list.clear()
    SE_id_list.clear()
    SE_listbox.delete(0, "end")

    if not debug:
        # lancio solo una query
        query_text = user_input.get()
        r = searcher.search(query_text)
        if len(r) != 0:
            getIdGoogle(query_text)
            log_OUTPUT.insert("end", "Query Eseguita: {}\n".format(r[0].getQuery()))
            log_OUTPUT.insert("end", "Termini trovati: {}\n".format(r[0].getTerms()))
        else:
            log_OUTPUT.insert("end", "Nessun risultato trovato\n")

        x=0
        for item in r:
            SE_id_list.append(item.getID())
            SE_listbox.insert("end", item.getTitle())
            x = x+1
            #print(x)
        print("GO {}".format(GO_id_list))
        AVG_SCORE = AVG(SE_id_list, GO_id_list)
        NDGC = ndgc_score(SE_rel_list)
        print(AVG_SCORE)
        print(NDGC)

    if debug:
        #lancio tutte le query
        query_text = debug_query
        r = searcher.search(query_text)
        getIdGoogle(query_text)
        for item in r:
            SE_id_list.append(item.getID())

        AVG_SCORE = AVG(SE_id_list, GO_id_list)
        for elem in SE_id_list:
            if elem in GO_id_rel_dict.keys():
                SE_rel_list.append(GO_id_rel_dict.get(elem))
            else:
                SE_rel_list.append(0)
        NDGC = ndgc_score(SE_rel_list)

        print("Query {: <28}".format(debug_query) + "AVG: {: <10}".format(AVG_SCORE) + "NDCG: {: <10}".format(NDGC))

        return AVG_SCORE, NDGC


def all_query_at_once(searcher, user_input, SE_listbox):
    log_OUTPUT.delete("1.0", tk.END)
    query_list = ["DNA", "Apple", "Epigenetics", "Hollywood", "Maya",
                  "Microsoft", "Precision", "Tuscany", "99 balloons", "Computer Programming",
                  "Financial meltdown", "Justin Timberlake", "Least Squares", "Mars robots", "Page six",
                  "Roman Empire", "Solar energy", "Statistical Significance", "Steve Jobs", "The Maya",
                  "Triple Cross", "US Constitution", "Eye of Horus", "Madam I'm Adam", "Mean Average Precision",
                  "Physics Nobel Prizes", "Read the manual", "Spanish Civil War", "Do geese see god",
                  "Much ado about nothing"]
    avg_sum = 0
    ndgc_sum = 0
    start_time = time.time()

    for query in query_list:
        avg_tmp, ndgc_tmp = search_query(searcher, user_input, SE_listbox, debug=True, debug_query=query)
        log_OUTPUT.insert("end", "Query {: <28} AVG: {: <10} NDCG: {: <10}\n".format(query, avg_tmp, ndgc_tmp))
        avg_sum += avg_tmp
        ndgc_sum += ndgc_tmp
    log_OUTPUT.insert("end", "Time: {} seconds\n".format(round(time.time() - start_time, 3)))
    log_OUTPUT.insert("end", "MAP: {: <10} NDGC MEDIA: {: <10}".format(round(avg_sum / 30, 4), round(ndgc_sum / 30, 4)))
    print("MAP: {}".format(avg_sum / 30))
    print("NDGC MEDIA: {}".format(ndgc_sum / 30))


def suggWord(query):
    token = nltk.word_tokenize(query)
    for word in token:
        suggester_word = searcher.suggestion_word(word)
        if word not in suggester_word:
            log_OUTPUT.insert("end", "Possibile errore in Query, parole consigliate {}\n".format(suggester_word))

def showHelp():
    d = MyDialog(root)
    root.wait_window(d.top)

def getText():
    document_text.delete(1.0, tk.END)
    try:

        title=SE_listbox.get(SE_listbox.curselection())
        r = searcher.search_title(title)
        document_text.insert("end", r)
    except:
        log_OUTPUT.insert("end", "Errore nella selezione della pagina")

def rollWheel(canvas, event):
    direction = 0
    if event.num == 5 or event.delta == -120:
        direction = 1
    if event.num == 4 or event.delta == 120:
        direction = -1
    canvas.yview_scroll(direction, "units")

if __name__ == '__main__':
    site.addsitedir(os.path.dirname(os.path.realpath(__file__)) + '/SearchEngine')
    index = CustomIndex()
    index.create()
    root = tk.Tk()
    background_color = "bisque2"
    root.title("Custom Search Engine")
    root.geometry("{}x{}".format(WIDTH, HEIGHT))
    root.resizable(False, True)
    canvas = tk.Canvas(root, width=WIDTH)
    frame = tk.Frame(canvas, background=background_color, width=WIDTH)
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4, 4), width=WIDTH, window=frame, anchor="nw")
    searcher = Searcher(index)
    buttonPadY = 15
    buttonPadX = 10

    p0 = tk.PanedWindow(frame, width=WIDTH, background=background_color)
    p1 = tk.PanedWindow(frame, background=background_color)
    p2 = tk.PanedWindow(frame, background=background_color)
    p3 = tk.PanedWindow(frame, background=background_color)
    p4 = tk.PanedWindow(frame, background=background_color)
    p5 = tk.PanedWindow(frame, background=background_color)
    p6 = tk.PanedWindow(frame, background=background_color)

    p0.grid()
    p1.grid()
    p2.grid()
    p3.grid()
    p4.grid(pady=5)
    p5.grid(pady=5)
    p6.grid(pady=5)

    label0 = tk.Label(p1, text="Custom Search Engine", background=background_color)
    label0.config(font=("Courier", 44))
    p1.add(label0)

    user_input = tk.Entry(width=50)
    p2.add(user_input, pady=buttonPadY)

    BTT_query = tk.Button(text="Search", relief="groove", padx=buttonPadX, command=lambda: search_query(searcher, user_input, SE_listbox))
    root.bind('<Return>', lambda action: search_query(searcher, user_input,SE_listbox))
    p3.add(BTT_query, padx=buttonPadX, pady=buttonPadY)

    BTT_all_query = tk.Button(text="Benchmark", relief="groove", padx=buttonPadX, command=lambda: all_query_at_once(searcher, user_input, SE_listbox))
    root.bind('<Shift_L>', lambda event: all_query_at_once(searcher, user_input, SE_listbox))
    p3.add(BTT_all_query, padx=buttonPadX, pady=buttonPadY)

    BTT_sugg_word = tk.Button(text="Did you mean", relief="groove", padx=buttonPadX, command=lambda: suggWord(user_input.get()))
    p3.add(BTT_sugg_word, padx=buttonPadX, pady=buttonPadY)

    BTT_help = tk.Button(text="HELP", relief="groove", padx=buttonPadX, command=lambda: showHelp())
    p3.add(BTT_help, padx=buttonPadX, pady=buttonPadY)

    label1 = tk.Label(p4, text="Search Engine Results", background=background_color)
    label1.config(font=("Courier", 20))
    label1.grid(row=0, column=0)

    SE_listbox = tk.Listbox(p4, width=50)
    SE_listbox.grid(row=1, column=0)
    SE_listbox.bind('<Double-1>', lambda event: getText())

    user_input.focus_set()

    label1 = tk.Label(p5, text="Search Engine Log", background=background_color)
    label1.config(font=("Courier", 20))
    label1.grid(row=1, column=0)

    log_OUTPUT = ScrolledText(p5, height=10)
    log_OUTPUT.grid(row=2, column=0)

    document_text = ScrolledText(p6)
    document_text.grid(row=2, column=1)
    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

    frame.bind('<MouseWheel>', lambda event: rollWheel(canvas,event))
    frame.bind('<Button-4>', lambda event: rollWheel(canvas, event))
    frame.bind('<Button-5>', lambda event: rollWheel(canvas, event))

    root.mainloop()
