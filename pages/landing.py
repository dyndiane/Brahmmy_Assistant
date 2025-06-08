import streamlit as st
import base64
from PIL import Image
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Brahmmy's App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS
def load_css():
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    with open("static/css/landing.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load CSS
load_css()

# Hide the sidebar and Streamlit's default menu/footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Hide scrollbars and prevent scrolling
hide_scroll_style = """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
    }
    ::-webkit-scrollbar {
        display: none;
    }
    </style>
"""
st.markdown(hide_scroll_style, unsafe_allow_html=True)

# CSS for full-page box model (main area much bigger)
box_model_css = """
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        margin: 0;
        padding: 0;
        background: #b8864b;
        /* height: 100vh !important; */
        /* width: 100vw !important; */
    }
    .box-model-outer {
        min-height: 100vh;
        width: 100vw;
        background: #b8864b;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .box-model-border {
        width: 100%;
        background: #222;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .box-model-padding {
        width: 100%;
        background: #222;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        color: #fff;
        text-align: center;
    }
    .box-model-content {
        background: #222;
        color: #fff;
        font-size: 3em;
        padding: 50px;
        border-radius: 32px;
        border: none !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-width: 1px;
        min-height: 1px;
        box-shadow: none !important;
    }
    .title {
        font-weight: 900;  /* Extra bold */
        margin-bottom: 20px;
    }
    .subtitle {
        font-weight: 700;  /* Bold */
        font-size: 0.5em;  /* Smaller than the title */
        margin-top: 20px;
    }
    .section-image {
        margin-right: 48px;
        border-radius: 0px !important;
        width: 300px;
        min-width: 300px;
        height: auto;
        border: none !important;
    }
    .centered-image {
        width: 300px;
        max-width: 90vw;
        height: auto;
        display: block;
        margin: 0 auto;
    }
    .clickable-image {
        cursor: pointer;
        transition: transform 0.2s;
    }
    .clickable-image:hover {
        transform: scale(1.05);
    }
    .stButton > button {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 500px;
        height: 500px;
        opacity: 0;
        cursor: pointer;
    }
    </style>
"""
st.markdown(box_model_css, unsafe_allow_html=True)

# Load and encode the image as base64 PNG
img = Image.open("brahmmy.jpg")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_b64 = base64.b64encode(buffered.getvalue()).decode()

# Centered content in the box model
st.markdown(
    f"""
    <div class="box-model-outer">
        <div class="box-model-border">
            <div class="box-model-padding">
                <div class="box-model-content">
                    <div class="title">Welcome to Brahmmy's App</div>
                    <div class="image-wrapper">
                        <img src="data:image/png;base64,{img_b64}" class="centered-image" alt="Brahmmy"/>
                    </div>
                    <div class="subtitle">Click continue to Start!</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Only a continue button to go to page-section.py
if st.button("Continue", key="continue_btn", help="Click to continue"):
    st.switch_page("pages/page-section.py")