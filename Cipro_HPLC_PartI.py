#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import pandas as pd
import os
from xlrd import XLRDError
 
    
def hplc(windows = False, excel_page_num = 999, unit = None, cipro_rt = None):
    '''
    Parameters
    ----------
    windows : boolean, optional
        DESCRIPTION. The default is False. Fixes file path based on operating system
    excel_page_num : int, optional
        DESCRIPTION. The default is 999. Set the max sheet number within a given excel spreadsheet. If number selected is higher than actual
        XLDRError will present itself and break the code.
    Returns
    -------
    all_data_list : pandas data frame
        DESCRIPTION. Combined data frame that has all spreadsheets and excels from the directory path

    '''
    if (unit == None) | (unit == ''):
        unit = input('Please input the process (i.e. r3, r5, cau, pau): ')
    all_data_list = []
    if windows:
        data_path = os.getcwd() + '\\Data\\' + str(unit).lower()
    else:
        data_path = os.getcwd() + '/Data/' + str(unit).lower()

    for j in os.listdir(data_path):
        if (j == '.DS_Store') or ('~$' in j):
            continue
       
        if windows:
            sheet_path = data_path + '\\' + str(j)
        else:
            sheet_path = data_path + '/' + str(j)
            
        # Header = None creates integer column names and grabs the whole sheet
        #series = pd.read_excel(sheet_path, sheet_name = 'Page 2', header = None, index = False, index_col = None)
        
        for k in range(1, excel_page_num+1):
            sheetname = 'Page ' + str(k)
            try:
                series = pd.read_excel(sheet_path, sheet_name = sheetname, header = None, index_col = None)
                
                # Identification Page [Generally odd]
                if type(series.at[2,4]) is str:
                    identifcation = series.at[2,4]
                    continue
                elif type(series.at[6,1]) is str:
                    identifcation = series.at[6,5]
                    continue
                # Data Page(s) [Generally even but if more than one page of data exist, off shifts odd/even cycle]
                else:
                    # Remove the first row 
                    series = series.iloc[1:]
                    
                    #Reset index numbers
                    series = series.reset_index(drop=True)
                    
                    # Finds the first non-null in column 0, Generally this is where "Signal" is
                    start_index = series[0].first_valid_index() + 1
                    
                    #Remove all data above ""Peak Retention Time"
                    series = series.iloc[start_index:]
                    
                    # Renames column names to Peak retention time, etc.
                    headers = series.iloc[0]
                    series = pd.DataFrame(series.values[1:], columns = headers)
                    
                    # Removes all dead space from Excel merged columns
                    series = series.loc[:, series.columns.notnull()]
                    ## Old method
                    #series = series.loc[:,~series.columns.str.match('Unnamed')]
                   
                    # Removes all rows that have more than 2 NaN
                    series = series.dropna(thresh = 2)
                    series = series[series['Peak\nRetention\nTime'].notna()]
                    if unit == 'r3':
                        if cipro_rt == None:
                            cipro_rt = float(input('Please input the RT of cipro to update the RRT: '))
                            if cipro_rt == '':
                                cipro_rt = 1
                        series['RRT (ISTD) new'] = [float(x)/cipro_rt for x in series['Peak\nRetention\nTime']]
                    series['id'] = identifcation
                    series['excel sheet'] = j
                    series['page number'] = k
                    all_data_list.append(series)
            
            except XLRDError:
                print('Page {} does not exist in Excel spreadsheet {}'.format(k, j))
                break
    if len(all_data_list) >= 1:         
        all_data_list = pd.concat(all_data_list)
    else:
        print('The directory, {}, is currently empty. Please make sure that files were properly added to the correct directory folder.'.format(unit))
    return all_data_list
    
def save_data(data, unit = None, windows = False):
    if type(data) == list:
        return None
    else:
        if windows:
            slash = '\\'
        else:
            slash = '/'
        if (unit == None) | (unit == ''):
            unit = input('Please input the process (i.e. r3, r5, cau, pau): ')
        file_name = str(unit) + '-clean-data_0.csv'
        csv_path = os.path.abspath("output") + slash + 'clean' + slash + file_name
        if os.path.isfile(csv_path):
            expand = 0
            while True:
                expand += 1
                new_file_name = file_name.split("_")[0] + '_' + str(expand) + '.csv'
                csv_path = os.path.abspath("output") + slash + new_file_name
                if os.path.isfile(csv_path):
                    continue
                else:
                    file_name = csv_path
                    break
        data.to_csv(csv_path, index=False)

from timeit import default_timer as timer
if __name__ == '__main__':
      start = timer()
      w = True
      unit_ = input('Please input the process (i.e. r3, r5, cau, pau): ')
      test = hplc(windows = w, unit = unit_)
      save_data(test, unit = unit_, windows = w)
      print(timer() -start)
      


