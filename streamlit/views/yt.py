import langcodes, datetime, importlib, pycountry, kagglehub, shutil, os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import country_converter as coco
import plotly.express as px
import altair as alt
from pathlib import Path
from PIL import Image
from countryinfo import CountryInfo
from utils.path_helper import from_root

# Get all languages
def safe_lang_name(code):
    if isinstance(code, str):
        try:
            return langcodes.Language.get(code).display_name()
        except Exception:
            return 'Unknown'
    else:
        return 'Unknown'

# get all the country lists
cc = coco.CountryConverter().data[["name_official","name_short","ISO2","ISO3","UNregion","continent","Continent_7"]]
cc['ISO2'] = cc['ISO2'].replace(to_replace=r'\$|\^', value='', regex=True)
cc['ISO2'] = cc['ISO2'].str.split('|')
cc = cc.explode('ISO2')
cc.columns = ['name_official', 'name_short', 'code_2', 'code_3', 'subregion', 'region', 'Continent_7']

def get_countryinfo_data_safe(code_2):
    name_row = cc[cc['code_2'] == code_2]
    if name_row.empty:
        return None
    name = name_row.iloc[0]['code_2']
    try:
        c = CountryInfo(name)
        info = c.info()
        return info
    except:
        return None

countryinfo_list = [get_countryinfo_data_safe(code) for code in cc['code_2']]
df_countryinfo = pd.json_normalize(countryinfo_list)
df_countryinfo.columns = [col.replace('.', '_') for col in df_countryinfo.columns]

countryInfo = pd.merge(cc,\
                       df_countryinfo[['ISO_alpha2'] + ['ISO_alpha3'] +\
                                      [col for col in df_countryinfo.columns if col not in ['ISO_alpha2','ISO_alpha3','region','subregion']]].dropna(subset="name"),\
                       left_on='code_3', right_on='ISO_alpha3', how='left').drop_duplicates(subset='code_2')

# 現在只用中文的資料
file = from_root("assets/", "sample.pkl")
yt_lang = pd.read_pickle(file).sort_values(by=['publish_date','video_id', 'snapshot_date'])

df = yt_lang[(yt_lang.publish_date>='2024-01-01')&\
                    (yt_lang.publish_date<'2025-01-01')&\
                    (yt_lang.view_count>0)]

# latest snapshot
latest = df.groupby(['video_id']).agg({'snapshot_date': 'max'}).reset_index().rename(columns={'snapshot_date':'snapshot_date_max'})

neo = pd.merge(df,latest, left_on="video_id",right_on="video_id", how="left")\
    .sort_values(by=['publish_date','country'], ascending=True)
neo['publish_date'] = pd.to_datetime(neo['publish_date'])
neo['snapshot_date'] = pd.to_datetime(neo['snapshot_date'])

# body 開始
st.title("Visualisation - Youtube")
with st.form("Filtered Data App"):
    st.header("Set Filters")

    lang = st.multiselect(
        "please select video languages",
        options=neo.lang_gen.unique().tolist(),
        default=neo.lang_gen.unique().tolist()[0:2]
    )

    min_dat, max_dat = st.slider(
        "Select a range of date",
        min_value=neo['publish_date'].min().date(),
        max_value=neo['publish_date'].max().date(),
        value=(neo['publish_date'].quantile(0.25).date(),\
            neo['publish_date'].quantile(0.75).date())
        )
    
    submitted = st.form_submit_button("Apply Filters")


if submitted:
    if not lang:
        st.error("please input the language!")
    if lang:
        st.success(f"selected language(s): {', '.join(lang)}")
        min_dat = pd.to_datetime(min_dat)
        max_dat = pd.to_datetime(max_dat)
        if min_dat.tzinfo is None:
            min_dat = min_dat.tz_localize("UTC")
        else:
            min_dat = min_dat.tz_convert("UTC")

        if max_dat.tzinfo is None:
            max_dat = max_dat.tz_localize("UTC")
        else:
            max_dat = max_dat.tz_convert("UTC")

        exp = neo[((neo.publish_date>=min_dat)&(neo.publish_date<max_dat))&
                (neo['lang_gen'].isin(lang))]
        grouped_tv = exp.groupby(['publish_date']).agg({
        'video_id': 'nunique'
        }).reset_index()
        grouped_tv_ov = grouped_tv.video_id.sum()
        grouped = exp.groupby(['publish_date', 'video_id', 'title', 'channel_name', 'lang', 'video_tags']).agg({
        'view_count': 'median',
        'like_count': 'median',
        'comment_count': 'median',
        'country':"count"
        }).reset_index()

        exp_none = neo[(neo['lang_gen'].isin(lang))]
        grouped_tv_none = exp_none.groupby(['publish_date']).agg({
        'video_id': 'nunique'
        }).reset_index()
        grouped_tv_ov_none = grouped_tv_none.video_id.sum()
        grouped_none = exp_none.groupby(['publish_date', 'lang']).agg({
        'video_id': 'nunique',
        'view_count': 'median',
        'like_count': 'median',
        'comment_count': 'median',
        'country':"count"
        }).reset_index()
        
        if exp.shape[0]>0:
        # Overview selected data.
            st.markdown(f"date: from {min_dat.strftime("%Y/%m/%d")} to {max_dat.strftime("%Y/%m/%d")}")
            st.write("Country that accessing the language:")
            st.plotly_chart(px.bar((exp.\
                groupby(['country_name','language']).agg({
                    'video_id': 'nunique'
                    }).\
                reset_index().sort_values(by='video_id',ascending=False).head(20).rename(columns={'video_id':'total videos', 'country_name': 'country'})), x='country', y='total videos', color='language').\
                        update_layout(xaxis={'categoryorder':'total descending'}))

            st.dataframe(grouped[['publish_date','title','channel_name','view_count','like_count','comment_count','video_id']])
            # Total Video related
            st.markdown(f"total video published: {grouped_tv_ov}")
            st.line_chart(grouped_tv, x="publish_date", y="video_id", color=None)

        else:
            st.markdown("Search returns zero result. Please refer to the data below:")
            st.write("Country that accessing the language:")
            st.plotly_chart(px.bar((exp_none.\
                groupby(['country_name','language']).agg({
                    'video_id': 'nunique'
                    }).\
                reset_index().sort_values(by='video_id',ascending=False).rename(columns={'video_id':'total videos', 'country_name': 'country'})), x='country', y='total videos', color='language').\
                        update_layout(xaxis={'categoryorder':'total descending'}))

            st.dataframe(grouped_none[['publish_date','lang','view_count','like_count','comment_count','video_id']].rename(columns={'video_id':'total videos'}))
            # Total Video related
            st.markdown(f"total video published: {grouped_tv_ov_none}")
            st.line_chart(grouped_tv_none, x="publish_date", y="video_id", color=None)


st.write("Data References: ","https://www.kaggle.com/datasets/asaniczka/trending-youtube-videos-113-countries/data")

