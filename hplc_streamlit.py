#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:38:10 2021

@author: samueljon
"""
import streamlit as st
import pandas as pd
import base64
#import streamlit_analytics

# username = st.sidebar.text_input("User Name")
# password = st.sidebar.text_input("Password",type='password')
# login = st.sidebar.button('login')


#if (username == st.secrets["DB_USERNAME"]) & (password == st.secrets["DB_PASSWORD"]):
#if (login) & (username.lower() == 'odp_user') & (password == 'Open123$'):
# st.sidebar.write('Welcome odp_user!')
st.set_page_config(layout="wide")
col1, mid, col2 = st.columns([10, 25, 3.5])
with col1:
    st.image('supporting_docs/odp_logo.png', width=225)
with col2:
    st.text('Updated 02/10/22')



def get_table_download_link(df, file_name, group_by, clean='y'):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    if clean == 'y' or clean == 'thresh':
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        # href =f'<a href="data:file/csv;base64,{b64}" download="HPLC_clean_data.csv">Download Clean HPLC CSV file</a>'
        if clean == 'y':
            extension = 'Cleaned'
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_{extension}.csv">Download Clean HPLC CSV file</a>'
        elif clean == 'thresh':
            extension = 'Cleaned&Threshold'
            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_{extension}.csv">Download Clean & Removed LCAP HPLC CSV file</a>'
    elif clean == 'n':
        csv = df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}_{group_by}_IFM.csv">Download IFM CSV file</a>'
        # href = f'<a href="data:file/csv;base64,{b64}" download="HPLC_IFM_data.csv">Download IFM CSV file</a>'
    return href


def rrt_range(rrt, range_=None, rounding_num=None):
    rrt = float(rrt)
    range_ = float(range_)
    rounding_num = int(rounding_num)
    return [round(rrt - range_, rounding_num), round(rrt + range_, rounding_num)]


def average(lst):
    return sum(lst) / len(lst)


def drop_lcap(dataframe, threshold=0.2):
    # file = pd.read_csv(dataframe, dtype = object, header = 0)
    file = dataframe
    file.rename({'Peak\nArea\nPercent': 'Peak_Area_Percent', 'Peak Area\nPercent': 'Peak_Area_Percent'}, axis=1,
                inplace=True)
    file_drop = file.groupby('id').apply(lambda x: x.loc[x.Peak_Area_Percent >= float(threshold)]).reset_index(
        drop=True)
    file_drop['Peak_Area_Percent'] = pd.to_numeric(file_drop["Peak_Area_Percent"])
    file_other = file.groupby('id')['Peak_Area_Percent'].agg('sum') - file_drop.groupby('id')['Peak_Area_Percent'].agg(
        'sum')  # Updated to have total sum - non-dropped vs. 100 - non-dropped
    file_other = pd.DataFrame({'id': file_other.index, 'Peak_Area_Percent': file_other.values,
                               'Peak_Retention_Time': 999, 'RRT (ISTD)': str(999), 'Compound': 'Other', 'Area': 999,
                               'Height': 999, 'Compound Amount': 000})
    file = pd.concat([file_drop, file_other], ignore_index=True)
    return file


def normRRT(data, reference_chem, thermo=True):
    if thermo:
        try:  ## Normalizing RRT
            if len(data[data['Peak Name'].str.endswith(reference_chem, na=False)]) > 0:
                reference_series = data[data['Peak Name'].str.endswith(reference_chem, na=False)]
                reference_value = reference_series.iloc[0]['RT']
            else:
                reference_value = reference_chem
            data['RRT'] = [float(x) / float(reference_value) for x in data['RT']]
        except:  ## The case if the reference_chem is not found
            data['RRT'] = data['RT']
    else:
        try:
            if len(data[data['Compound'].str.endswith(reference_chem, na=False)]) > 0:
                reference_series = data[data['Compound'].str.endswith(reference_chem, na=False)]
                reference_value = reference_series.iloc[0]['Peak\nRetention\nTime']
            else:
                reference_value = reference_chem
            data['RRT (ISTD)'] = [float(x) / float(reference_value) for x in data['Peak\nRetention\nTime']]
        except:
            data['RRT (ISTD)'] = data['Peak\nRetention\nTime']
    return data


def thermo1(uploaded_file, reference_chem):
    identification = \
    pd.read_excel(uploaded_file, dtype=object, sheet_name='Integration', header=None, index_col=None).at[4, 2]
    data = pd.read_excel(uploaded_file, dtype=object, sheet_name='Integration', header=0, index_col=None,
                         skiprows=46).drop([0, 1])

    data = data[~data['No. '].isin(['n.a.', 'Total:'])]
    data['id'] = identification
    try:
        data['excel_sheet'] = pd.read_excel(uploaded_file, dtype=object, sheet_name='Overview', header=None, index_col=None).at[3, 2]
    except:
        try:
            data['excel_sheet'] = '-'.join(identification.split('-')[0:3])
        except:
            data['excel_sheet'] = identification
    data = normRRT(data, reference_chem=reference_chem, thermo=True)
    data = data.rename(columns={'Peak Name': 'Compound', 'RT': 'Peak_Retention_Time', 'RRT': 'RRT (ISTD)',
                                'LCAP ': 'Peak_Area_Percent', 'Area ': 'Area',
                                'Height ': 'Height'})
    try:  # Renaming columns and shortening columns
        data = data.rename(columns={'Amount ': 'Compound Amount'})
        data = data[['Peak_Retention_Time', 'RRT (ISTD)', 'Peak_Area_Percent', 'Area', 'Height', 'Compound',
                     'Compound Amount', 'id', 'excel_sheet']]
        data['Compound Amount'].replace({'n.a.': 0}, inplace=True)
    except KeyError:  # Midaz does not have 'compound amount; and instead has 'S/N'
        data = data[['Peak_Retention_Time', 'RRT (ISTD)', 'Peak_Area_Percent', 'Area', 'Height', 'Compound',
                     'id', 'excel_sheet']]
    return data


def thermo2(uploaded_file, reference_chem):
    identification = \
    pd.read_excel(uploaded_file, dtype=object, sheet_name='Integration', header=None, index_col=None).at[3, 2]
    data = pd.read_excel(uploaded_file, dtype=object, sheet_name='Integration', header=0, index_col=None,
                         skiprows=39).drop([0, 1])

    data = data[~data['No. '].isin(['n.a.', 'Total:'])]
    data['id'] = identification
    data['excel_sheet'] = identification
    data = data.rename(columns={'Retention Time': 'RT'})
    data['RRT'] = data['RT']  # RRT isn't present in Lab 4 reports
    data = normRRT(data, reference_chem=reference_chem, thermo=True)
    data = data.rename(columns={'Peak Name': 'Compound', 'RT': 'Peak_Retention_Time', 'RRT': 'RRT (ISTD)',
                                'Relative Area ': 'Peak_Area_Percent', 'Area ': 'Area',
                                'Height ': 'Height', 'Relative Height ': 'Relative_Height',
                                'Amount ': 'Compound Amount'})
    data = data[['Peak_Retention_Time', 'RRT (ISTD)', 'Peak_Area_Percent', 'Area', 'Height', 'Compound',
                 'Compound Amount', 'id', 'excel_sheet']]
    data['Compound Amount'].replace({'n.a.': 0}, inplace=True)
    return data


def agilent(uploaded_file, sheetname, reference_chem):
    series = pd.read_excel(uploaded_file, dtype=object, sheet_name=sheetname, header=None, index_col=None)
    if type(series.at[2, 0]) is str:
        identifcation = series.at[2, 4]
        if 'blank' in identifcation.lower():
            identifcation = identifcation + ' ' + str(uploaded_file.name.split('.')[0]) + ' ' + str(k)
        else:
            identifcation = identifcation + ' page ' + str(k)
        return identifcation
    else:  # Dealing with different Agilents [Beyonce]
        try:
            if series.at[6, 1] == 'Sample name:':
                identifcation = series.at[6, 5]
                if 'blank' in identifcation.lower():
                    identifcation = identifcation + ' ' + str(uploaded_file.name.split('.')[0]) + ' ' + str(k)
                else:
                    identifcation = identifcation + ' page ' + str(k)
                return identifcation
            elif 'signal' not in str(series.at[0, 0]).lower():
                series = series.iloc[1:]  # Remove the first row
                series = series.reset_index(drop=True)  # Reset index numbers
        except KeyError:
            if 'signal' not in str(series.at[0, 0]).lower():
                series = series.iloc[1:]  # Remove the first row
                series = series.reset_index(drop=True)  # Reset index numbers

    start_index = series[
                      0].first_valid_index() + 1  # Finds the first non-null in column 0, Generally this is where "Signal" is
    series = series.iloc[start_index:]  # Remove all data above ""Peak Retention Time"
    headers = series.iloc[0]
    series = pd.DataFrame(series.values[1:], columns=headers)  # Renames column names to Peak retention time, etc.
    series = series.loc[:, series.columns.notnull()]  # Removes all dead space from Excel merged columns
    series = series.dropna(thresh=2)  # Removes all rows that have more than 2 NaN
    series = series[series['Peak\nRetention\nTime'].notna()]
    series = normRRT(series, reference_chem, thermo=False)  ## Normalize RRT based on reference_chem
    series = series.rename(columns={'Peak\nRetention\nTime': 'Peak_Retention_Time', 'RRT': 'RRT (ISTD)',
                                    'Peak\nArea\nPercent': 'Peak_Area_Percent',
                                    'Peak Area\nPercent': 'Peak_Area_Percent'})
    return series
#streamlit_analytics.start_tracking()
colClean, spacer1, colIFM= st.columns((10,.35,10))

colClean.title('HPLC Clean-Up')
with colClean:
    ################################
    # Clean HPLC Module
    ################################
    st.subheader('Upload Excel File(s) for Cleaning')
    files = st.file_uploader('Multiple files can be added at once', accept_multiple_files=True)
    output_name = st.text_input('Please enter the name you would like for the returned dataset: ')
    if output_name == '':
        output_name = 'HPLC_Clean_Data'
    system = st.selectbox('Are you using an agilent or thermo system?', ('agilent', 'thermo'), index =1)

    reference_chem = st.selectbox('Please select a reference chemical for RRT',
                                  ('Midazolam', 'CIPRO', 'Cis', 'Cis Besylate', 'Other'), index=2)
    if reference_chem == 'Other':
        reference_chem = st.text_input(
            "Input a reference chemical not listed from the dropdown or a specific RT value (ex. 2.11)?")

    remove_lcap = st.selectbox('Would you like to remove all LCAPs below a threshold?', ('yes', 'no'), index=1)
    if remove_lcap == 'yes':
        lcap_thresh = st.text_input("Please input the minimum LCAP value allowed: ")

    selectivity_name = ''
    ignore_names = ''
    if system == 'agilent':
        selectivity = st.selectbox(
            'Would you like to only like to clean certain files? i.e. only R5? Note, only applicable for Agilent Systems',
            ('yes', 'no'), index=1)
        if selectivity == 'yes':
            selectivity_name = st.text_input("Please input the compound(s) you want cleaned. If entering more than one please separate with a comma with no space in between. For example, 'r5,blank' :")
        ignore = st.selectbox(
            'Would you like to ignore certain names? For example, ignore blanks. Note, only applicable for Agilent Systems',
            ('yes', 'no'), index=1)
        if ignore == 'yes':
            ignore_names = st.text_input("Please input the compound(s) you want to ignore. If entering more than one please separate with a comma with no space in between. For example, 'r5,blank' :")

    if st.button("Clean-up HPLC Data"):
        if files is not None:
            all_data_list = []
            for uploaded_file in files:
                if system == 'agilent':
                    for k in range(1, 999):
                        sheetname = 'Page ' + str(k)
                        try:
                            id_series = agilent(uploaded_file, sheetname, reference_chem)
                            if type(id_series) == str:
                                identifcation = id_series
                                continue
                            else:
                                if selectivity_name != '':
                                    selectivity_name_list = list(map(str.lower,selectivity_name.split(',')))
                                    #if selectivity_name.lower() not in identifcation.lower():
                                    if not any(substring in identifcation.lower() for substring in selectivity_name_list):
                                        continue
                                if ignore_names != '':
                                    ignore_names_list = list(map(str.lower,ignore_names.split(',')))
                                    if any(substring in identifcation.lower() for substring in ignore_names_list):
                                        continue
                                id_series['id'] = identifcation
                                id_series['excel_sheet'] = uploaded_file.name.split('.')[0]
                                id_series['page_number'] = k
                                all_data_list.append(id_series)
                        except:
                            st.write('Page {} does not exist in Excel spreadsheet {}'.format(k, uploaded_file.name))
                            break
                elif system == 'thermo':  # This is for Thermo units
                    try:
                        data = thermo1(uploaded_file, reference_chem)
                    except:
                        data = thermo2(uploaded_file, reference_chem)
                    all_data_list.append(data)
                else:
                    st.write('Please ensure that only thermo or agilent files are processed together')
                    break
        if len(all_data_list) == 0:
            st.write(
                'No objects to concatenate, please ensure that the proper items were selected. Note if using an Aglient system you might have to resave the excel spreadsheet and upload those to the clean-up module.')
        else:  # Dropping LCAP + Displaying Data + Saving
            all_data_list = pd.concat(all_data_list)
            st.subheader('Clean HPLC data')
            if remove_lcap == 'yes':
                drop_lcap_df = drop_lcap(all_data_list, lcap_thresh)
                st.markdown(get_table_download_link(drop_lcap_df, file_name=output_name,group_by = None, clean='thresh'),
                            unsafe_allow_html=True)
            try:
                st.dataframe(all_data_list)
                st.dataframe(drop_lcap_df)
            except Exception as e:
                st.write(
                    'There was an error displaying the data in real time. However, you can still download the cleaned data using the link below.')
                # st.write(e)
            st.markdown(get_table_download_link(all_data_list, file_name=output_name, group_by = None, clean='y'), unsafe_allow_html=True)

    ################################
    # Clean FAQ
    ################################
    clean_faq = st.expander('Clean-Module FAQ')
    with clean_faq:
        """
        *** 
        #### **Clean Module**
        1. **I receive an error message when using Thermo reports.**
    
            Ensure that the file saved from the HPLC computer has the *Integration* sheet when saving as an excel spreadsheet.
    
        2. **I receive an error message when using Agilent reports.**
    
            For some reason, when exporting files from Agilent systems, an *OpenPyxl* source error appears due to faulty reading using *pandas.read_excel()*. Based on a [StackOverflow Report](https://stackoverflow.com/questions/46150893/error-when-trying-to-use-module-load-workbook-from-openpyxl)
            there appears to be some styling done on Agilent systems that corrupts the output file. To circumvent this, if you re-save (save_as) your excel spreadsheets the problem is removed. My apologies for the inconvenience. 
    
        3. **How come I receive a message saying X page doesn't exist?**
    
            The output for agilent systems are several sheets within a single excel file. The algorithm will loop from
            page 1 to 999 until there is either an actual error or until the page doesn't exist. For examlpe,
            if your excel spreadsheet has 35 pages, you should receive an error stating page 36 doesn't exist. In this case,
            the algorithm is running okay and can disregard the message. In the same example, if you receive a message stating page 1-35 doesn't exist
            then there is an actual problem with either the file or code. 
    
        4. **What is *reference chemical for RRT* feature?**
    
            Because each run has slight variations in retention time, for the impurity fate mapping grouping process, it is better to group based on a relative compound / value rather than just retention time.
            This feature allows you to choose a chemical, listed within the HPLC report (case-sensitive), or specific retention time value (i.e. 1.00) to use as reference.
    
        5. **What is *remove LCAP below threshold value* feature?**
    
            This is also a nice feature prior to importing to the IFM module. If your reports are riddled with very small peaks due potentially due to processing errors,
            you can remove those values and re-categorize them as *other*
    
        6. **What is this *999* I see in my results?**
    
            If you used the remove LCAP below threshold value feature, 999 is a place holder for *other* in the IFM module. 
    
        7. **What is the *clean certain files* feature for Agilent systems?**
    
            Because Agilent reports HPLC results on a single excel file for numerous entries, a user might only want to extract out information from a specific entry. 
            Specifically, this feature looks at the sample name, i.e. XXX-21-001-R5, and returns a cleaned/concatenated spreadsheet of entry of interest. 
            For example, if I have XXX-21-001-R5-1, XXX-21-001-R5-2, XXX-21-001-CAU-1 and want only r5 results, I would type r5 into the text box 
            and only be returned XXX-21-001-R5-1 & XXX-21-001-R5-2. Note this is only useful for Agilent systems since Thermo automatically separates 
            each entry as its own excel file. 
        ***  
        """
colIFM.title('Impurity Fate Mapping')
with colIFM:
    ################################
    # IFM Module
    ################################
    st.subheader('Upload a CSV file for IFM')
    ifm_file = st.file_uploader('Only one file at a time.', accept_multiple_files=False)
    output_name_2 = st.text_input('Please enter the name you would like for the returned IFM dataset: ')
    if output_name_2 == '':
        output_name_2 = 'IFM_Data'
    round_num = st.selectbox('How many digits would you like RRT to be rounded by?', (1, 2, 3, 4, 5), index=2)
    r = st.selectbox('What range would you like to bucket values?', (
    0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1),
                     index=1)
    group_by = st.selectbox('Would you like to return lcap%, area, height or concentrations?',
                            ('Peak_Area_Percent', 'Area', 'Height', 'Compound Amount'), index=0)

    if st.button('Impurity fate mapping'):
        series = pd.read_csv(ifm_file, dtype=object, header=0)
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

        try:  # old version
            subset = series.groupby(['id']).apply(lambda x: x[['RRT (ISTD)_new', 'Peak\nArea\nPercent']].values).to_dict()
        except:
            subset = series.groupby(['id']).apply(lambda x: x[['RRT (ISTD)_new', group_by]].values).to_dict()

        for key, value in subset.items():
            test_list = [i if i in subset[key][:, 0].tolist() else 0 for i in list(new_set)]
            for idx2, j in enumerate(subset[key][:, 0].tolist()):
                if subset[key][:, 0][idx2] in test_list:
                    test_list[test_list.index(j)] = round(float(subset[key][:, 1].tolist()[idx2]), 3)
            final_dict.update({key: test_list})
        final_rrt_lst = [round(float(x), round_num) for x in new_set]

        # Some reason, 999 is being read as a float, 999.0 so when performing:
        # [list(set(series.loc[series['RRT (ISTD)'] == str(i)]['Compound'].tolist())) for i in new_set]
        # str(i) for i in new_set is '999.0' and is not the same as series['RRT (ISTD)'] == '999'
        # This is a workaround
        if 999.0 in new_set:
            new_set = ['999' if x == 999 else x for x in new_set]
            # new_set = list(new_set)
            # new_set[-1] = str(int(new_set[-1]))
            # new_set = set(new_set)
        rrt_to_names = [list(set(series.loc[series['RRT (ISTD)'] == str(i)]['Compound'].tolist())) for i in new_set]
        rrt_to_names = [item for items in rrt_to_names for item in items]
        st.subheader('Impurity Fate Mapping')
        df = pd.DataFrame.from_dict(final_dict, orient='index', columns=final_rrt_lst, dtype=object)

        # Used to add a row with column names. However running into datatype issues with multi dtypes in a single column
        # df_names = df.append(pd.DataFrame([rrt_to_names], columns=df.columns, index=['Compound_name']).fillna('n.a.').astype(object))
        df_names = pd.concat([pd.DataFrame([rrt_to_names], columns=df.columns, index=['Compound_name']), df]).fillna(
            'n.a.').astype(object)

        try:
            df = df.reindex(sorted(df.columns), axis=1)
            sum = df.sum(axis=1)
            df['Total ' + group_by] = sum
            df_names = df_names.reindex(sorted(df_names.columns), axis=1)
            # df_values = df_names.iloc[1:df_names.shape[0]]
            sum_name = sum.tolist()
            sum_name.insert(0, 0)
            df_names['Total ' + group_by] = sum_name
        except ValueError:
            st.write('Error at rounding {} and range {}'.format(round_num, r))
        if group_by == 'Compound Amount':
            df = df.loc[:, (df != 0).any(axis=0)]
        try:
            st.write(df_names)
            st.write('IFM with compound names')
            st.markdown(get_table_download_link(df_names, file_name=output_name_2, group_by=group_by, clean='n'), unsafe_allow_html=True)
        except:
            st.write(
                'There was an error displaying the data with compound names in real time. However, you can still download the IFM data with names using the link below data.')
            st.write(df)
            st.markdown(get_table_download_link(df_names, file_name=output_name_2, group_by=group_by, clean='n'), unsafe_allow_html=True)

    ################################
    # IFM FAQ
    ################################
    ifm_faq = st.expander('IFM-Module FAQ')
    with ifm_faq:
        """
        *** 
        #### **Impurity Fate Map Module**
        1. **How come I receive an error?**
    
            Ensure that you are uploading the clean file downloaded from the clean module and not the raw HPLC report. If you are and still receiving issues, email Jon.
    
        2. **What is the *RRT to round by* feature?**
    
            When running multiple samples for HPLC, there are slight variations within retention times that otherwise would be considered the same compound. 
            Within the clean module, referencing based on a single compound or value is the first step in tackling this problem.
            Next would be rounding the RRT to a value such that similar enough compounds are grouped together.
            For example, if compound A shows up at RRT 1.0008 for run 1 and RRT 1.0009 for run 2, rounding to the third decimal place would help group these compounds as
            1.001. However, there is drawbacks if you set the rounding to low such as round to 1 as many compounds that shouldn't share the same RRT might be grouped as one. 
            It's a trade-off system but generally found that rounding to 3 is sufficient. 
    
        3. **What does *range you would like to bucketize* mean?**
    
            Similar to the RRT rounding feature, we might want to group items that are within a certain +/- range of RRT.
            For example, if for compound A in run 1 has RRT 1.008 and run 2 has RRT 1.011 but should be the same, I'd want my range to group as 
            at least +/- 0.003 such that these values are considered the same. Similar to the rounding feature, there is a trade-off where
            if the range is too large, values that shouldn't be grouped become grouped and if too small, no grouping occurs. 0.005 was found to be the most sufficient when paired with round to 3.
            To have the optimal IFM output it's best to utilize the cleaning based on a reference chemical value feature, removing values below a threshold feature that aren't impurities but rather noise from processing, 
            and perform a rounding and group-by range feature.
    
        4. **How come some of my runs don't add up to 99.9-100.1%?**
    
            If your values do not add up to 99.9-100.1% LCAP, you might need to change the rounding or group-by range value. It is possible that
            some values are being grouped because they are very close to each other but being considered as one by the algorithm. 
    
        5. **Is it possible to see what compounds correspond to which RRT?**
    
            Yes, if available within the HPLC report, when you download the IFM file, there will be a row that contains a chemical that corresponds
            to the RRT within that column. If one was not present within the report, it will appear as n.a. 
         ***    
        """
################################
# Need Help Module
################################
need_help = st.expander("Still can't find your answer? 👉")
with need_help:
    st.markdown(
        "If you have any trouble please refer to the common FAQ first and if you don't find your solutin please Teams message or Email " + '<a href="mailto:jsamuel@ondemandpharma.com">Jon</a>' + ' or ' + '<a href="mailto:LTruong@ondemandpharma.com ">Loan.</a>' + ' Please submit a copy of the error message and file(s) that popped the error. ',
        unsafe_allow_html=True)
updates = st.expander('Updates 🆕')
with updates:
    """
    - February 10, 2022:
        - Requirement set Streamlit version to 1.4.0
    - October 11, 2021:
        - Updated layout for better user experience
        - Added more information to FAQ
        - For agilent systems, added an ignore sample name functionality. Could be useful if you want to ignore blanks, assays, etc (not case sensitive)
        - For agilent systems, updated the selective sample name to include more than one sample name. Similar to above, this will be useful if
        a user wants to only return samples with a certain name such as R3, R5 (not case sensitive)
        - For Compound Amount in IFM, remove columns that are all zero (dead-space)
    - October 8, 2021:
        - For agilent systems, updated identification to include page numbers so multiple samples that share the same name
        are not overwritten
        - Bug fix in the LCAP summing column during IFM reporting
        - For thermo reporting, added an ignore feature if the Overview page is not provided
    - Septemberr 30, 2021:
        - Expanded on IFM output to choose between LCAP, Area, Height or Compound Amount (Concentration)
        - Included formatting for Thermo output from Lab 4 HPLC
    """
#streamlit_analytics.stop_tracking(unsafe_password = 'BIGMEDS1!')
# elif (username == '') | (password == ''):
#     st.warning("Please enter a username and password")
# else:
#     st.warning("Incorrect Username/Password")
