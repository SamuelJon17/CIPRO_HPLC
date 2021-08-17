# CIPRO_HPLC

## Getting started with Streamlit
* You will need to ensure the following packages are installed on your computer
  * Streamlit **pip install streamlit** https://pypi.org/project/streamlit/
  * Pandas **pip install pandas** https://pypi.org/project/pandas/
  * Openpyxl **pip install openpyxl** https://pypi.org/project/openpyxl/
  * Xlrd **pip install xlrd** https://pypi.org/project/xlrd/
* Download the repository by clicking the download button on the repo or by going in the terminal and adding **git clone https://github.com/SamuelJon17/CIPRO_HPLC.git**
* Change directories to the repository using your terminal. For example, using a MAC I would type **cd Desktop/ODP/Code/GitHub_Repo/CIPRO_HPLC** but note your path will differ. The syntax, **cd**, should be the same for windows: https://www.howtogeek.com/659411/how-to-change-directories-in-command-prompt-on-windows-10/
* Once your directory has changed to CIPRO_HPLC, *../CIPRO_HPLC*, type **streamlit run hplc_streamlit.py** and you should be able to access the HPLC_clean and IFM app on your local port. For example, my computer runs streamlit on http://localhost:8501. Please be advised that this is a working prototype so there might be bugs. If there are any feel free to message me. 

**Clean Module**
You will be asked to upload the HPLC files you want cleaned. Note you can upload more than one but needs to be from the same system (i.e. only uploda agilent HPLC and not agilent + thermo HPLC data). A box will ask which system you are using and what reference chemical you want from the dropdown for calculating RRT. Note if you don't see your chemical of interest or have a specific RT value, press other and type the chemiacl name (should match what is in the HPLC chromatagram, i.e. cisatracurium is 'Cis' from the HPLC). If you are unsure, type 1. You'll be able to see the cleaned data and asked to download if you so desire. 

**IFM module**
For the IFM module, you'll need to upload the cleaned data, from the clean module (note: only one file at a time). You can change the rounding and range for RRT. This is so that we can bucket similar RRT's that might differ slightly due from run to run in HPLC (i.e. RRT 0.920 is the same as RRT 0.922 for two separate runs). You'll be given the total LCAP for each row so you can ensure that the total adds up to ~100. If it doesn't you might need to change your range or rounding but not that this is a balance. Too much rounding and range might group a lot of RRT's as the same and too little range and rounding might not be able to bucket like values thus having a wider IFM. I generally found that 0.05 range and rounding 2-3 is sufficient. For your convinience, RRT & their respective chemical names are represented as a new row.

**Future**
* It was suggested that the IFM module notify users if their chromatogram passed specification for drug substance / product. I plan to incorporate a feature that checks and reports 0 = False, 1 = True & possibly a color change so users can easily identify if their samples passed specification. 
* Deployment for easier access. In the future this will be accessible like any other website where you type in the URL and have access to the modules.

**Suggestions / Concerns**
If you have any further suggestions, concerns, bugs feel free to contact either Jon, jsamuel@ondemandpharma.com or Loan, ltruong@ondemandpharma.com.




