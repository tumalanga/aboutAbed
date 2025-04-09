# References: 
# https://www.youtube.com/watch?v=2siBrMsqF44
# Soli Deo Gloria
# .\env\Scripts\activate 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.write("simple data dashboard")
st.write("based on: ",)

uploaded_file = st.file_uploader("Chooese a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("Data Preview")
    st.write(df.head())
    
    st.subheader("Data Summary")
    st.write(df.describe())
    
    st.subheader("Filter Data")
    collie = df.columns.to_list()
    selected_columns = st.selectbox("Select column to filter by", collie)
    unique_values = df[selected_columns].unique()
    selected_values = st.selectbox("select value",unique_values)

    filtered_df = df[df[selected_columns] == selected_values]
    st.write(filtered_df)

    st.subheader("Plot Data")
    x_column = st.selectbox("select x-axis column", collie)
    y_column = st.selectbox("select y-axis column", collie)

    if st.button("Generate Plot"):
        st.line_chart(filtered_df.set_index(x_column)[y_column])
else:
    st.write("Waiting on file upload")