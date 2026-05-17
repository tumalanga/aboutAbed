import streamlit as st


st.title("Coming Soon!")
# from pathlib import Path
# import os, time, gspread, json
# from PIL import Image
# import pandas as pd
# from utils.path_helper import from_root

# creds = json.loads(st.secrets["gcp_service_account"])
# gc = gspread.service_account_from_dict(creds)
# gc_open = gc.open_by_key(st.secrets["cv_id"])

# per_dat = gc_open.get_worksheet_by_id(st.secrets["cv_per"])
# perdat = pd.DataFrame(per_dat.get_all_records())
# perdat = perdat[perdat['lang']=='en']

# tskill = gc_open.get_worksheet_by_id(st.secrets["cv_ts"])
# tsdat = pd.DataFrame(tskill.get_all_records())
# tsdat = tsdat[tsdat['lang']=='en']

# exper = gc_open.get_worksheet_by_id(st.secrets["cv_pe"])
# pedat = pd.DataFrame(exper.get_all_records())
# pedat = pedat[pedat['lang']=='en']

# educ = gc_open.get_worksheet_by_id(st.secrets["cv_edu"])
# edudat = pd.DataFrame(educ.get_all_records())
# edudat = edudat[edudat['lang']=='en']

# traindat = gc_open.get_worksheet_by_id(st.secrets["cv_tr"])
# trdat = pd.DataFrame(traindat.get_all_records())
# trdat = trdat[trdat['lang']=='en']

# # --- PATH SETTINGS ----
# profile_file = from_root("assets", "me.png")
# resume_file = from_root("assets", "DonovanAbednego_cv.pdf")

# # --- GENERAL SETTINGS ----
# NAME = perdat['name'][0]
# DESCRIPTION = perdat['about'][0]
# EMAIL = perdat['email'][0]
# SOCIAL_MEDIA = {"My LinkedIn":perdat['linkedin'][0]}
# EMAIL_LINK = f"mailto:{perdat['email'][0]}"

# # --- CSS, pdf and prof pic ----
# with open(resume_file,"rb") as pdf_file:
#     PDFbyte = pdf_file.read()
# profile_pic = Image.open(profile_file)

# # --- mukadimah ----
# col1,col2 = st.columns(2, gap="small")
# with col1:
#     st.image(profile_pic)
# with col2:
#     st.title(NAME)
#     st.write(DESCRIPTION)

#     st.markdown(f"""
#     <a href="{SOCIAL_MEDIA['My LinkedIn']}" target="_blank" style="color:#0077B5; text-decoration:none; font-weight:bold;">
#         LinkedIn
#     </a>
#     |
#     <a href="{EMAIL_LINK}" target="_blank" style="color:#0077B5; text-decoration:none; font-weight:bold;">
#         Keep in Touch
#     </a>
#     """, unsafe_allow_html=True)

#     st.download_button(
#         label = "Download Resume",
#         data=PDFbyte,
#         file_name=str(from_root("assets", "DonovanAbednego_cv.pdf")).replace("\\","/").split("/")[-1],
#         mime="application/octet-stream"
#     )

# # st.write("#")
# st.subheader("Experience")
# st.write("---")
# st.write("""
# - 💼 Experienced in on-site, remote, and hybrid work environments.
# - 📈 Passionate about data-driven decision-making and process automation, with a strong focus on optimizing dataflows and reporting through scripting and advanced analytical tools to enhance efficiency.
# - 👟 Skilled in collaborating with clients and stakeholders, managing upward communication, and addressing ad-hoc data requirements to support business objectives.""")

# st.write("#")
# st.subheader("Hard Skills")
# st.write("---")
# for index, row in tsdat.iterrows():
#     st.write(f"- {row['icon']}{row['skills']} : {row['objects']}")

# st.write("#")
# st.subheader("Working Experience")
# st.write("---")
# for index, row in pedat.iterrows():
#     st.write(f"**{row['place']} | {row['job']}**")
#     st.write(f"{row['time']} | {row['location']}")
#     st.write(f"""
#     {row['about']}
#     """)
#     st.write("##")

# st.subheader("Education")
# st.write("---")
# for index, row in edudat.iterrows():
#     st.write(f"**{row['uni']} | {row['time']}**")
#     st.write(f"{row['degree']} | {row['location']}")

# st.write("#")
# st.subheader("Other Course")
# st.write("---")
# # trdat[['lang', 'program', 'host', 'location', 'year']]
# for index, row in trdat.iterrows():
#     st.write(f"**{row['program']} | {row['year']} ({row['length']})**")
#     st.write(f"{row['host']} | {row['location']}")