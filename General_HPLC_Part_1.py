#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import pandas as pd
import os
from xlrd import XLRDError
import ast

def hplc_clean(excel_page_num = 999, unit = None, reference_chem = None):
    if (unit == None) | (unit == ''):
        unit = input('Please input either thermo or agilent: ')
    all_data_list = []
    data_path = os.path.join(os.getcwd(), 'input', str(unit).lower())
    for j in os.listdir(data_path):
        if (j == '.DS_Store') or ('~$' in j):
            continue
        sheet_path = os.path.join(data_path, str(j))
        if unit == 'agilent':
            for k in range(1, excel_page_num+1):
                sheetname = 'Page ' + str(k)
                try:
                    series = pd.read_excel(sheet_path, sheet_name = sheetname, header = None, index_col = None)
                    # Identification Page [Generally odd]
                    if type(series.at[2,0]) is str:
                        identifcation = series.at[2,4]
                        if 'blank' in identifcation.lower():
                            identifcation = identifcation + ' ' + str(j) + ' ' + str(k)
                        continue
                    else: #Dealing with different Agilents [Beyonce]
                        try:
                            if type(series.at[6,1]) is str:
                                identifcation = series.at[6,5]
                                if 'blank' in identifcation.lower():
                                    identifcation = identifcation + ' ' + str(j) + ' ' + str(k)
                                continue
                            elif 'signal' not in str(series.at[0,0]).lower():
                                series = series.iloc[1:] # Remove the first row
                                series = series.reset_index(drop=True) #Reset index numbers
                        except KeyError:
                            if 'signal' not in str(series.at[0,0]).lower():
                                series = series.iloc[1:] # Remove the first row
                                series = series.reset_index(drop=True) #Reset index numbers

                    start_index = series[0].first_valid_index() + 1 # Finds the first non-null in column 0, Generally this is where "Signal" is
                    series = series.iloc[start_index:] #Remove all data above ""Peak Retention Time"
                    headers = series.iloc[0]
                    series = pd.DataFrame(series.values[1:], columns = headers) # Renames column names to Peak retention time, etc.
                    series = series.loc[:, series.columns.notnull()]  # Removes all dead space from Excel merged columns
                    series = series.dropna(thresh = 2) # Removes all rows that have more than 2 NaN
                    series = series[series['Peak\nRetention\nTime'].notna()]

                    try:
                        reference_series = series[series['Compound'].str.endswith('Cipro', na=False)]
                        reference_value = reference_series.iloc[0]['Peak\nRetention\nTime']
                        data['RRT (ISTD)'] = [float(x) / float(reference_value) for x in data['Peak\nRetention\nTime']]
                    except:
                        reference_value = input('Please input the RT (float) of reference sample to update the RRT or type no: ')
                        if reference_value == 'no':
                            reference_value = 1
                        data['RRT (ISTD)'] = [float(x) / float(reference_value) for x in data['Peak\nRetention\nTime']]

                    series['id'] = identifcation
                    series['excel sheet'] = j
                    series['page number'] = k
                    all_data_list.append(series)

                except XLRDError:
                    print('Page {} does not exist in Excel spreadsheet {}'.format(k, j))
                    break
        else: #This is for Thermo units
            identification = pd.read_excel(sheet_path, sheet_name = 'Integration', header = None, index_col = None).at[4,2]
            data = pd.read_excel(sheet_path, sheet_name = 'Integration', header = 0, index_col = None, skiprows = 46).drop([0,1])
            data = data[~data['No. '].isin(['n.a.', 'Total:'])]
            data['id'] = identification
            data['excel_sheet'] = pd.read_excel(sheet_path, sheet_name = 'Overview', header = None, index_col = None).at[3,2]
            if (reference_chem == None) | (reference_chem == ''):
                reference_chem = input('Please input the reference chemical of interest (case-sensitive) or '
                                       'type (float) a reference RT of interest: ')
            try:
                if len(data[data['Peak Name'].str.endswith(reference_chem, na=False)]) > 0:
                    reference_series = data[data['Peak Name'].str.endswith(reference_chem, na=False)]
                    reference_value = reference_series.iloc[0]['RT']
                else:
                    reference_value = reference_chem
                data['RRT'] = [float(x) / float(reference_value) for x in data['RT']]
            except:
                data['RRT'] = data['RT']
            try:
                data = data.rename(columns={'Peak Name': 'Compound', 'RT': 'Peak\nRetention\nTime', 'RRT': 'RRT (ISTD)',
                                    'LCAP ': 'Peak\nArea\nPercent', 'Amount ':'Compound Amount', 'Area ': 'Area', 'Height ': 'Height' })
                data = data[['Peak\nRetention\nTime', 'RRT (ISTD)', 'Peak\nArea\nPercent', 'Area', 'Height', 'Compound',
                             'Compound Amount', 'id', 'excel_sheet']]
            except KeyError: #Midaz does not have 'compound amount; and instead has 'S/N'
                data = data.rename(columns={'Peak Name': 'Compound', 'RT': 'Peak\nRetention\nTime', 'RRT': 'RRT (ISTD)',
                                            'LCAP ': 'Peak\nArea\nPercent', 'Area ': 'Area', 'Height ': 'Height'})
                data = data[['Peak\nRetention\nTime', 'RRT (ISTD)', 'Peak\nArea\nPercent', 'Area', 'Height', 'Compound',
                             'id', 'excel_sheet']]
            all_data_list.append(data)
    if len(all_data_list) >= 1:         
        all_data_list = pd.concat(all_data_list)
    else:
        print('The directory, {}, is currently empty. Please make sure that files were properly added to the correct directory folder.'.format(unit))
    return all_data_list
    
def save_data(data, unit = None):
    if type(data) == list:
        return None
    else:
        if (unit == None) | (unit == ''):
            unit = input('Please input either thermo or agilent: ')
        file_name = str(unit) + '-clean-data_0.csv'
        csv_path = os.path.join(os.path.abspath("output"), 'clean', file_name)
        if os.path.isfile(csv_path):
            expand = 0
            while True:
                expand += 1
                new_file_name = file_name.split("_")[0] + '_' + str(expand) + '.csv'
                csv_path = os.path.join(os.path.abspath("output"), 'clean',new_file_name)
                if os.path.isfile(csv_path):
                    continue
                else:
                    file_name = csv_path
                    break
        data.to_csv(csv_path, index=False)
    print('File was saved at {}'.format(csv_path))

from timeit import default_timer as timer

if __name__ == '__main__':
      unit_ = input('Please enter either thermo or agilent: ')
      start = timer()
      dataframe = hplc_clean(unit = unit_)
      save_data(dataframe, unit = unit_)
      print('Total time to run code was {} sec'.format(timer() -start))
      


