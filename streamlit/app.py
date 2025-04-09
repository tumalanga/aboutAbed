# .\st\scripts\activate
# streamlit run app.py

from pathlib import Path
import streamlit as st
from PIL import Image
from utils.path_helper import from_root

css_path = from_root("styles", "main.css")
# --- PATH SETTINGS ----
# current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
# css_file = "styles/main.css"
css_path = from_root("styles", "main.css")
# profile_file = "assets/pp.jpg"
profile_file = from_root("assets", "me.jpg")
# resume_file = "assets/DonovanAbednego_cv.pdf"
resume_file = from_root("assets", "DonovanAbednego_cv.pdf")

# --- GENERAL SETTINGS ----
PAGE_TITLE = "Digital CV | Donovan Abednego"
PAGE_ICON = ":wave:"
NAME = "Donovan Abednego"
DESCRIPTION = "Seeking opportunities to apply analytical expertise and automation skills in a dynamic professional setting."
EMAIL = "donovan.abednego@gmail.com"
SOCIAL_MEDIA = {"LinkedIn":"linkedin.com/in/dabednego"}

# --- header. WAJIB DI ATAS! ----
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- CSS, pdf and prof pic ----
with open(css_path) as f:
    css = f.read()
    st.markdown("<style>{}</style>".format(css), unsafe_allow_html=True)
about_page = st.Page(
    page="views/landing.py",
    title="About Me",
    default=True
)

project_1 = st.Page(
    page="views/instantDaviz.py",
    title="Quick Data Visualisation"
)

pg = st.navigation({"info":[about_page],
                    "Projects": [project_1]
                    })
pg.run()