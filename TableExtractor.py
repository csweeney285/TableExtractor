import constants
from PDFPaper import PDFPaper
import sys
import os
from GUI import _GUI

#The main method parses the given pdf file and extracts all of the table information
#Finally it saves the tables into the given table folder
#The Extract Table API Key, language, and output file are all declared in constants.py
def main(paper_name):
	paper = PDFPaper(paper_name,constants.ExtractTable_API_KEY, constants.LANGUAGE)
	print('Dict:')
	print(paper.dic)
	print('Tables:')
	print(paper.tables)
	print('Names:')
	print(paper.names)
	print('Saving Tables With Captions to:' + constants.TABLE_FOLDER)
	paper.save_tables_with_captions(constants.TABLE_FOLDER)
	print('Tables Saved!')

if __name__ == "__main__":
	#This program takes in a list of names to pdf files to parse
	os.environ['KMP_DUPLICATE_LIB_OK']='True'
	# for i in sys.argv[1:]:
	# 	main(i)
	gui = _GUI()