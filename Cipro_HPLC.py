#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import pandas as pd
import os

## 
### import all csv files to the Data bin then run

data_path = os.getcwd() + '/Data'
all_data_dict = {}
all_data_list = []
interested_retention = [15,19,20,22] ### change this to the retention times you are interestsed in
counter = 0
for j in os.listdir(data_path):
    if (j == '.DS_Store') or ('~$' in j):
        continue
    sheet_path = data_path + '/' + str(j)
    series = pd.read_excel(sheet_path, sheet_name = 'Page 2', header = 6, index = False, index_col = None)
    series = series.loc[:,~series.columns.str.match('Unnamed')]
    series = series.dropna(thresh = 2)
    identification = j.split('/')[-1].split('.')[0]
    index = []
    for i in range(len(series)):
        if any(round(series['Peak\nRetention\nTime'][i],0) == interested_retention): 
            index.append(i)
    new_series = series.loc[index,:]
    new_series['id'] = identification
    all_data_dict[str(identification)] = new_series
    all_data_list.append(new_series)
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