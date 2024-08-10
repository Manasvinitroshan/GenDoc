import streamlit as st 
from pathlib import Path
import google.generativeai as genai

#set page config

st.set_page_config(page_title="VitalImage Analytics",page_icon=':robot')

st.title("VitalImage Analytics")
st.subheader("An application that can help give medical advice based on image provided")
uploaded_file = st.file_uploader("Upload a medical image for analysis", type=["png","jpeg", "jpg"])





