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
    path = os.path.abspath('output'+ slash + 'cipro' + slash + 'clean' + slash + folder)
    try:
        series = pd.read_csv(path, header = 0)
        return series
    except:
        return print('Please ensure that the file is correct and has a .csv extension')

def rrt_range(rrt, range_ = None, rounding_num = None):
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
    return [round(rrt-range_,rounding_num),round(rrt+range_,rounding_num)]
def average(lst):
    return sum(lst) / len(lst)

def ifm(data = 'sample_combined_data_0', r = None, windows_ = False, round_num = None):
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
    data = data + '.csv'
    series = Import(folder = data, windows = windows_)
    lst = series['RRT (ISTD)'].tolist() #represents list of relative retention times, make sure to round prior
    ranges = [rrt_range(lst[0], range_=r, rounding_num=round_num)] #represents ranges of unique list
    range_dict = {str(rrt_range(lst[0], range_=r,rounding_num=round_num )):lst[0]}
    new_lst = [] #represents unique list of relative retention times based on ranges, initialize with the first number
    for i, num in enumerate(lst):
        if any(r[0] <= num <= r[1] for r in ranges): #if num is within any of the ranges, add the number that corresponds to that range to new_list
            #boolean =  [r[0] <= num <= r[1] for r in ranges] #return the index where num is in ranges
            index = [i for i, x in enumerate([r[0] <= num <= r[1] for r in ranges]) if x]
            if len(index) == 2:
                if abs(num - average(ranges[index[0]])) > (abs(num - average(ranges[index[1]]))):
                    index = [index[1]]
                else:
                    index = [index[0]]
            new_lst.append(range_dict[str(ranges[index[0]])])
        else:
            ranges.append(rrt_range(num,range_=r,rounding_num=round_num))
            range_dict.update({str(rrt_range(num, range_=r,rounding_num=round_num)):num})
            new_lst.append(num)
    series['RRT (ISTD)_new'] = new_lst
    new_set = set(new_lst) #unique values of list + sort
    final_dict = {}
    subset = series.groupby(['sample id']).apply(lambda x: x[['RRT (ISTD)_new', 'Peak Area\nPercent']].values).to_dict()
    for key, value in subset.items():
            test_list = [i if i in subset[key][:,0].tolist() else 0 for i in list(new_set)]
            for idx2, j in enumerate(subset[key][:,0].tolist()):
                if subset[key][:,0][idx2] in test_list:
                    test_list[test_list.index(j)]=subset[key][:,1].tolist()[idx2]
            final_dict.update({key: test_list})
    final_rrt_lst = [round(x,round_num) for x in new_set]
    df = pd.DataFrame.from_dict(final_dict, orient='index', columns = final_rrt_lst)
    #df = pd.DataFrame.from_dict(final_dict, orient='index', columns = new_set)
    try:
        df = df.reindex(sorted(df.columns), axis = 1)
        df['Total LCAP'] = df.sum(axis = 1)
        
        ''' Checking if the total LCAP of each sample is the same as the raw data.
            If they are all the same, the output is reliable.
            If any of them do not match, it most likely due to the grouping error, where two peaks from
            the same sample are too close to each other and were mistakenly group as one peak.
            In that case, user can use a smaller range, bigger rounding number, or both.
        '''
        check = []
        for k in subset.keys():
            subset[k] = pd.DataFrame(subset[k])
            subset[k] = subset[k].append(subset[k].sum(numeric_only=True), ignore_index=True) # Adds a sum row to each sample
            if round(df.loc[k,'Total LCAP'], 2) != round(subset[k].loc[len(subset[k])-1,1], 2):
                check.append(k)
        if len(check) >= 1:
            # CGREEN = '\033[1;32;40m'
            # CEND = '\033[1;30;46m'
            print(('\033[31m'+ 'Total LCAP of samples {} do NOT match with raw data. Please try smaller range, bigger rounding, or both' + '\033[30m').format(check))
        return df
    except ValueError:
        print('Error at rounding {} and range {}'.format(round_num,r))
        return final_rrt_lst

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
        file_name = str(unit) + '-LCAP-summary-data_0.csv'
        csv_path = os.path.abspath("output" + slash + 'cipro' + slash + 'summary' +slash + file_name)
        if os.path.isfile(csv_path):
            expand = 0
            while True:
                expand += 1
                new_file_name = file_name.split("_")[0] + '_' + str(expand) + '.csv'
                csv_path = os.path.abspath("output" + slash + 'cipro' + slash + 'summary' + slash + new_file_name)
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
    clean_data = input('Please input clean file name: ')
    cip_step = input('Please input the process (i.e. r3, r5, cau, pau), NO lowerdash: ')
    start = timer()
    df = ifm(data = clean_data, r = 0.01, round_num = 3, windows_ = w)
    save_data(data = df, unit = cip_step, windows =w)     
    print('Total time to run code was {} sec'.format(timer() -start))  
    
        
        