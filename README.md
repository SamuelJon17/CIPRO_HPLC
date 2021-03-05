# CIPRO_HPLC

# Getting started
Clone the git repository in the directory of your choice.
Make sure you add all the excel files you are interested in extracting data from to the "Data" directory
Change the "interested_retention" in Cipro_HPLC.py to the retention times you are interested in. 
For example, right now the script will extract any retention time that rounds to the nearets whole number to 15, 19, 20 and 22 and concatenate all that data into a single CSV file w/ excel file name attatched to each row.

## Making changes
* If you want more granularity (i.e. you want 7.8, 7.9 and 8.0 rather than 7.5, 7.6 or 7.7), change the number after the comma of line 29: "round(series['Peak\nRetention\nTime'][i],0)" to either 1,2,3, etc. with 1 representing first decimal place rounding, 2 == 2nd decimal place, so forth.
* Please email/slack me if there are excel spreadsheet(s) that start the table name: "Peak retention time | RRT (ISTD) | ..." on a different row from 7 on page 2. If this occurs, the data extracted will be shifted and not extract right and might require a more complex solution. 
