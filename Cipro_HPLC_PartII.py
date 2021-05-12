#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 11:10:53 2021

@author: samueljon
"""
import os
import pandas as pd

def Import(folder = None, windows = False):
    if windows:
        slash = '\\'
    else:
        slash = '/'
    if folder == None:
        folder = input('Please specifiy which data you would like imported. Make sure to include the file extension (i.e, .csv): ')
        if folder == '':
            return print('Please enter a file name')
    path = os.path.abspath('output'+ slash + folder)
    try:
        #path.split('.')[1] == 'csv'
        series = pd.read_csv(path, header = 0)
        return series
    except:
        return print('Please ensure that the file is correct and has a .csv extension')

def rrt_range(rrt, range_ = 0.02):
    rrt = float(rrt)
    return [round(rrt-range_,2),round(rrt+range_,2)]

def ifm(data = 'sample_combined_data_0.csv'):
    series = Import(folder = data)
    lst = series['RRT (ISTD)'].round(2).tolist() #represents list of relative retention times, make sure to round prior
    ranges = [rrt_range(lst[0])] #represents ranges of unique list
    range_dict = {str(rrt_range(lst[0])):lst[0]}
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
    df = df.reindex(sorted(df.columns), axis=1)
    return df

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
        file_name = str(unit) + '-summary-data_0.csv'
        csv_path = os.path.abspath("output") + slash + file_name
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
        data.to_csv(csv_path, index=True)

if __name__ == '__main__':
    df = ifm(data = 'sample_combined_data_0.csv')
    #save_data(data = df, unit = 'r3')   
   