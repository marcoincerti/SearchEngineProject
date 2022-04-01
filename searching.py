from whoosh.index import open_dir
from whoosh import highlight
import PySimpleGUI as sg
from threading import Thread
from queue import Queue
import time
from myIndexSearcher import getQueryResults
from whoosh.analysis import Filter
from nltk.stem.lancaster import LancasterStemmer
import myutils

# Creating a Queue to store the results of the SearchThread
resultsQueue = Queue()

lancStemmer = LancasterStemmer()

class LancasterStemFilter(Filter):
    """
    Using the NLTK Lancaster Stemmer
    """
    def __call__(self, tokens):
        for t in tokens:
            t.text = lancStemmer.stem(t.text)
            yield t

# Creating a personal Formatter to highlight the matched terms in the queries fragments
class BoldFormatter(highlight.Formatter):
    #Puts ~ around the matched terms and transforms them in bold text.

    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the token
        tokentext = highlight.get_text(text, token, replace)

        # Return the string uppercased and surrounded by ~
        return " ~%s~ " % tokentext.upper()

# Creating a Thread to search a query in the Index
class SearchThread (Thread):
    def __init__(self, index, query, numDocs, numKeywords, searcher, resultsQueue):
        Thread.__init__(self)
        self.index = index
        self.query = query
        # Number of documents to be returned
        self.numDocs = numDocs
        self.numKeywords = numKeywords
        self.searcher = searcher
        self.resultsQueue = resultsQueue
		
    def run(self):
        start_time = time.time()
        keywords = []
        queryResults,  keywords, correctedStringQuery = getQueryResults(self.index, self.query, self.numDocs, self.searcher, numKeywords=self.numKeywords, returnCorrectedQuery=True)
        query_time = time.time() - start_time
        queryResults.fragmenter.charlimit = 80000
        # Allow larger fragments
        queryResults.fragmenter.maxchars = 250
        # Show more context before and after
        queryResults.fragmenter.surround = 45
        # Set the Formatter for the matches in fragments
        queryResults.formatter = BoldFormatter()
        # Set the order of relevance of the returned fragment (FIRST/SCORE)
        queryResults.order = highlight.SCORE
        
        titleToShow = []
        textToShow = []
        for hit in queryResults:
            titleToShow.append(hit['title'])
            textHighlights = hit.highlights("content", top=3)        
            if textHighlights == '':
                textToShow.append(hit['content'][:200])
            else:
                textToShow.append(textHighlights)
        
        if len(titleToShow) > 0:
            textToDisplay = ''.join(str(i + 1) + '. Title: ' + titleToShow[i] + '\n\n' + textToShow[i] + '\n\n' for i in range(0, len(titleToShow)))
        else:
            textToDisplay = ''
        if keywords == None:
            keywordsToDisplay = ''.join(keyword + " - " for keyword in queryResults.key_terms("title", docs=self.numDocs, numterms=self.numKeywords))
        else:
            keywordsToDisplay = ''.join(keyword + " - " for keyword in keywords)
        
        resultsQueue.put(queryResults)
        resultsQueue.put(correctedStringQuery)
        resultsQueue.put(textToDisplay)
        resultsQueue.put(keywordsToDisplay)
        resultsQueue.put(query_time)
        total_time = time.time() - start_time
        resultsQueue.put(total_time)
        print(query_time)
        print(total_time)
        
def getLayout():
    # Sets the theme of the GUI
    sg.theme('DarkAmber')
    # All the stuff inside the GUI window.
    return [  [sg.Text('Query:'), sg.InputText(key='-INPUTEXT-'), sg.Text('N°:'), sg.Spin([i for i in range(1,31)], initial_value=10, key='-INPUTRESULTS-')],
                [sg.Button('Search'), sg.Button('Reset'), sg.Button('Close')],
                [sg.Text(size=(0,1), key='-OUTPUTCORRECTEDQUERY-'), sg.Button('Correct', disabled=True, key='-CORRECTBUTTON-')],
                [sg.Text('Results:')],
                [sg.Multiline(key='-OUTPUTRESULTS-', size=(80, 25), disabled=True)],
                [sg.Text('Query time:'), sg.Text('0.00 sec.', key='-OUTPUTQUERYTIME-'), sg.Text('Total time:'), sg.Text('0.00 sec.', key='-OUTPUTTOTALTIME-')],
                [sg.Text('Suggested Keywords:'), sg.Spin([i for i in range(1,11)], initial_value=5, key='-INPUTKEYWORDS-')],
                [sg.Multiline(key='-OUTPUTKEYWORDS-', size=(80, 1), disabled=True)]]
        
