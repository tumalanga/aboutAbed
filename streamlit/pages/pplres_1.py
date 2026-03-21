import streamlit as st
import os, time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.path_helper import from_root
file_parti = from_root("data/", "participants.csv")
parti = pd.read_csv(file_parti)[['id', 'username', 'date_regd', 'user_ip', 'user_ag', 'user_lang',
       'user_country', 'email', 'age', 'gender', 'race', 'time_completed']]
parti.columns = ['participant_id', 'username', 'date_registered', 'user_ip', 'user_agent', 'user_lang',
       'user_country', 'user_email', 'user_age', 'user_gender', 'user_race', 'time_completed']

file_resp = from_root("data/", "responses.csv")
resp_x = pd.read_csv(file_resp)
resp = resp_x[['id', 'participant_id', 'username',
       'created_at', 'stimulus', 'attract', 'race', 'gender', 'age', 'pic',
       'friendly', 'whiteshirt', 'actual_race', 'actual_age', 'actual_gender']]
resp.columns = ['resp_id', 'participant_id', 'username',
       'created_at', 'stimulus', 'attract', 'answer_race', 'answer_gender', 'answer_age', 'pic',
       'friendly', 'whiteshirt', 'actual_race', 'actual_age', 'actual_gender']

longr_all = pd.merge(parti, resp, on=['participant_id','username'], how='left')
longr = longr_all[longr_all['resp_id'].isna()==False].copy()
longr['res_race'] = np.where(longr['answer_race']==longr['actual_race'],True,False)
longr['res_age'] = np.where(longr['answer_age']==longr['actual_age'],0,(longr['actual_age']-longr['answer_age']))
longr['res_gender'] = np.where(longr['answer_gender']==longr['actual_gender'],True,False)
longr['race_black'] = np.where(longr['actual_race']=='Black',1,0)
longr['race_white'] = np.where(longr['actual_race']=='White',1,0)
longr['race_asian'] = np.where(longr['actual_race']=='Asian',1,0)
longr['gender_male'] = np.where(longr['actual_gender']=='Male',1,0)
# #  based on: https://www.beresfordresearch.com/age-range-by-generation/
longr['user_gen'] = np.where((longr['user_age'].replace('na', np.nan).astype(float).isna())==True,"no data",
    np.where((longr['user_age'].replace('na', np.nan).astype(float)<14),"gen A",
    np.where((longr['user_age'].replace('na', np.nan).astype(float)>=14)&(longr['user_age'].replace('na', np.nan).astype(float)<=29),"gen Z",
                np.where((longr['user_age'].replace('na', np.nan).astype(float)>=30) & (longr['user_age'].replace('na', np.nan).astype(float)<=46),"Millenials",
                        "Gen X Above")
                                            )))
longr['groups'] = np.where((longr['whiteshirt']==1) & (longr['friendly']==1),"Friendly White T-shirt",
    np.where((longr['whiteshirt']==1) & (longr['friendly']==0),"Normal White T-shirt",
            np.where((longr['whiteshirt']==0) & (longr['friendly']==1),"Friendly Blue T-shirt",
                        np.where((longr['whiteshirt']==0) & (longr['friendly']==0),"Normal Blue T-shirt","Other"))))

longr_parti = longr.groupby(['resp_id', 'participant_id', 'username', 'date_registered', 'user_ip', 'user_agent',
       'user_race', 'user_gender', 'user_age', 'user_email', 'user_country', 'user_gen']).agg(
    score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
).reset_index()

st.title("Demography")
st.markdown(f"""Total survey from 3 countries: {longr_parti.shape[0]}\n
Germany: {longr_parti[longr_parti['user_country']=='Germany'].shape[0]}\n
Taiwan: {longr_parti[longr_parti['user_country']=='Taiwan'].shape[0]}\n
Vietnam: {longr_parti[longr_parti['user_country']=='Vietnam'].shape[0]}\n
""")
st.write("""Data Demography \n
         reference: https://www.beresfordresearch.com/age-range-by-generation/
""")
# Use Barchart 我覺得比較好
demo = longr_parti.copy()
demo['user_age'] = demo['user_age'].replace('na', np.nan).astype(float)
st.bar_chart(demo[['user_country','user_gen']].groupby(['user_country','user_gen']).agg(
    total=pd.NamedAgg(column="user_gen", aggfunc="count"),
    ).reset_index().sort_values(by=['user_country','user_gen']),
    x='user_country', y="total", color="user_gen", stack=False)

st.write(
    longr_parti.groupby(['user_country','user_gen','user_gender']).agg(
    total=pd.NamedAgg(column="user_gen", aggfunc="count"),
    ).reset_index().sort_values(by=['user_country','user_gen', "user_gender"]))

st.title("Exploration")
cou = st.multiselect(
    "Select respondent's country:",
    longr['user_country'].unique(),
    default=None,
)

if not cou:
    st.error("please input the Country")
if cou:
    target = longr_parti[longr_parti['user_country'].isin(cou)]
    exp = longr[longr['user_country'].isin(cou)]

    exp_stats = exp[['resp_id', 'participant_id', 'pic',
                    'answer_race', 'answer_gender', 'answer_age',
                    'race_black', 'race_white', 'race_asian', 'gender_male',
                    'actual_race', 'actual_gender', 'actual_age',
                    'stimulus', 'friendly', 'whiteshirt',
                    'res_race', 'res_gender', 'res_age',
                    'attract']].copy()

    st.write("Top 20 'friendly' photos")
    friendly = exp.groupby(['pic',
        # 'actual_race', 'actual_gender',
        'actual_age', 'friendly', 'whiteshirt',
        'race_black', 'race_white', 'race_asian', 'gender_male']).agg(
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
    # stimulus_mode=pd.NamedAgg(column="stimulus", aggfunc=pd.Series.mode),
    attract=pd.NamedAgg(column="attract", aggfunc="median"),
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    attract_sum=pd.NamedAgg(column="attract", aggfunc="sum")
    ).reset_index().sort_values(by='attract_avg', ascending = False)
    st.bar_chart(friendly.head(20),
                x='pic', y='attract_avg', stack=False, sort='-attract_avg')
    st.write(friendly.head(20))

    st.write("Groups")
    groups = exp.groupby(['groups']).agg(
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
    # stimulus_mode=pd.NamedAgg(column="stimulus", aggfunc=pd.Series.mode),
    attract=pd.NamedAgg(column="attract", aggfunc="median"),
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    attract_sum=pd.NamedAgg(column="attract", aggfunc="sum")
    ).reset_index().sort_values(by='attract_avg', ascending = False)

    st.bar_chart(groups,
    x='groups', y='attract_avg', stack=False, sort='-attract_avg',horizontal=True)
    st.write(groups)

    st.write("Age overview")
    st.write(
    exp.groupby(['actual_age']).agg(
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_age_mean=pd.NamedAgg(column="res_age", aggfunc="mean"),
    attract=pd.NamedAgg(column="attract", aggfunc="median"),
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    attract_sum=pd.NamedAgg(column="attract", aggfunc="sum")
    ).reset_index().sort_values(by='score_age', ascending = False))

    st.write("Adding races to support age variable")
    st.write(
    exp.groupby(['actual_age','actual_race']).agg(
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    # score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_age_mean=pd.NamedAgg(column="res_age", aggfunc="mean"),
    # score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
    # stimulus_mode=pd.NamedAgg(column="stimulus", agg func=pd.Series.mode),
    attract=pd.NamedAgg(column="attract", aggfunc="median"),
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    attract_sum=pd.NamedAgg(column="attract", aggfunc="sum")
    ).reset_index().sort_values(by='score_age', ascending = False))