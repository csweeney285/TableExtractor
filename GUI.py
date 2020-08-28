from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import constants
from PDFPaper import PDFPaper

#Custom Scrollable List class
class ScrollableList(Scrollbar):

    def __init__(self, root):
        super().__init__()
        self.listbox = Listbox(root, exportselection=0)
        self.listbox.pack(side = LEFT, fill = BOTH)
        self.listbox.config(yscrollcommand = self.set) 
        self.config(command = self.listbox.yview)

    def insert(self, index, *elements):
        return self.listbox.insert(index, *elements)

    def get(self, first, last=None):
        return self.listbox.get(first,last)

    def current_selection(self):
        return self.get(self.listbox.curselection())

    def activate_default(self):
        self.listbox.select_set(0)

#This is a graphical user interface in order to run and test our TableExtractorParser
class _GUI:
    def __init__(self):
    	#Setup GUI
        self.root = Tk()
        self.root.title('PDF Table Caption Extractor')

        #Instructions
        instruction_text = "This is a simple GUI for running our Table Caption Extractor software. Simply choose a pdf file that you would like to parse for table captions and wait for the results."

        self.instructions = Message(self.root, text=instruction_text, relief=RAISED, width = 1250)
        self.instructions.pack(side = TOP, fill = BOTH, expand = True)

        #Languages
        self.language_list = ScrollableList(self.root)
        self.language_list.pack(side = LEFT, fill = BOTH) 
        self.language_dict = {'English': 'en' ,'Abaza' : 'abq', 'Adyghe' : 'ady', 'Afrikaans' : 'af', 'Angika' : 'ang', 'Arabic' : 'ar', 'Assamese' : 'as', 'Avar' : 'ava', 'Azerbaijani' : 'az', 'Belarusian' : 'be', 'Bulgarian' : 'bg', 'Bihari' : 'bh', 'Bhojpuri' : 'bho', 'Bengali' : 'bn', 'Bosnian' : 'bs', 'Simplified Chinese' : 'ch_sim', 'Traditional Chinese' : 'ch_tra', 'Chechen' : 'che', 'Czech' : 'cs', 'Welsh' : 'cy', 'Danish' : 'da', 'Dargwa' : 'dar', 'German' : 'de', 'Spanish' : 'es', 'Estonian' : 'et', 'Persian (Farsi)' : 'fa', 'French' : 'fr', 'Irish' : 'ga', 'Goan Konkani' : 'gom', 'Hindi' : 'hi', 'Croatian' : 'hr', 'Hungarian' : 'hu', 'Indonesian' : 'id', 'Ingush' : 'inh', 'Icelandic' : 'is', 'Italian' : 'it', 'Japanese' : 'ja', 'Kabardian' : 'kbd', 'Korean' : 'ko', 'Kurdish' : 'ku', 'Latin' : 'la', 'Lak' : 'lbe', 'Lezghian' : 'lez', 'Lithuanian' : 'lt', 'Latvian' : 'lv', 'Magahi' : 'mah', 'Maithili' : 'mai', 'Maori' : 'mi', 'Mongolian' : 'mn', 'Marathi' : 'mr', 'Malay' : 'ms', 'Maltese' : 'mt', 'Nepali' : 'ne', 'Newari' : 'new', 'Dutch' : 'nl', 'Norwegian' : 'no', 'Occitan' : 'oc', 'Polish' : 'pl', 'Portuguese' : 'pt', 'Romanian' : 'ro', 'Russian' : 'ru', 'Serbian (cyrillic)' : 'rs_cyrillic', 'Serbian (latin)' : 'rs_latin', 'Nagpuri' : 'sck', 'Slovak (need revisit)' : 'sk', 'Slovenian' : 'sl', 'Albanian' : 'sq', 'Swedish' : 'sv', 'Swahili' : 'sw', 'Tamil' : 'ta', 'Tabassaran' : 'tab', 'Thai' : 'th', 'Tagalog' : 'tl', 'Turkish' : 'tr', 'Uyghur' : 'ug', 'Ukranian' : 'uk', 'Urdu' : 'ur', 'Uzbek' : 'uz'}
        
        #Only display the full names of the languages and not the acronyms needed for the TableExtractor
        for k in self.language_dict.keys():
            self.language_list.insert(END, k)
        self.language_list.activate_default()

        #Label to display the chosen pdf file
        self.file_label = Message(self.root, text="No File Selected", relief=RAISED, width = 1250)
        self.file_label.pack(side = TOP, fill = BOTH, expand = True)
		
		#Button
        self.button = Button(self.root, text ="Select File", command = self._select_file)
        self.button.pack(side = TOP)

        #Response
        #Where we will print out the results of the extractor
        self.response = Message(self.root, text= "", relief=RAISED)
        self.response.pack(side = BOTTOM, fill = BOTH)

        self.root.mainloop()

    
    def _select_file(self):
        #allow the user to select a pdf to parse
    	self.filename = askopenfilename()
     
        #verify that the file is a pdf and if not prompt a warning
    	if not self.filename.endswith('.pdf'):
    		show_method = getattr(messagebox, 'show{}'.format('warning'))
    		show_method("Invalid Input", "This program requires a PDF file to analyze.")
    	else:
    		self.file_label.configure(text = self.filename)
    		language_key = self.language_list.current_selection()
    		language = self.language_dict.get(language_key)
    		paper = PDFPaper(self.filename,constants.ExtractTable_API_KEY, language)
    		_add_to_response('Dict:')
    		_add_to_response(paper.dic)
    		_add_to_response('Tables:')
    		_add_to_response(paper.tables)
    		_add_to_response(paper.names)
    		_add_to_response('Saving Tables With Captions to:' + constants.TABLE_FOLDER)
    		paper.save_tables_with_captions(constants.TABLE_FOLDER)
    		_add_to_response('Tables Saved!')
    
    #custom print method in order to print the results in the response message container
    def _add_to_response(text):
    	self.response.configure(text = self.response.text + '\n' +str(text))



