# CIPRO_HPLC

## Getting started with Streamlit
* You will need to ensure the following packages are installed on your computer
  * Streamlit **pip install streamlit** https://pypi.org/project/streamlit/
  * Pandas **pip install pandas** https://pypi.org/project/pandas/
  * Openpyxl **pip install openpyxl** https://pypi.org/project/openpyxl/
  * Xlrd **pip install xlrd** https://pypi.org/project/xlrd/
* Download the repository by clicking the download button on the repo or by going in the terminal and adding git clone https://github.com/SamuelJon17/CIPRO_HPLC.git
* Maneuver towards the repository on your terminal. For example for me, using a MAC, I would type **cd Desktop/ODP/Code/GitHub_Repo/CIPRO_HPLC** but note your path might differ. The same input should be the same for windows: https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/
* Once your directory is the ../CIPRO_HPLC type **streamlit run hplc_streamlit.py** and you should be able to access the HPLC_clean and IFM app on your local port. For example, mine is on http://localhost:8501. Note, this is a working prototype so there might be bugs. Feel free to message me if there are any.

**Clean Module**
You will be asked to upload the HPLC files you want cleaned. Note you can upload more than one but needs to be from the same system (i.e. only uploda agilent HPLC and not agilent + thermo HPLC data). A box will ask which system you are using and what reference chemical you want from the dropdown for calculating RRT. Note if you don't see your chemical of interest or have a specific RT value, press other and type the chemiacl name (should match what is in the HPLC chromatagram, i.e. cisatracurium is 'Cis' from the HPLC). Note if you are unsure, type 1. You'll be able to see the cleaned data and asked to download if you so desire. 

**IFM module**
For the IFM module, you'll need to upload the cleaned data (note: only one file at a time). You can change the rounding and range for RRT. This is so that we can bucket similar RRT's that might differ slightly due from run to run in HPLC (i.e. RRT 0.920 is the same as RRT 0.922 for two separate runs). You'll be given the total LCAP for each row so you can ensure that the total adds up to ~100. If it doesn't you might need to change your range or rounding but not that this is a balance. Too much rounding and range might group a lot of RRT's as the same and too little range and rounding might not be able to bucket like values thus having a wider IFM. I generally found that 0.05 range and rounding 2-3 is sufficient. In the future, RRT values will be repalced with actual chemical names from HPLC.

