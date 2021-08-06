# CIPRO_HPLC

# Getting started
Clone the git repository in the directory of your choice.
Make sure you add all the excel files you are interested in extracting data from to the "Data" directory
Change the "interested_retention" in Cipro_HPLC.py to the retention times you are interested in. 
For example, right now the script will extract any retention time that rounds to the nearets whole number to 15, 19, 20 and 22 and concatenate all that data into a single CSV file w/ excel file name attatched to each row.

## Getting started with Streamlit
Download streamlit using the command terminal type **pip install streamlit** https://pypi.org/project/streamlit/
Ensure that pandas is installed, **pip install pandas** https://pypi.org/project/pandas/
Download the repository by clicking the download button on the repo or by going in the terminal and adding git clone https://github.com/SamuelJon17/CIPRO_HPLC.git
Maneuver towards the repository on your terminal. For example for me, using a MAC, I would type **cd Desktop/ODP/Code/GitHub_Repo/CIPRO_HPLC** but note your path might differ. The same input should be the same for windows: https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/
Once your directory is the ../CIPRO_HPLC type **streamlit run hplc_streamlit.py** and you should be able to access the HPLC_clean and IFM app on your local port. For example, mine is on http://localhost:8501. Note, this is a working prototype so there might be bugs. Feel free to message me if there are any.

You will be asked to upload the HPLC files you want cleaned. Note you can upload more than one but needs to be from the same system (i.e. only uploda agilent HPLC and not agilent + thermo HPLC data). A box will ask which system you are using and what reference chemical you want from the dropdown for calculating RRT. Note if you don't see your chemical of interest or have a specific RT value, press other and type the chemiacl name (should match what is in the HPLC chromatagram, i.e. cisatracurium is 'Cis' from the HPLC). Note if you are unsure, type 1. You'll be able to see the cleaned data and asked to download if you so desire. 

For the IFM module, you'll need to upload the cleaned data (note: only one file at a time). You can change the rounding and range for RRT. This is so that we can bucket similar RRT's that might differ slightly due from run to run in HPLC (i.e. RRT 0.920 is the same as RRT 0.922 for two separate runs). You'll be given the total LCAP for each row so you can ensure that the total adds up to ~100. If it doesn't you might need to change your range or rounding but not that this is a balance. Too much rounding and range might group a lot of RRT's as the same and too little range and rounding might not be able to bucket like values thus having a wider IFM. I generally found that 0.05 range and rounding 2-3 is sufficient. In the future, RRT values will be repalced with actual chemical names from HPLC.

## Making changes
* If you want more granularity (i.e. you want 7.8, 7.9 and 8.0 rather than 7.5, 7.6 or 7.7), change the number after the comma of line 74: "round(series['Peak\nRetention\nTime'][i],0)" to either 1,2,3, etc. with 1 representing first decimal place rounding, 2 == 2nd decimal place, so forth.
* If there are multiple excel spreadsheets that vary in page number, add the max page number from all sheets to 'excel_page_num'. For example: if Data_1.xslx had 20 sheets & Data_2.xlsx has 4 sheets, input 20 into the excel_page_num.
* Please email/slack me if there are any questions/concerns
