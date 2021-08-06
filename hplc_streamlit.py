#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import streamlit as st
import pandas as pd
from xlrd import XLRDError
import base64

col1, mid, col2 = st.columns([10,1,25])

with col1:
    st.image('supporting_docs/odp_logo.png', width=200)
with col2:
    st.title('Cleaning HPLC Data And Impurity Fate Mapping')

def get_table_download_link(df, clean = True):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    if clean:
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href =f'<a href="data:file/csv;base64,{b64}" download="HPLC_clean_data.csv">Download Clean HPLC CSV file</a>'
    else:
        csv = df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="HPLC_IFM_data.csv">Download IFM CSV file</a>'
    return href

def rrt_range(rrt, range_ = None, rounding_num = None):
    rrt = float(rrt)
    range_ = float(range_)
    rounding_num = int(rounding_num)
    return [round(rrt-range_,rounding_num),round(rrt+range_,rounding_num)]

def average(lst):
    return sum(lst) / len(lst)

#st.title('Cleaning HPLC Data And Impurity Fate Mapping')

st.subheader('Upload Excel File(s) for Cleaning')
files = st.file_uploader('Multiple files can be added at once', accept_multiple_files=True )

system = st.selectbox('Are you using an agilent or thermo system?',('agilent', 'thermo'))
reference_chem = st.selectbox('Please select a reference chemical for RRT', ('Midazolam', 'CIPRO', 'Cis'), index = 2)

if st.button("Other reference?"):
    reference_chem = st.text_input("Input a reference chemical not listed from the dropdown or a specific RT value (ex. 2.11)?")

if st.button("Clean-up HPLC Data"):
    if files is not None:
        all_data_list = []
        for uploaded_file in files:
            if system == 'agilent':
                for k in range(1, 999):
                    sheetname = 'Page ' + str(k)
                    try:
                        series = pd.read_excel(uploaded_file, dtype = object, sheet_name = sheetname, header = None, index_col = None)
                        if type(series.at[2, 0]) is str:
                            identifcation = series.at[2, 4]
                            if 'blank' in identifcation.lower():
                                identifcation = identifcation + ' ' + str(uploaded_file.name.split('.')[0]) + ' ' + str(k)
                            continue
                        else: #Dealing with different Agilents [Beyonce]
                            try:
                                if series.at[6, 1] == 'Sample name:':
                                    identifcation = series.at[6, 5]
                                    if 'blank' in identifcation.lower():
                                        identifcation = identifcation + ' ' + str(uploaded_file.name.split('.')[0]) + ' ' + str(k)
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
                            if len(series[series['Compound'].str.endswith(reference_chem, na=False)]) > 0:
                                reference_series = series[series['Compound'].str.endswith(reference_chem, na=False)]
                                reference_value = reference_series.iloc[0]['Peak\nRetention\nTime']
                            else:
                                reference_value = reference_chem
                            series['RRT (ISTD)'] = [float(x) / float(reference_value) for x in series['Peak\nRetention\nTime']]
                        except:
                            series['RRT (ISTD)'] = series['Peak\nRetention\nTime']

                        series['id'] = identifcation
                        series['excel sheet'] = uploaded_file.name.split('.')[0]
                        series['page number'] = k
                        all_data_list.append(series)
                    except XLRDError:
                        print('Page {} does not exist in Excel spreadsheet {}'.format(k, uploaded_file.name))
                        break

            elif system == 'thermo': #This is for Thermo units
                identification = pd.read_excel(uploaded_file, dtype = object, sheet_name = 'Integration', header = None, index_col = None).at[4,2]
                data = pd.read_excel(uploaded_file, dtype = object, sheet_name = 'Integration', header = 0, index_col = None, skiprows = 46).drop([0,1])
                data = data[~data['No. '].isin(['n.a.', 'Total:'])]
                data['id'] = identification
                data['excel_sheet'] = pd.read_excel(uploaded_file, dtype = object, sheet_name = 'Overview', header = None, index_col = None).at[3,2]

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

            else:
                st.write('Please ensure that only thermo or agilent files are processed together')
    all_data_list = pd.concat(all_data_list)
    st.subheader('Clean HPLC data')
    st.dataframe(all_data_list)
    st.markdown(get_table_download_link(all_data_list, clean=True), unsafe_allow_html=True)

#st.markdown(get_table_download_link(all_data_list, clean = True), unsafe_allow_html=True)

