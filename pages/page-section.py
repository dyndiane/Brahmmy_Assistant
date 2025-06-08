import streamlit as st
import base64
from PIL import Image
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Brahmmy's App - Sections",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load external CSS
def load_css():
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    with open("static/css/section.css") as f:
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
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: rgba(34, 34, 34, 0.95);
        display: flex;
        align-items: center;
        padding: 0 20px;
        z-index: 1000;
        border-bottom: 2px solid #b8864b;
    }
    /* Style for the back button */
    .stButton button {
        background: none !important;
        border: none !important;
        color: #b8864b !important;
        font-size: 1.5em !important;
        padding: 10px 20px !important;
        transition: all 0.2s !important;
        box-shadow: none !important;
        position: fixed !important;
        top: 10px !important;
        left: 20px !important;
        z-index: 1001 !important;
    }
    .stButton button:hover {
        color: #fff !important;
        transform: translateX(-5px) !important;
    }
    .box-model-outer {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        width: 100vw;
        height: 100vh;
        background: #b8864b;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .box-model-border {
        width: 100vw;
        height: 100vh;
        background: #222;
        border: none;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .box-model-padding {
        width: 100vw;
        height: 100vh;
        background: #222;
        border: none;
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
        font-size: 2em;
        padding: 1px;
        border-radius: 32px;
        border: none !important;
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        min-width: 0px;
        min-height: 0px;
        box-shadow: none !important;
    }
    .section-btn {
        width: 400px;
        font-size: 0.5em;
        margin: 10px 0;
        padding: 20px 0;
        border-radius: 16px;
        border: none;
        background: #b8864b;
        color: #222;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
    }
    .section-btn:hover {
        background: #fff;
        color: #b8864b;
    }
    .section-image-wrapper {
        display: inline-block;
        position: relative;
        border-radius: 18px;
        margin-right: 1cm;
        /* Optional: for smooth corners */
    }
    .section-image {
        display: block;
        border-radius: 18px;
        width: 300px;
        min-width: 100px;
        height: auto;
        border: none !important;
        position: relative;
        z-index: 2;
    }
    .section-image-wrapper::before {
        content: "";
        position: absolute;
        top: -8px; left: -8px; right: -8px; bottom: -8px;
        border-radius: 24px;
        z-index: 1;
        pointer-events: none;
    }
    </style>
"""
st.markdown(box_model_css, unsafe_allow_html=True)

# Add top bar with back button
st.markdown("""
    <div class="top-bar">
    </div>
""", unsafe_allow_html=True)

# Add back button
if st.button("← Back", key="back_btn", help="Go back to main page"):
    st.switch_page("pages/landing.py")

# Load and encode the image as base64 PNG
img = Image.open("Brahmmyp-s.png")
buffered = BytesIO()
img.save(buffered, format="PNG")
img_b64 = base64.b64encode(buffered.getvalue()).decode()

# Centered content in the box model with image and four vertical buttons
st.markdown(
    f"""
    <div class="box-model-outer">
        <div class="box-model-border">
            <div class="box-model-padding">
                <div class="box-model-content">
                    <div class="section-image-wrapper">
                        <img src="data:image/png;base64,{img_b64}" class="section-image" alt="Brahmmy"/>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-start;">
                        <div style="font-size: 1.0em; font-weight: bold; margin-bottom: 20px; color: #fff;">
                            Choose what department <br/> you want to explore:
                        </div>
                        <a href="/app?section=architecture"><button class="section-btn">Architecture</button></a>
                        <a href="/app?section=computer_engineering"><button class="section-btn">Computer Engineering</button></a>
                        <a href="/app?section=industrial_engineering"><button class="section-btn">Industrial Engineering</button></a>
                        <a href="/app?section=information_technology"><button class="section-btn">Information Technology</button></a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

section = st.query_params.get("section", "architecture")