if __name__ == "__main__":

    # Create the Window
    window = sg.Window('Goggle', getLayout())
    
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        # If user closes window or clicks cancel
        if event in (None, 'Close'):	
            break
        
        if event in ('-CORRECTBUTTON-'):
            window['-INPUTEXT-'].update(correctedStringQuery)
            window['-OUTPUTCORRECTEDQUERY-'].update('')
            window['-CORRECTBUTTON-'].update(disabled=True)
            continue
        
        # If user clicks the Reset button
        if event in ('Reset'):
            window['-INPUTEXT-'].update('')
            window['-INPUTRESULTS-'].update(10)
            window['-INPUTKEYWORDS-'].update(5)
            window['-OUTPUTCORRECTEDQUERY-'].update('')
            window['-CORRECTBUTTON-'].update(disabled=True)
            continue
        
        # If user clicks the Search Button but no query is entered
        if values['-INPUTEXT-'] == '':
            sg.Popup('No query entered!')
            continue
            
        # Check if the Input field of the number of documents to be retrivied is correct
        if values['-INPUTRESULTS-'] == '':
            sg.Popup('No number of documents retrivied entered!')
            continue
        if not type(values['-INPUTRESULTS-']) == int:
            if not values['-INPUTRESULTS-'].isdigit():
                sg.Popup('Number of documents retrivied should be an integer.')
                continue				
            elif int(values['-INPUTRESULTS-']) < 1 or int(values['-INPUTRESULTS-']) > 30:
                sg.Popup('Number of documents retrivied should be between 1 and 30.')
                continue
        
        # Check if the Input field of the number of keyword to be retrivied is correct
        if values['-INPUTKEYWORDS-'] == '':
            sg.Popup('No number of keywords retrivied entered!')
            continue
        if not type(values['-INPUTKEYWORDS-']) == int:
            if not values['-INPUTKEYWORDS-'].isdigit():
                sg.Popup('Number of keywords retrivied should be an integer.')
                continue				
            elif int(values['-INPUTKEYWORDS-']) < 1 or int(values['-INPUTKEYWORDS-']) > 10:
                sg.Popup('Number of keywords retrivied should be between 1 and 10.')
                continue
        
        ix = open_dir(myutils.currentIndex_path)
        searcher = ix.searcher()
        searcherThread = SearchThread(ix, values['-INPUTEXT-'], int(values['-INPUTRESULTS-']), int(values['-INPUTKEYWORDS-']), searcher, resultsQueue)
        searcherThread.start()
        
        # While the thread is searching, show a loading gif
        while searcherThread.is_alive():
            sg.PopupAnimated(image_source=myutils.loadingGif_path, message="Searching...", background_color='black', alpha_channel=1, time_between_frames=75)
        
        # Close the Animated Popup with the loading gif when the thread ends
        sg.PopupAnimated(None)
        # Get the threadSearch results from the Queue passed to the thread
        results = resultsQueue.get()
        correctedStringQuery = resultsQueue.get()
        textToDisplay = resultsQueue.get()
        keywordsToDisplay = resultsQueue.get()
        queryTime = resultsQueue.get()
        totalTime = resultsQueue.get()
        
        if len(results) == 0:
            window['-OUTPUTRESULTS-'].update('Empty result!')
        else:
            # Prints on the screen the search results and 3 fragments of text from each one of the pages retrivied
            window['-OUTPUTRESULTS-'].update(textToDisplay)
            # Prints on the screen a certain number of Keywords, to help the User expanding his query
            window['-OUTPUTKEYWORDS-'].update(keywordsToDisplay)
            # Prints on the screen the Query Time
            window['-OUTPUTQUERYTIME-'].update(str(queryTime)[:4] + " sec.")
            # Prints on the screen the Total Time
            window['-OUTPUTTOTALTIME-'].update(str(totalTime)[:4] + " sec.")

        searcher.close()

        if correctedStringQuery != None:
            window['-OUTPUTCORRECTEDQUERY-'].update('Did you mean "' + correctedStringQuery + '" ' + '?')
            window['-CORRECTBUTTON-'].update(disabled=False)
        else:
            window['-OUTPUTCORRECTEDQUERY-'].update('')
            window['-CORRECTBUTTON-'].update(disabled=True)
            
    window.close()