st.subheader('Upload a CSV file for IFM')
ifm_file = st.file_uploader('Only one file at a time.',accept_multiple_files=False)
round_num = st.selectbox('How many digits would you like RT to be rounded by?', (1, 2, 3, 4, 5), index = 2)
r = st.selectbox('What range would you like to bucket values?', (0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), index = 4)
if st.button('Impurity fate mapping?'):
    series = pd.read_csv(ifm_file, dtype = object, header = 0)
    lst = series['RRT (ISTD)'].tolist()  # represents list of relative retention times, make sure to round prior
    ranges = [rrt_range(lst[0], range_=r, rounding_num=round_num)]  # represents ranges of unique list
    range_dict = {str(rrt_range(lst[0], range_=r, rounding_num=round_num)): lst[0]}
    new_lst = []  # represents unique list of relative retention times based on ranges, initialize with the first number
    for i, num in enumerate(lst):
        num = float(num)
        if any(r[0] <= num <= r[1] for r in
               ranges):  # if num is within any of the ranges, add the number that corresponds to that range to new_list
            # boolean =  [r[0] <= num <= r[1] for r in ranges] #return the index where num is in ranges
            index = [i for i, x in enumerate([r[0] <= num <= r[1] for r in ranges]) if x]
            if len(index) == 2:
                if abs(num - average(ranges[index[0]])) > (abs(num - average(ranges[index[1]]))):
                    index = [index[1]]
                else:
                    index = [index[0]]
            new_lst.append(range_dict[str(ranges[index[0]])])
        else:
            ranges.append(rrt_range(num, range_=r, rounding_num=round_num))
            range_dict.update({str(rrt_range(num, range_=r, rounding_num=round_num)): num})
            new_lst.append(num)
    series['RRT (ISTD)_new'] = new_lst
    new_set = set(new_lst)  # unique values of list + sort
    final_dict = {}
    subset = series.groupby(['id']).apply(lambda x: x[['RRT (ISTD)_new', 'Peak\nArea\nPercent']].values).to_dict()
    for key, value in subset.items():
        test_list = [i if i in subset[key][:, 0].tolist() else 0 for i in list(new_set)]
        for idx2, j in enumerate(subset[key][:, 0].tolist()):
            if subset[key][:, 0][idx2] in test_list:
                test_list[test_list.index(j)] = round(float(subset[key][:, 1].tolist()[idx2]),2)
        final_dict.update({key: test_list})
    final_rrt_lst = [round(float(x), round_num) for x in new_set]
    df = pd.DataFrame.from_dict(final_dict, orient='index', columns=final_rrt_lst)
    try:
        df = df.reindex(sorted(df.columns), axis=1)
        df['Total LCAP'] = df.sum(axis=1)
        # check = []
        # for k in subset.keys():
        #     subset[k] = pd.DataFrame(subset[k])
        #     subset[k] = subset[k].append(subset[k].sum(numeric_only=True), ignore_index=True)  # Adds a sum row to each sample
        #     if round(df.loc[k, 'Total LCAP'], 2) != round(subset[k].loc[len(subset[k]) - 1, 1], 2):
        #         check.append(k)
        #
        # if len(check) >= 1:
        #     # CGREEN = '\033[1;32;40m'
        #     # CEND = '\033[1;30;46m'
        #     #st.write(('\033[31m' + 'Total LCAP of samples {} do NOT match with raw data. Please try smaller range, bigger rounding, or both' + '\033[30m').format(check))
        #     st.markdown(
        #         'Total LCAP of samples' + '<span style="color:red"> {} </span>'.format(
        #             check) + ' do NOT match with raw data. Please try smaller range, bigger rounding, or both', unsafe_allow_html=True)
    except ValueError:
        st.write('Error at rounding {} and range {}'.format(round_num, r))
    st.subheader('Impurity Fate Mapping')
    st.dataframe(df)
    st.markdown(get_table_download_link(df, clean=False), unsafe_allow_html=True)

need_help = st.expander('Need help? 👉')
with need_help:
    st.markdown("Having trouble with either modules? Feel free to " + '<a href="mailto:jsamuel@ondemandpharma.com">contact</a>' + ' me!', unsafe_allow_html=True)
    #st.markdown('<a href="mailto:jsamuel@ondemandpharma.com">Email</a>', unsafe_allow_html=True)
