import base64
from pathlib import Path
import streamlit as st


@st.cache()
def generate_background() -> str:
    file = Path(__file__).parent / "bg-min.png"
    data = file.read_bytes()
    return base64.b64encode(data).decode()


def generate_html():
    html_file = Path(__file__).parent / "snowfall.html"
    html_content = html_file.read_text()
    return html_content


def snowfall():
    html = generate_html()
    st.markdown("""
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
    }
    </style>
    """ % generate_background(), unsafe_allow_html=True)
    st.markdown(html, unsafe_allow_html=True)
