from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import cv2
from google.colab.patches import cv2_imshow
import numpy as np
import pandas as pd
import os

import itertools
import easyocr
from ExtractTable import ExtractTable
from Page import _Page


class PDFPaper:
    def __init__(self, pdf_path, key, language):
        self.pdf_path = pdf_path
        self.language = language
        self.num_pages, self.folder_name = self._pdf_save_images()
        self.table_folder = self.folder_name + '/table'
        self.table_cnt = self._table_recog2img()
        self.dic = self._check_caption()
        self.tables, self.names = self._match_table_captions(key)

    #Public Methods:
    #This function save tables(dataframe) as csv files with a dictionary which mapps the csv names to table captions 
    def save_tables_with_captions(to_folder):
        names = self.names
        tables = self.tables
        dic = self.dic
        if not os.path.isdir(to_folder):
            os.mkdir(to_folder)
        for i in range(len(tables)):
            tables[i].to_csv(to_folder+names[i]+'.csv', index=False)
        caps = [dic[x] for x in names]
        dic2 = {'name': names, 'caption candidates':caps}
        pd.DataFrame(dic2).to_csv(to_folder + 'caps.csv', index=False)

    #Private Methods:
    #This function saves images for each page in the pdf paper under to_path
    def _pdf_save_images(self, to_path='./'):
        base = os.path.basename(self.pdf_path)
        paper_name = os.path.splitext(base)[0]
        folder = to_path + paper_name 
        if not os.path.isdir(folder):
            os.mkdir(folder)
        images = convert_from_path(self.pdf_path)
        index = 0
        for image in images:
          index += 1
          image.save(folder + "/page_" + str(index) + ".jpg")
        print('# pages: ', index)
        return index, folder

    #This function creates _Page object for each page image,
    #gets the images for tables in it and updates the count for tables in the whole pdf paper
    def _table_recog2img(self):
        if not os.path.isdir(self.table_folder):
            os.mkdir(self.table_folder)
        table_cnt = 0
        for i in range(1, self.num_pages+1):
            image_path = self.folder_name + '/page_'+str(i)+'.jpg'
            page = _Page(image_path, i)
            table_cnt = page.table_recog2img_one_page(self.table_folder, table_cnt)  
        return table_cnt

    #This function checks each candidate image for tables 
    #and removes images that cannot be recognized to have captions
    #It return a dictionary which map the image name (table index) to the corresponding captions
    def _check_caption(self):
        dic = {}
        for img in os.listdir(self.table_folder):
            if img.startswith('total'):
                page = int(img.split('_')[2]) 
                reader = easyocr.Reader([self.language])
                text_list = reader.readtext(self.table_folder + '/' + img)
                if len(text_list) == 0:
                    path1 = self.table_folder+ '/'+img
                    path2 = self.table_folder+ '/'+img[6:] 
                    os.remove(path1)
                    os.remove(path2)
                else:
                    box_co = [text[0][0] for text in text_list]
                    row_list = self._get_row(box_co, text_list)
                    clist = self._caption(list(itertools.chain.from_iterable(row_list)))
                    if len(clist) != 0:
                        dic[img[6:]] = clist
                    else:
                        path1 = self.table_folder+ '/'+img
                        path2 = self.table_folder+ '/'+img[6:] 
                        os.remove(path1)
                        os.remove(path2)
        return dic
      
    #This function recognizes the content of tables in the images and returns the dataframe of the content   
    def _get_table_content(self, table_path, key):
        et_sess = ExtractTable(api_key=key)
        dfs = et_sess.process_file(filepath=table_path, output_format="df")
        return dfs[0]


    #This function gets the content of recognized tables with the corresponding image names (table index)
    def _match_table_captions(self, key):
        tables = []
        names = []
        for img in os.listdir(self.table_folder):
            if img.startswith('page') and img.endswith('.jpg'):
                df = self._get_table_content(self.table_folder+'/'+img, key)
                tables.append(df)
                names.append(img)
        return tables, names

    #This function recovers the coordinates of text recognized and returns a list of ordered text
    #height: the text with y-coordinate smaller than height are considered in the same line
    def _get_row(self,box_co, text_list, height=10):
        m = box_co[0][1]
        num_row = 0
        ptr = 0
        n = len(box_co)
        left = [t[0] for t in box_co]
        row_list = []
        while ptr < n:
            prev = ptr    
            while ptr < n and box_co[ptr][1] < (m+height):
              ptr += 1
            ind = np.asarray(left[prev:ptr]).argsort() + prev
            row = [text_list[i][1] for i in ind]
            row_list.append(row)
            if ptr < n:
                m = box_co[ptr][1]
        return row_list

    #This function returns a list of candidate captions in the text_list
    def _caption(self, text_list):
        clist=[]
        caption = ''
        n = len(text_list)
        i = 0
        while i < n:
            if text_list[i].startswith('Table') and '.' in text_list[i]:
                ind = text_list[i].index('.')
                clist.append(text_list[i][0:ind+1])
            elif text_list[i].startswith('Table'):
                caption = text_list[i]
            elif '.' in text_list[i]:
                ind = text_list[i].index('.')
                caption += text_list[i][0:ind+1]
                if caption.startswith('Table'):
                    clist.append(caption)
                caption = ''
            else:
                caption += text_list[i]
            i += 1 #happens in all if/elif/else blocks so can be moved outside can also be a for loop

        if caption.startswith('Table'):
            clist.append(caption)
        return clist
