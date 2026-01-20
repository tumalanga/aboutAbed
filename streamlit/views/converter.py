import streamlit as st
import pandas as pd
import kagglehub, shutil, os
import datetime as dt
import numpy as np
from utils.path_helper import from_root

# fundamentals
file = from_root("assets/", "rates.pkl")
rates = pd.read_pickle(file).sort_values(by='currency',ascending=True)
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
    forgs['date'] = pd.to_datetime(forgs['date']).dt.strftime('%Y-%m-%d')
    forgs["result"] = np.where(forgs[到]/forgs[從]<1,forgs[到]/forgs[從],round(forgs[到]/forgs[從],2))
    st.dataframe(forgs[(forgs['date']>=forgs['date'].min()) & (forgs['date']<=forgs['date'].max())][['date','result']].sort_values(by='date',ascending=False))
    st.line_chart(forgs[forgs['date']>="2016-01-01"][['date','result']], x="date", y="result", color=None)

    st.write("Disclaimer: for visualisation purpose only. Basic currency was converted from Euro everyday.")
    st.markdown(
    "Data References (for data showed before November 2025): "
    "[Kaggle](https://www.kaggle.com/datasets/asaniczka/forex-exchange-rate-since-2004-updated-daily)")
    st.markdown(
    "Data References (for data showed from November 2025): "
    "[Currbeacon](https://currencybeacon.com/)")