import cv2
from google.colab.patches import cv2_imshow
import numpy as np
import pandas as pd


# This is a private class that is only used by the PDFPaper class
class _Page:
    def __init__(self, page_path, page_number):
        #The initializer calls all of the private methods in order to fully create the class
        self.page_path = page_path
        self.page_number = page_number
        self.image = cv2.imread(page_path)
        self.merge, self.bitwiseAnd, self.dilatedcol = self._line_get()
        self.merge_df, self.mylisty, self.tabledf = self._table_df_get()
        self.line_df = self._find_linedf()
        self.box_list = self._find_table()

    #Public Methods:
    #This is the only public method used by the PDFPaper class
    def table_recog2img_one_page(self, to_folder, table_cnt):
        #verify that we have a table before calling a method which would fail without one
        if (self.tabledf is None) or (len(self.tabledf) == 0):
          return table_cnt
        table_cnt = self._table_get_crop(to_folder, table_cnt)
        print('#tables in page '+ str(self.page_number))
        return table_cnt

    #Private Methods:

    # This function crops 1. each table based on the coordinates of box vertices which are stored in the self.box_list
    #                     2. each table with additional room above and below to include the caption part
    # cnt: the index of the table in the whole pdf paper
    # thr1: error within which the boxes are not considered as tables
    # thr2: distance to keep for left and right to the table
    # thr3: distance to keep for above and below the table
    def _table_get_crop(self, to_folder, cnt, thr=50, thr2=100, thr3=160):
        for box in self.box_list:
          xmin, xmax, ymin, ymax = box
          table = self.image.copy()
          table_cropImg = table[ymin-thr:ymax+thr, xmin-thr:xmax+thr]
          if (ymax - ymin <= thr) or (xmax - xmin) <= thr:
            continue              
          print('table ', cnt)
          cv2.imwrite(to_folder + '/page_'+str(self.page_number)+'_table'+str(cnt)+'.jpg', table_cropImg)
          total_cropImg = table[ymin-thr3:ymax+thr3, xmin-thr2:xmax+thr2]
          cv2.imwrite(to_folder + '/total_page_'+str(self.page_number)+'_table'+str(cnt)+'.jpg', total_cropImg) 
          cnt += 1
        return cnt

    #This function returns a list of points which are the ending points of the lines in pt_list 
    #pt_list: a list of coordinates of points, where points with continuous coordinates consist of lines
    #thr: two points with distance larger than thr are considered discontinuous
    def _get_discrete_pts(self, pt_list, thr=5):
        if len(pt_list) == 0:
            return [] 
        res = []
        for i in range(len(pt_list)-1):
            if (pt_list[i+1] - pt_list[i] > thr):
                res.append(pt_list[i])
        res.append(pt_list[-1])  
        return res

    #This function returns the merge, bitwiseAnd, and dilatedcol values of the image
    #merge: the coordinates of points which consist of both horizontal and vertical lines
    #bitwiseAnd: the coordinates of points which are the crossing of horizontal and vertical lines
    #dilatedcol: the coordinates of points which consist of horizontal lines
    def _line_get(self, scale=40):
        image = self.image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
        rows, cols = binary.shape
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols//scale,1))
        eroded = cv2.erode(binary, kernel, iterations = 1)
        dilatedcol = cv2.dilate(eroded,kernel,iterations = 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,rows//scale))
        eroded = cv2.erode(binary,kernel,iterations = 1)
        dilatedrow = cv2.dilate(eroded,kernel,iterations = 1)
        bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)
        merge = cv2.add(dilatedcol,dilatedrow)
        return merge, bitwiseAnd, dilatedcol


    #This function returns the coordinates of 
    #1. both horizontal and vertical lines as merge_df (dataframe)
    #2. horizontal lines as tabledf (dataframe)
    #3. the y-axis of each horizontal line as mylisty (list)
    def _table_df_get(self):
        merge = self.merge
        dilatedcol = self.dilatedcol
        bitwiseAnd = self.bitwiseAnd
        tableco = np.where(merge>0)
        merge_df = pd.DataFrame({'y':tableco[0], 'x':tableco[1]})
        ys, xs = np.where(dilatedcol>0)
        tabledf = pd.DataFrame({'y':ys, 'x':xs})
        myys = np.sort(np.unique(ys))
        mylisty = self._get_discrete_pts(myys)
        return merge_df, mylisty, tabledf

    #This function returns a dataframe showing starting, ending and y-axis of horizontal lines
    def _find_linedf(self, thr=100, thr2=10, thr3=5):
        tabledf = self.tabledf
        mylisty = self.mylisty
        if len(tabledf) == 0:
            return None
        x_global_min = min(tabledf['x'])
        xmin = x_global_min
        xmax = 0
        yprev = mylisty[0]
        ymin = mylisty[0]
        listx = []
        for y in mylisty:
            line = tabledf[tabledf['y'] < (y+thr2)]
            line = line[line['y'] > (y-thr2)]
            xmin = min(line['x'])
            xs = sorted(list(set(line['x'])))
            #get_discrete_pts(xs)
            for i in range(len(xs)-1):
                if (xs[i+1] - xs[i] > thr3):
                    listx.append([xmin, xs[i], y])
                    xmin = xs[i+1]
            listx.append([xmin, xs[-1], y])
        line_df = pd.DataFrame(listx, columns=['x_min', 'x_max', 'y'])
        return line_df

    #This function returns a list of boxes which contains the coordinates of four vertices
    #thr: for lines with difference of y-axis larger than thr are considered not stacked
    def _find_table(self, thr=5): 
        line_df = self.line_df
        box_list = []
        if (line_df) is None:
          return box_list
        x_list = sorted(list(set(line_df['x_min'])))
        resmin = self._get_discrete_pts(x_list)
        for xmin in resmin:
            table_df = line_df[line_df['x_min'] > xmin - thr]
            table_df = table_df[table_df['x_min'] <= xmin]
            resmax = []
            x_list = sorted(list(table_df['x_max']))
            resmax = self._get_discrete_pts(x_list)
            for xmax in resmax:
                table_df2 = table_df[table_df['x_max'] > xmax-thr]
                table_df2 = table_df2[table_df2['x_max'] <= xmax]
                ymin, ymax = min(table_df2['y']), max(table_df2['y'])
                if ymax > ymin + thr:
                   box_list.append((xmin, xmax, ymin, ymax))
        return box_list
