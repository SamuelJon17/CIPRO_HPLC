files = st.file_uploader('Pick a file', accept_multiple_files=True)
if st.button("Process"):
    if files is not None:
        all_data_list = []
        for uploaded_file in files:
            for k in range(1, 999):
                sheetname = 'Page ' + str(k)
                try:
                    series = pd.read_excel(uploaded_file, dtype=object, sheet_name=sheetname, header=None,
                                           index_col=None)
                    # Identification Page [Generally odd]
                    if type(series.at[2, 0]) is str:
                        identifcation = series.at[2, 4]
                        if 'blank' in identifcation.lower():
                            identifcation = identifcation + ' ' + str(uploaded_file.name.split('.')[0]) + ' ' + str(k)
                        continue
                    # elif len(series) >= 7:
                    else:
                        # This applied for data from Beyonce
                        try:
                            if type(series.at[6, 1]) == 'Sample name:':

                                st.write(series.at[2, 0])
                                st.write(series.at[2, 4])
                                st.write(series.at[6, 5])
                                st.write(series.at[6, 1])
                                st.write(type(series.at[2, 0]))
                                st.write(type(series.at[2, 4]))
                                st.write(type(series.at[6, 5]))
                                st.write(type(series.at[6, 1]))

                                identifcation = series.at[6, 5]
                                if 'blank' in identifcation.lower():
                                    identifcation = identifcation + ' ' + str(
                                        uploaded_file.name.split('.')[0]) + ' ' + str(k)
                                continue
                            elif 'signal' not in str(series.at[0, 0]).lower():
                                # Remove the first row
                                series = series.iloc[1:]
                                # Reset index numbers
                                series = series.reset_index(drop=True)
                        except KeyError:
                            if 'signal' not in str(series.at[0, 0]).lower():
                                # Remove the first row
                                series = series.iloc[1:]
                                # Reset index numbers
                                series = series.reset_index(drop=True)

                    # Finds the first non-null in column 0, Generally this is where "Signal" is
                    start_index = series[0].first_valid_index() + 1

                    # Remove all data above ""Peak Retention Time"
                    series = series.iloc[start_index:]

                    # Renames column names to Peak retention time, etc.
                    headers = series.iloc[0]
                    series = pd.DataFrame(series.values[1:], columns=headers)

                    # Removes all dead space from Excel merged columns
                    series = series.loc[:, series.columns.notnull()]
                    ## Old method
                    # series = series.loc[:,~series.columns.str.match('Unnamed')]

                    # Removes all rows that have more than 2 NaN
                    series = series.dropna(thresh=2)
                    series = series[series['Peak\nRetention\nTime'].notna()]
                    # if cipro_rt == None:
                    #     cipro_rt = input('Please input the RT of cipro to update the RRT: ')
                    #     if cipro_rt == '':
                    #         cipro_rt = 1
                    # if cipro_rt ==1:
                    #     series['RRT (ISTD)'] = series['RRT (ISTD)']
                    # else:
                    try:
                        reference_series = series["Compound"].str.find('CIPRO')
                        reference_value = reference_series.iloc[0]['Peak\nRetention\nTime']
                        series['RRT (ISTD)'] = [float(x) / float(reference_value) for x in
                                                series['Peak\nRetention\nTime']]
                    except:
                        print('Target of interest could not be found in excel sheet')
                    series['id'] = identifcation
                    series['excel sheet'] = uploaded_file.name.split('.')[0]
                    series['page number'] = k
                    all_data_list.append(series)
                except XLRDError:
                    print('Page {} does not exist in Excel spreadsheet {}'.format(k, uploaded_file.name))
                    break
            all_data_list = pd.concat(all_data_list)

            st.subheader('Raw data')
            st.dataframe(all_data_list)