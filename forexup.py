# # -----API Section-----
import pandas as pd
import numpy as np

gsheetkey = "1qsyZS3H9S3lcHYyn3TXR7VoCuPLsFHlUL7GRvSNDeGI"
url_before=f'https://docs.google.com/spreadsheets/d/{gsheetkey}/export?format=csv&gid=0'
df_before = pd.read_csv(url_before)

url=f'https://docs.google.com/spreadsheets/d/{gsheetkey}/export?format=csv&gid=191653358'
df = pd.read_csv(url)

get_name = pd.merge(df[['currency','currency_name']].rename(columns={'currency_name':'current'}),\
         df_before[['currency','currency_name']].rename(columns={'currency_name':'former'}),\
            on='currency',how='left').drop_duplicates(subset='currency')
get_name['currency_name'] = np.where(get_name['former'].isna()==True,get_name['current'],get_name['former'])

keep = pd.concat([df_before,df])
finals = pd.merge(keep.rename(columns={'currency_name':'target'}),get_name[['currency','currency_name']], on='currency')\
    [['date', 'currency', 'base_currency', 'currency_name', 'exchange_rate']]
finals['options'] = finals['currency_name']+" ("+finals['currency']+")"
finals.to_pickle("streamlit/assets/rates.pkl")

print(f"Pickle created with {finals[['currency']].drop_duplicates().shape[0]} currencies (fiat and crypto)")