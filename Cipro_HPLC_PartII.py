#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 11:10:53 2021

@author: samueljon
"""
import os
import pandas as pd

def Import(folder = None, windows = True):
    '''

    Parameters
    ----------
    folder : path
        DESCRIPTION. The default is None.
    windows : boolean, optional
        DESCRIPTION. The default is False. Apply True if running the program on Windows OS

    Returns
    -------
    TYPE
        DESCRIPTION. If the path exist in the CIPRO_HPLC/output directory, returns a pandas dataframe

    '''
    
    if windows:
        slash = '\\'
    else:
        slash = '/'
    if folder == None:
        folder = input('Please specifiy which data you would like imported. Make sure to include the file extension (i.e, .csv): ')
        if folder == '':
            return print('Please enter a file name')
    path = os.path.abspath('output'+ slash + 'clean' + slash + folder)
    try:
        series = pd.read_csv(path, header = 0)
        return series
    except:
        return print('Please ensure that the file is correct and has a .csv extension')

def rrt_range(rrt, range_ = 0.02):
    '''
    Overview : outputs the relative retention time range for a given retentino time. Useful within the IFM algorithm when checkcing through
    all data and classifying data as the same value or not based on the range of retention time(s). For example, if sample A has an rrt = 0.9, 
    based on a range_ = 0.02, sample B with rrt=0.92 would be classified as 0.9 because it falls in the range of [0.9-0.02, 0.9+0.02]
    
    Parameters
    ----------
    rrt : float
        DESCRIPTION. relative retention time
    range_ : float
        DESCRIPTION. The default is 0.02. This value will be the addition/subtraction for the upper and lower bound of the relative retention
        time range. 

    Returns
    -------
    list
        DESCRIPTION. lower and upper bound range rounded to 2 decimal places for the relative retention time

    '''
    rrt = float(rrt)
    return [round(rrt-range_,2),round(rrt+range_,2)]


def ifm(data = 'sample_combined_data_0.csv', r = 0.02):
    '''

    Parameters
    ----------
    data : csv name within the the CIPRO_HPLC/output directory. Used as a variable for function Import
        DESCRIPTION. The default is 'sample_combined_data_0.csv'.
    r : used as range_ input for rrt_range
        DESCRIPTION. The default is 0.02

    Returns
    -------
    df : pandas dataframe
        DESCRIPTION. Summary dataframe with columns as unique relative retention times after applying rrt_range, rows as samples and the data as
        LCAP%. 

    '''
    
    series = Import(folder = data)
    lst = series['RRT (ISTD)'].round(2).tolist() #represents list of relative retention times, make sure to round prior
    ranges = [rrt_range(lst[0], range_=r)] #represents ranges of unique list
    range_dict = {str(rrt_range(lst[0], range_=r)):lst[0]}
    new_lst = [] #represents unique list of relative retention times based on ranges, initialize with the first number
    for i, num in enumerate(lst):
        if any(r[0] <= num <= r[1] for r in ranges): #if num is within any of the ranges, add the number that corresponds to that range to new_list
            #boolean =  [r[0] <= num <= r[1] for r in ranges] #return the index where num is in ranges
            index = [i for i, x in enumerate([r[0] <= num <= r[1] for r in ranges]) if x]
            new_lst.append(range_dict[str(ranges[index[0]])])
        else:
            ranges.append(rrt_range(num))
            range_dict.update({str(rrt_range(num)):num})
            new_lst.append(num)
    series['RRT (ISTD)_new'] = new_lst
    new_set = set(new_lst) #unique values of list + sort
    final_dict = {}
    subset = series.groupby(['id']).apply(lambda x: x[['RRT (ISTD)_new', 'Peak Area\nPercent']].values).to_dict()
    for key, value in subset.items():
            test_list = [i if i in subset[key][:,0].tolist() else 0 for i in list(new_set)]
            for i in test_list:
                for idx2, j in enumerate(subset[key][:,0].tolist()):
                    if subset[key][:,0][idx2] in test_list:
                        test_list[test_list.index(j)]=subset[key][:,1].tolist()[idx2]
            final_dict.update({key: test_list})
    df = pd.DataFrame.from_dict(final_dict, orient='index', columns = new_set)
    df = df.reindex(sorted(df.columns), axis = 1)
    return df

def save_data(data, unit = None, windows = True):
    '''
    Parameters
    ----------
    data : pandas dataframe
        DESCRIPTION. dataframe after undergoing ifm()
    unit : str
        DESCRIPTION. The default is None. unit process such as 'r3, r5, cau, pau'. Used to name the save file correctly
    windows : boolean, optional
        DESCRIPTION. The default is False. Apply True if running the program on Windows OS

    Returns
    -------
    None. Saves data under CIPRO_HPLC/output/ with extention 'unit'-summary-data_#.csv where # starts at 0 and += 1 if there exist a file w/ that extenssion.

    '''
    
    
    if type(data) == list:
        return None
    else:
        if windows:
            slash = '\\'
        else:
            slash = '/'
        if (unit == None) | (unit == ''):
            unit = input('Please input the process (i.e. r3, r5, cau, pau, other): ')
        file_name = str(unit) + '-summary-data_0.csv'
        csv_path = os.path.abspath("output" + slash + 'summary' +slash + file_name)
        if os.path.isfile(csv_path):
            expand = 0
            while True:
                expand += 1
                new_file_name = file_name.split("_")[0] + '_' + str(expand) + '.csv'
                csv_path = os.path.abspath("output" + slash + 'summary' + slash + new_file_name)
                if os.path.isfile(csv_path):
                    continue
                else:
                    file_name = csv_path
                    break
        data.to_csv(csv_path, index=True)
    print('File was saved at {}'.format(csv_path))

from timeit import default_timer as timer
if __name__ == '__main__':
    w = input('Are you using a windows? (y/n) ')
    if w == 'n':
        w = False
    else:
        w = True
    clean_data = input('Please input clean .csv file name: ')
    cip_step = input('Please input the process (i.e. r3, r5, cau, pau): ')
    start = timer()
    save_data(data = df, unit = unit_)   
    print('Total time to run code was {} sec'.format(timer() -start))
    save_data(data = df, unit = cip_step)   
    df = ifm(data = clean_data, r = 0.02)