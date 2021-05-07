#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import pandas as pd
import os
import math
from xlrd import XLRDError


##########################################  vv USER CHANGE vv  ##########################################


### import all csv files to the Data bin then run

interested_retention = [8, 15,19,20,22, 30] ### change this to the retention times you are interestsed in
excel_page_num = 47 ## Change this number to the numer of pages there are in a single Excel sheet.
                    ## If there are multiple sheets with varying page numbers, enter the max excel sheet 
                    ## or a number that you think is high enough to capture all data
                    ## You will receive a print message that tells you where the page number
                    ## does not exist for a given excel sheet 
min_peak_area = 10

######################################## vv USER DONT CHANGE vv  #########################################
def hplc(Athena = True):
    
    data_path = os.getcwd() + '\\Data'
    all_data_dict = {}
    all_data_list = []
    counter = 0
    
    for j in os.listdir(data_path):
        if (j == '.DS_Store') or ('~$' in j):
            continue
        sheet_path = data_path + '\\' + str(j)
        
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
                    series['id'] = identifcation
                    series['excel sheet'] = j
                    series['page number'] = k
                    all_data_list.append(series)
            except XLRDError:
                print('Page {} does not exist in Excel spreadsheet {}'.format(k, j))
                break
                
        
        ## Old method
        #identification = j.split('/')[-1].split('.')[0]
        # index = []
        # for i in range(len(series)):
        #     if any(round(series['Peak\nRetention\nTime'][i],0) == interested_retention): 
        #         index.append(i)
        # new_series = series.loc[index,:]
        # new_series['id'] = identification
        # all_data_dict[str(identification)] = new_series
        # all_data_list.append(new_series)
    
    all_data_list = pd.concat(all_data_list)
    
    file_name = 'data_0.csv'
    csv_path = os.getcwd() + file_name
    if os.path.isfile(file_name):
        expand = 0
        while True:
            expand += 1
            new_file_name = file_name.split("_")[0] + '_' + str(expand) + '.csv'
            if os.path.isfile(new_file_name):
                continue
            else:
                file_name = new_file_name
                break
    all_data_list.to_csv(file_name, index=False)
    return all_data_list
a = hplc()
