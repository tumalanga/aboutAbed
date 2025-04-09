# .\st\scripts\activate
# streamlit run app.py

import streamlit as st

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