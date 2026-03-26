import streamlit as st
import os, time, gspread, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.path_helper import from_root

# with open("service_account.json") as f:
#     creds = json.load(f)
# gc = gspread.service_account_from_dict(creds)
creds = json.loads(st.secrets["gcp_service_account"])
gc = gspread.service_account_from_dict(creds)

file_parti = gc.open_by_key(st.secrets["pplres_1"]).get_worksheet_by_id(st.secrets["pplres_1_file_parti"])
parti = pd.DataFrame(file_parti.get_all_records())
# file_parti = from_root("data/", "participants.csv")
# parti = pd.read_csv(file_parti)
parti = parti[['id', 'username', 'date_regd', 'user_ip', 'user_ag', 'user_lang',
       'user_country', 'email', 'age', 'gender', 'race', 'time_completed']]
parti.columns = ['participant_id', 'username', 'date_registered', 'user_ip', 'user_agent', 'user_lang',
       'user_country', 'user_email', 'user_age', 'user_gender', 'user_race', 'time_completed']

file_resp = gc.open_by_key(st.secrets["pplres_1"]).get_worksheet_by_id(st.secrets["pplres_1_file_resp"])
resp_x = pd.DataFrame(file_resp.get_all_records())
# file_resp = from_root("data/", "responses.csv")
# resp_x = pd.read_csv(file_resp)
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

longr_parti = longr.groupby(['resp_id', 'participant_id', 'username', 'date_registered', 'user_ip', 'user_agent', 'user_lang',
       'user_race', 'user_gender', 'user_age', 'user_email', 'user_country', 'user_gen']).agg(
    score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    score_age=pd.NamedAgg(column="res_age", aggfunc="sum"),
    score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
).reset_index()

st.title("Demography")
st.markdown(f"""Total survey from 3 countries: {longr_parti[longr_parti['user_country']!='Other'].shape[0]}\n
Germany: {longr_parti[longr_parti['user_country']=='Germany'].shape[0]}\n
Taiwan: {longr_parti[longr_parti['user_country']=='Taiwan'].shape[0]}\n
Vietnam: {longr_parti[longr_parti['user_country']=='Vietnam'].shape[0]}\n
""")
st.write("""Data Demography \n
         reference: https://www.beresfordresearch.com/age-range-by-generation/
""")
# Use Barchart 我覺得比較好
demo = longr_parti[longr_parti['user_country']!='Other'].copy()
demo['user_age'] = demo['user_age'].replace('na', np.nan).astype(float)
st.bar_chart(demo[['user_country','user_gen']].groupby(['user_country','user_gen']).agg(
    total=pd.NamedAgg(column="user_gen", aggfunc="count"),
    ).reset_index().sort_values(by=['user_country','user_gen']),
    x='user_country', y="total", color="user_gen", stack=False)

st.write(
    longr_parti.groupby(['user_country','user_gen','user_gender']).agg(
    total=pd.NamedAgg(column="user_gen", aggfunc="count"),
    ).reset_index().sort_values(by=['user_country','user_gen', "user_gender"]))

with st.form("Filtered App 01 currency"):
    st.title("Exploration")
    col1, col2 = st.columns([1, 1])


    with col1:
        cou = st.multiselect(
            "Select respondent's country:",
            longr['user_country'].unique(),
            default=None,
        )

    with col2:
        lang = st.multiselect(
            "Select respondent's language:",
            longr['user_lang'].unique(),
            default=None,
        )

    submitted_01 = st.form_submit_button("Apply Filters")

if submitted_01:
    st.write(f"selected country(ies): {', '.join(cou)}")
    st.write(f"selected language(s): {', '.join(lang)}")
    target = longr_parti[(longr_parti['user_country'].isin(cou)) & (longr_parti['user_lang'].isin(lang))]
    exp = longr[(longr['user_country'].isin(cou)) & (longr['user_lang'].isin(lang))]

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
        # 'actual_age', 'friendly', 'whiteshirt',
        # 'race_black', 'race_white', 'race_asian', 'gender_male'
    ]).agg(
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    score_age_avg=pd.NamedAgg(column="res_age", aggfunc="mean"),
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count")
    # score_race=pd.NamedAgg(column="res_race", aggfunc="sum"),
    # score_gender=pd.NamedAgg(column="res_gender", aggfunc="sum"),
    # stimulus_mode=pd.NamedAgg(column="stimulus", aggfunc=pd.Series.mode),
    # attract=pd.NamedAgg(column="attract", aggfunc="median"),
    # attract_sum=pd.NamedAgg(column="attract", aggfunc="sum")
    ).reset_index().sort_values(by='attract_avg', ascending = False)
    st.bar_chart(friendly.head(20),
                x='pic', y='attract_avg', stack=False, sort='-attract_avg',horizontal=True)
    st.write(friendly.head(20))

    st.write("Groups")
    # Create groups
    groups = exp.groupby(['groups']).agg(
    score_age_avg=pd.NamedAgg(column="res_age", aggfunc="mean"),
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean")
    ).reset_index().sort_values(by='score_age_avg', ascending = True)

    # gather data which score_age_avg close to 0.
    groups_below_0 = groups[groups['score_age_avg']<=0].sort_values(by='score_age_avg', ascending=False).head(1)
    groups_below_0['score_age_avg'] = abs(groups_below_0['score_age_avg'])
    groups_above_0 = groups[groups['score_age_avg']>=0].sort_values(by='score_age_avg', ascending=True).head(1)
    groups_0 = pd.concat([groups_below_0,groups_above_0]).sort_values(by='score_age_avg', ascending=True)

    st.bar_chart(groups,
    x='groups', y='score_age_avg', stack=False, sort='-score_age_avg',horizontal=True)
    st.write(groups)

    group_race_age = exp[exp['groups']==groups_0.iloc[0,0]].groupby(['groups','actual_race','actual_age']).agg(
    attract_avg=pd.NamedAgg(column="attract", aggfunc="mean"),
    total_appeared=pd.NamedAgg(column="pic", aggfunc="count"),
    score_age_avg=pd.NamedAgg(column="res_age", aggfunc="mean"),
    ).reset_index().sort_values(by='attract_avg', ascending = False)

    # st.bar_chart(group_race_age,
    # x='groups', y='attract_avg', stack=False, sort='-attract_avg',horizontal=True)
    st.write(group_race_age)
