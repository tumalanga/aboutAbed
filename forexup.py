# # -----API Section-----
import pandas as pd

gsheetkey = "1qsyZS3H9S3lcHYyn3TXR7VoCuPLsFHlUL7GRvSNDeGI"

url=f'https://docs.google.com/spreadsheet/ccc?key={gsheetkey}&output=xlsx'
df = pd.read_excel(url,sheet_name="API")
df['options'] = df['currency_name']+" ("+df['currency']+")"

gsheetkey_before = "1qsyZS3H9S3lcHYyn3TXR7VoCuPLsFHlUL7GRvSNDeGI"
url_before=f'https://docs.google.com/spreadsheet/ccc?key={gsheetkey}&output=xlsx'
df_before = pd.read_excel(url,sheet_name="Result")
df_before['options'] = df_before['currency_name']+" ("+df_before['currency']+")"

pd.concat([df_before,df]).to_pickle("streamlit/assets/rates.pkl", index=False)