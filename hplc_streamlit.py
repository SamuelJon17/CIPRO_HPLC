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

def get_table_download_link(df, file_name, clean = 'y'):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    if clean == 'y' or clean == 'thresh':
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        #href =f'<a href="data:file/csv;base64,{b64}" download="HPLC_clean_data.csv">Download Clean HPLC CSV file</a>'
        if clean == 'y':
            extension = 'Cleaned'
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_{extension}.csv">Download Clean HPLC CSV file</a>'
        elif clean == 'thresh':
            extension = 'Cleaned&Threshold'
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_{extension}.csv">Download Clean & Removed LCAP HPLC CSV file</a>'
    elif clean == 'n':
        csv = df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_IFM.csv">Download IFM CSV file</a>'
        #href = f'<a href="data:file/csv;base64,{b64}" download="HPLC_IFM_data.csv">Download IFM CSV file</a>'
    return href

def rrt_range(rrt, range_ = None, rounding_num = None):
    rrt = float(rrt)
    range_ = float(range_)
    rounding_num = int(rounding_num)
    return [round(rrt-range_,rounding_num),round(rrt+range_,rounding_num)]

def average(lst):
    return sum(lst) / len(lst)

def drop_lcap(dataframe, threshold = 0.2):
    #file = pd.read_csv(dataframe, dtype = object, header = 0)
    file = dataframe
    file = file.rename(columns = {'Peak\nArea\nPercent':'Peak_Area_Percent'})
    file_drop = file.groupby('id').apply(lambda x: x.loc[x.Peak_Area_Percent >= float(threshold)]).reset_index(drop=True)
    file_drop['Peak_Area_Percent'] = pd.to_numeric(file_drop["Peak_Area_Percent"])
    file_other = 100 - file_drop.groupby('id')['Peak_Area_Percent'].agg('sum')
    file_other = pd.DataFrame({'id':file_other.index, 'Peak_Area_Percent':file_other.values,
                               'Peak\nRetention\nTime':999, 'RRT (ISTD)': str(999), 'Compound': 'Other', 'Area':999,
                               'Height':999, 'Compound Amount': 000})
    file = pd.concat([file_drop, file_other], ignore_index = True).rename(columns = {'Peak_Area_Percent': 'Peak\nArea\nPercent'})
    return file

################################
# Clean HPLC Module
################################
st.subheader('Upload Excel File(s) for Cleaning')
files = st.file_uploader('Multiple files can be added at once', accept_multiple_files=True )
output_name = st.text_input('Please enter the name you would like for the returned dataset: ')
if output_name == '':
    output_name = 'HPLC_Clean_Data'
system = st.selectbox('Are you using an agilent or thermo system?',('agilent', 'thermo'))

reference_chem = st.selectbox('Please select a reference chemical for RRT', ('Midazolam', 'CIPRO', 'Cis', 'Cis Besylate', 'Other'), index = 2)
if reference_chem == 'Other':
    reference_chem = st.text_input(
        "Input a reference chemical not listed from the dropdown or a specific RT value (ex. 2.11)?")

remove_lcap = st.selectbox('Would you like to remove all LCAPs below a threshold?',('yes', 'no'), index = 1)
if remove_lcap == 'yes':
    lcap_thresh = st.text_input("Please input the minimum LCAP value allowed: ")

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
                    except:
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
    if remove_lcap == 'yes':
        drop_lcap_df = drop_lcap(all_data_list, lcap_thresh)
        st.markdown(get_table_download_link(drop_lcap_df, file_name=output_name,clean='thresh'), unsafe_allow_html=True)
    try:
        st.dataframe(all_data_list)
        st.dataframe(drop_lcap_df)
    except Exception as e:
        st.write('There was an error displaying the data in real time. However, you can still download the cleaned data using the link below.')
        #st.write(e)
    st.markdown(get_table_download_link(all_data_list, file_name=output_name, clean='y'), unsafe_allow_html=True)

################################
# IFM Module
################################
st.subheader('Upload a CSV file for IFM')
ifm_file = st.file_uploader('Only one file at a time.',accept_multiple_files=False)
output_name_2 = st.text_input('Please enter the name you would like for the returned IFM dataset: ')
if output_name_2 == '':
    output_name_2 = 'IFM_Data'
round_num = st.selectbox('How many digits would you like RT to be rounded by?', (1, 2, 3, 4, 5), index = 2)
r = st.selectbox('What range would you like to bucket values?', (0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1), index = 1)
if st.button('Impurity fate mapping'):
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

    # Some reason, 999 is being read as a float, 999.0 so when performing:
    # [list(set(series.loc[series['RRT (ISTD)'] == str(i)]['Compound'].tolist())) for i in new_set]
    # str(i) for i in new_set is '999.0' and is not the same as series['RRT (ISTD)'] == '999'
    # This is a workaround
    try:
        new_set = list(new_set)
        new_set[-1] = str(int(new_set[-1]))
        new_set = set(new_set)
    except ValueError:
        new_set = set(new_lst)

    rrt_to_names = [list(set(series.loc[series['RRT (ISTD)'] == str(i)]['Compound'].tolist())) for i in new_set]
    rrt_to_names = [item for items in rrt_to_names for item in items]
    st.subheader('Impurity Fate Mapping')
    df = pd.DataFrame.from_dict(final_dict, orient='index', columns=final_rrt_lst, dtype=object)

    # Used to add a row with column names. However running into datatype issues with multi dtypes in a single column
    df_names = df.append(pd.DataFrame([rrt_to_names], columns=df.columns, index=['Compound_name']).fillna('n.a.').astype(object))
    try:
        df = df.reindex(sorted(df.columns), axis=1)
        df['Total LCAP'] = df.sum(axis=1)

        df_names = df_names.reindex(sorted(df_names.columns), axis=1)
        df_values = df_names.iloc[0:df_names.shape[0] - 1]
        df_names['Total LCAP'] = df_values.sum(axis=1)
    except ValueError:
        st.write('Error at rounding {} and range {}'.format(round_num, r))
    try:
        st.write(df_names)
        st.write('IFM with compound names')
        st.markdown(get_table_download_link(df_names, file_name=output_name_2, clean='n'), unsafe_allow_html=True)
    except:
        st.write(
            'There was an error displaying the data with compound names in real time. However, you can still download the IFM data with names using the link below data.')
        st.write(df)
        st.markdown(get_table_download_link(df_names, file_name= output_name_2, clean='n'), unsafe_allow_html=True)

################################
# Need Help Module
################################
need_help = st.expander('Need help? 👉')
with need_help:
    st.markdown("Having trouble with either modules? Feel free to contact " + '<a href="mailto:jsamuel@ondemandpharma.com">Jon</a>' + ' or '+ '<a href="mailto:LTruong@ondemandpharma.com ">Loan.</a>', unsafe_allow_html=True)
