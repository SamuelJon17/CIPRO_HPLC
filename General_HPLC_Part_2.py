#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 11:10:53 2021

@author: samueljon
"""
import os
import pandas as pd
import ast
import math

def Import(file_name = None):
    path = os.path.join(os.getcwd(), 'output', 'clean', file_name)
    try:
        series = pd.read_csv(path, header = 0)
        return series
    except:
        return print('Please ensure there is only one clean file in IFM')

def rrt_range(rrt, range_ = None, rounding_num = None):
    rrt = float(rrt)
    return [round(rrt-range_,rounding_num),round(rrt+range_,rounding_num)]

def average(lst):
    return sum(lst) / len(lst)

def ifm(data = None, r = None, round_num = None):
    if (data == None) | (data == ''):
        data_name = input('Please input clean file name: ')
    data = data_name + '.csv'
    series = Import(file_name = data)
    lst = series['RRT (ISTD)'].tolist() #represents list of relative retention times, make sure to round prior
    ranges = [rrt_range(lst[0], range_=r, rounding_num=round_num)] #represents ranges of unique list
    range_dict = {str(rrt_range(lst[0], range_=r,rounding_num=round_num )):lst[0]}
    new_lst = [] #represents unique list of relative retention times based on ranges, initialize with the first number
    for i, num in enumerate(lst):
        num = float(num)
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
    subset = series.groupby(['id']).apply(lambda x: x[['RRT (ISTD)_new', 'Peak\nArea\nPercent', 'Compound']].values).to_dict()
    for key, value in subset.items():
            test_list = [i if i in subset[key][:,0].tolist() else 0 for i in list(new_set)]
            for idx2, j in enumerate(subset[key][:,0].tolist()):
                if subset[key][:,0][idx2] in test_list:
                    test_list[test_list.index(j)]=round(float(subset[key][:, 1].tolist()[idx2]),2)
            final_dict.update({key: test_list})
    final_rrt_lst = [round(x,round_num) for x in new_set]
    #Temporary, grabbing names for columns
    rrt_to_names = [list(set(series.loc[series['RRT (ISTD)'] == i]['Compound'].tolist())) for i in new_set]
    rrt_to_names = [item for items in rrt_to_names for item in items]
    #rrt_to_names = pd.Series([item for items in rrt_to_names for item in items])
    #rrt_to_names.fillna(pd.Series(final_rrt_lst), inplace = True) #This is if you want columns name to be changed
    #rrt_to_names = rrt_to_names.tolist()
    
    df = pd.DataFrame.from_dict(final_dict, orient='index', columns = final_rrt_lst)
    df = df.append(pd.DataFrame([rrt_to_names], columns=df.columns, index = ['Compound_name']))

    try:
        #W/ names + RRT, sorting cannot happen
        df = df.reindex(sorted(df.columns), axis = 1)
        df_values = df.iloc[0:df.shape[0]-1]
        df['Total LCAP'] = df_values.sum(axis = 1)
        
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
        return df, data_name
    except ValueError:
        print('Error at rounding {} and range {}'.format(round_num,r))
        return final_rrt_lst

## Needs work done.

# import numpy as np
# def find_best_lcap(data):
#     r = list(set(np.linspace(.1,1,10).tolist() + np.linspace(.01,.1, 10).tolist()))
#     rnd_num = [1,2,3,4,5]
#     combo = [[x,y] for x in r for y in rnd_num]
#     dataframe = [sum(100.5 > i > 99.5 for i in ifm(data, r = x[0], round_num = x[1])[0]['Total LCAP']) for x in combo]
#     max = max(dataframe)
#     print(combo[dataframe.index(max)])

def save_data(data, name):
    if type(data) == list:
        return None
    else:
        file_name = name + '_IFM' + '.csv'
        csv_path = os.path.join(os.getcwd(), 'output', 'ifm', file_name)
        if os.path.isfile(csv_path):
            expand = 0
            while True:
                expand += 1
                new_file_name = name + '_IFM' + '_' + str(expand) + '.csv'
                csv_path = os.path.join(os.getcwd(), 'output', 'ifm', new_file_name)
                if os.path.isfile(csv_path):
                    continue
                else:
                    file_name = csv_path
                    break
        data.to_csv(csv_path, index=True)
    print('File was saved at {}'.format(csv_path))

from timeit import default_timer as timer
if __name__ == '__main__':
    start = timer()
    df = ifm(data = None, r = 0.005, round_num = 3)
    save_data(data = df[0], name = df[1])
    print('Total time to run code was {} sec'.format(timer() -start))  
    
        
        