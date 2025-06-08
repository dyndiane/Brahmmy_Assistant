import streamlit as st

# Set page config
st.set_page_config(
    page_title="Brahmmy's App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirect to landing page
st.switch_page("pages/landing.py")