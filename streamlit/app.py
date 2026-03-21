# .\st\scripts\activate
# streamlit run app.py

# GA tracker
import streamlit.components.v1 as components

from pathlib import Path
import streamlit as st
from PIL import Image
from utils.path_helper import from_root

css_path = from_root("styles", "main.css")
# --- PATH SETTINGS ----
# current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
# css_file = "styles/main.css"
css_path = from_root("styles", "main.css")
# html tracker
html_path = from_root("assets", "ga.html")
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
SOCIAL_MEDIA = {"LinkedIn":"https://linkedin.com/in/dabednego"}

# --- header. WAJIB DI ATAS! ----
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- CSS, pdf and prof pic ----
with open(css_path) as f, open(html_path) as r:
    # ini untuk css
    css = f.read()
    st.markdown("<style>{}</style>".format(css), unsafe_allow_html=True)
    # ini untuk tracker
    html_code = r.read()
    components.html(html_code, height=0)

about_page = st.Page(
    page="views/landing.py",
    title="About Me",
    default=True
)

project_1 = st.Page(
    page="views/instantDaviz.py",
    title="Quick Data Visualisation"
)

project_2 = st.Page(
    page="views/yt.py",
    title="Youtube data"
)

project_3 = st.Page(
    page="views/converter.py",
    title="Currency Converter"
)

project_x = st.Page(
    page="pages/pplres_1.py",
    title="Survey Report", visibility="hidden"
)

pg = st.navigation({"info":[about_page],
                    "Projects": [project_1,project_2, project_3],
                    "others": [project_x]
                    })
pg.run()