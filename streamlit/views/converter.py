import streamlit as st
import pandas as pd
import kagglehub, shutil, os
import datetime as dt
import numpy as np
from utils.path_helper import from_root

# fundamentals
file = from_root("assets/", "rates.csv")
rates = pd.read_pickle(file).sort_values(by='currency',ascending=True)
# rates['options'] = rates['currency_name']+" ("+rates['currency']+")"
dari = rates['options'].unique()
ke = rates['options'].unique()
 
# inputs
with st.form("Filtered App 01 currency"):
    st.header("Set Currency")

    col1, col2 = st.columns([1, 1])

    with col1:
        從 = st.selectbox(
            "From:",
            dari,
            index=None,
            placeholder="tap here",
            key="from"
        )

    with col2:
        到 = st.selectbox(
            "To:",
            ke,
            index=None,
            placeholder="tap here",
            key="to"
        )

    submitted_01 = st.form_submit_button("Apply Filters")

if submitted_01:
    st.write("From ", 從," to ", 到)

    # calculations
    forgs = pd.merge(rates[rates['options']==從][['date','exchange_rate']].rename(columns={'exchange_rate':從}),\
            rates[rates['options']==到][['date','exchange_rate']].rename(columns={'exchange_rate':到}),\
                on="date")
    forgs['date'] = forgs['date'].dt.strftime('%Y-%m-%d')
    forgs["result"] = np.where(forgs[到]/forgs[從]<1,forgs[到]/forgs[從],round(forgs[到]/forgs[從],2))
    # with st.form("filter based on date"):
    #     today = dt.datetime.now()
    #     yearn = today.year - 1
    #     jan_1 = dt.date(yearn, 1, 1)
    #     di = st.date_input("Select the date range:",
    #                     (jan_1, forgs['date'].max()),
    #                     min_value=forgs['date'].min(),
    #                     max_value=forgs['date'].max(),
    #                     format="MM.DD.YYYY")
    #     submitted_02 = st.form_submit_button("Apply date")
    #     if submitted_02:
    #     # st.write(forgs['date'].info())
    #         print(di)
    #     st.dataframe(forgs[(forgs['date']>=forgs['date'].min()) & (forgs['date']<=forgs['date'].max())][['date','result']].sort_values(by='date',ascending=False))
    #     st.line_chart(forgs[forgs['date']>="2016-01-01"][['date','result']], x="date", y="result", color=None)

    #     st.write("Disclaimer: for visualisation purpose only. Basic currency was converted from Euro to various currencies during that day.")
    #     st.write("Data References: ","https://www.kaggle.com/datasets/asaniczka/forex-exchange-rate-since-2004-updated-daily")
    st.dataframe(forgs[(forgs['date']>=forgs['date'].min()) & (forgs['date']<=forgs['date'].max())][['date','result']].sort_values(by='date',ascending=False))
    st.line_chart(forgs[forgs['date']>="2016-01-01"][['date','result']], x="date", y="result", color=None)

    st.write("Disclaimer: for visualisation purpose only. Basic currency was converted from Euro to various currencies during that day.")
    st.write("Data References: ","https://www.kaggle.com/datasets/asaniczka/forex-exchange-rate-since-2004-updated-daily")