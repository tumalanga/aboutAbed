import streamlit as st
from pathlib import Path
from PIL import Image
from utils.path_helper import from_root

# --- PATH SETTINGS ----
profile_file = from_root("assets", "me.png")
resume_file = from_root("assets", "DonovanAbednego_cv.pdf")

# --- GENERAL SETTINGS ----
NAME = "Donovan Abednego"
DESCRIPTION = "Seeking opportunities to apply analytical expertise and automation skills in a dynamic professional setting."
EMAIL = "donovan.abednego@gmail.com"
SOCIAL_MEDIA = {"My LinkedIn":"https://linkedin.com/in/dabednego"}
EMAIL_LINK = "mailto:donovan.abednego@gmail.com"

# --- CSS, pdf and prof pic ----
with open(resume_file,"rb") as pdf_file:
    PDFbyte = pdf_file.read()
profile_pic = Image.open(profile_file)

# --- mukadimah ----
col1,col2 = st.columns(2, gap="small")
with col1:
    st.image(profile_pic)
with col2:
    st.title(NAME)
    st.write(DESCRIPTION)

    st.markdown(f"""
    <a href="{SOCIAL_MEDIA['My LinkedIn']}" target="_blank" style="color:#0077B5; text-decoration:none; font-weight:bold;">
        LinkedIn
    </a>
    |
    <a href="{EMAIL_LINK}" target="_blank" style="color:#0077B5; text-decoration:none; font-weight:bold;">
        Keep in Touch
    </a>
    """, unsafe_allow_html=True)

    st.download_button(
        label = "Download Resume",
        data=PDFbyte,
        file_name=str(from_root("assets", "DonovanAbednego_cv.pdf")).replace("\\","/").split("/")[-1],
        mime="application/octet-stream"
    )

# st.write("#")
st.subheader("Experience")
st.write("---")
st.write("""
- 💼 Experienced in on-site, remote, and hybrid work environments.
- 📈 Passionate about data-driven decision-making and process automation, with a strong focus on optimizing dataflows and reporting through scripting and advanced analytical tools to enhance efficiency.
- 👟 Skilled in collaborating with clients and stakeholders, managing upward communication, and addressing ad-hoc data requirements to support business objectives.""")

st.write("#")
st.subheader("Hard Skills")
st.write("---")
st.write("""
- 🖥️ Programming: Python, SQL, Bigquery
- 💾 Data Visualization: Tableau, Data Studio
- ⚙️ Other supporting tools: Hubspot, Google Sheets, Google Slides
- 🔉 Languages: Bahasa Indonesia (native), English (CEFR B2), Mandarin Taiwan (Basic Proficiency)""")

st.write("#")
st.subheader("Working Experience")
st.write("---")
st.write("**Liven PTY LTD | Data Analyst**")
st.write("Jun 2023 - Aug 2024 | Bali, Indonesia")
st.write("""
- • Automate Monthly Revenue Reporting, Commission Report, Team Sales Report and Individual commission report for the sales team, tracking each sales performance is also possible. Made data reporting time from 3 working weeks to just 3 working days. All by using Python, Hubspot, Inhouse tools and Google Sheets.
- • Create Dataflow and datamart from the API to data platform. Prepared data from data platform to be distributed into several platforms i.e Google Sheets and Mosaic. Datamart has made data easier to be accessed efficiently by users, and the deployment of Datamart significantly enhanced data accessibility from 3 hours request into just few minutes.
""")

st.write("#")
st.write("**Tokocrypto | Social Media Data Analyst**")
st.write("Feb 2022 - Sep 2022 | Jakarta, Indonesia")
st.write("""
- •	Automate the flow and analyze the data source to stakeholders and help them to make data driven decisions by using Brandwatch, Google Colab, Google Sheets and Google slides. Hence, efficiency had been created for company since weekly Work in Progress (WIP) for social media and Corporate Communication team has made.
- • Cut the process of making weekly report from 5 days to just 3 days.  Hence, improving campaign performance and got insides from data team is a big leap for Social Media team.
""")

st.write("#")
st.write("**Redcomm Asia Inc. | Data Analyst Executive**")
st.write("Aug 2020 - Jan 2022 | Jakarta, Indonesia")
st.write("""
- • Automate Reporting process in order to support Business unit’s Data analyst and reduced 30% of reporting process by using Fanpage Karma, Google Bigquery, Google Sheet and present it in Tableau.
- • Used the same tools, created a dashboard of historical post to help Creative and Strategy team looking for inspirations for design, copy- writing and post schedule social media post for clients.
""")

st.write("#")
st.write("**Redcomm Asia Inc. | Data Analyst Freelancer for Funnel Dashboard for Telco Company**")
st.write("May 2020 - Jul 2020 | Jakarta, Indonesia")
st.write("""
- • Established a funnel dashboard to enable clients to monitor and oversee the progress of their marketing and sales efforts.
- • Tableau was the main tool to conduct the dashboard, along with sample data via google sheets and excel file.
""")
st.write("#")
st.write("**Conversant Solutions, Pte. Ltd. | Strategic Sales Executive**")
st.write("Mar 2017 - Mar 2020 | Jakarta, Indonesia")
st.write("""
- • Providing IT Solution in Content Delivery Network (CDN), Transcoding, game accelerator and Cache for company. Clients had made efficiency regarding the requests to their original servers by about 20% to 30%.
- • Partnering with Telkom International (Telin), Parolamas Insurance, Tado, Suara.com, RCTI Plus and other existing companies.	
""")

st.write("#")
st.subheader("Education")
st.write("---")
st.write("""**National Taiwan Normal University | Sep 2025 - Now**""")
st.write("""Graduate Institute of Management | Taipei, Taiwan""")
st.write("""**Bina Nusantara University | Sep 2011 - Sep 2016**""")
st.write("""Bachelor of Accounting and Information Systems | Jakarta, Indonesia""")

st.write("#")
st.subheader("Other Course")
st.write("---")
# st.write("#")
st.write("""**Ministry of Digital Affairs | Digital Innovation Talent Empowerment Program**""")
st.write("""Sep 2025 - Nov 2025 | Taipei, Taiwan""")
st.write("""- Data Science program course. The program included online courses, project-based learning, and company visits.""")
# st.write("#")
st.write("""**National Taiwan Normal University | Mandarin Training Center Non-Degree Program**""")
st.write("""Sep 2024 - Feb 2025 | Taipei, Taiwan""")
st.write("""- Huayu Enrichment Scholarship (HES) Recipient""")

st.write("""**Algoritma Data Science School | Bootcamp Data Analyst using Python**""")
st.write("""Sep 2019 - Oct 2019 | Jakarta, Indonesia""")
st.write("""**Algoritma Data Science School | Bootcamp Data Analyst and Data Science Using R**""")
st.write("""Jan 2019 - Mar 2019 | Jakarta, Indonesia""")
