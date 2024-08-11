import streamlit as st 
from pathlib import Path
import google.generativeai as genai

from api_key import api_key

genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}


#apply safety settings
safety_settings[
    
    {
        
        

}


]

#set page config

st.set_page_config(page_title="VitalImage Analytics",page_icon=':robot')

st.title("VitalImage Analytics")
st.subheader("An application that can help give medical advice based on image provided")
uploaded_file = st.file_uploader("Upload a medical image for analysis", type=["png","jpeg", "jpg"])





