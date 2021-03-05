#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import pandas as pd
import os
import math

## 
### import all csv files to the Data bin then run

data_path = os.getcwd() + '/Data'
all_data_dict = {}
all_data_list = []
counter = 0

## Users change these 
interested_retention = [15,19,20,22] ### change this to the retention times you are interestsed in
excel_page_num = 46 ## Change the number of pages there are on a single excel file. If there are varying pages, run in batches
                    ## by adding excel spreadsheets in the Data directory

for j in os.listdir(data_path):
    if (j == '.DS_Store') or ('~$' in j):
        continue
    sheet_path = data_path + '/' + str(j)
    
    # Header = None creates integer column names and grabs the whole sheet
    #series = pd.read_excel(sheet_path, sheet_name = 'Page 2', header = None, index = False, index_col = None)
    
    for k in range(1, excel_page_num+1):
        sheetname = 'Page ' + str(k)
        series = pd.read_excel(sheet_path, sheet_name = sheetname, header = None, index_col = None)
        #odd pages
        if (k % 2) != 0:
            identifcation = series.at[2,4]
        # even pages
        if (k % 2) == 0:
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
            index = []
            for i in range(len(series)):
                value = series['Peak\nRetention\nTime'][i]
                if math.isnan(value):
                    continue
                if round(series['Peak\nRetention\nTime'][i],0) in interested_retention: 
                    index.append(i)
            new_series = series.loc[index,:]
            new_series['id'] = identifcation
            all_data_dict[str(identifcation)] = new_series
            all_data_list.append(new_series)
    
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