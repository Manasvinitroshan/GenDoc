````markdown name=README.md
# GenDoc – Medical Image AI Assistant

A Streamlit app that uses Google Gemini AI to analyze medical images, lets users ask follow-up questions via chat, finds nearby specialists by ZIP code (using Google Maps), and generates a clean PDF report.

---

## 🚀 Features

- **Image Analysis**:  
  - Upload a PNG/JPG medical image  
  - Gemini returns:
    - Bullet-point findings  
    - Top 3 possible diagnoses (ranked)  
    - Recommended next steps  
    - Disclaimer  

- **Chat Q&A**: Follow up on the initial analysis with free-form questions.  

- **Nearby Specialists**: Enter your ZIP code; the app shows local hospitals/departments for the predicted condition.  

- **PDF Report**: Download a formatted PDF including:
  - Patient info  
  - Findings & recommendations  
  - Nearby specialist list  
  - (All text safely encoded)  

---

## 📦 Requirements

- Python 3.10+  
- [Streamlit](https://streamlit.io/) 1.48.0  
- [google-generativeai](https://pypi.org/project/google-generativeai/) 0.8.5  
- [googlemaps](https://pypi.org/project/googlemaps/) 4.10.0  
- [FPDF](https://pypi.org/project/fpdf/) 1.7.2  

Dependencies are listed in `requirements.txt`.

---

## 🔧 Installation & Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/Manasvinitroshan/medicalimagedetector.git
   cd medicalimagedetector
   ```

2. **Create & activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   # .\venv\Scripts\activate     # Windows PowerShell
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **API Keys**

   * **Google Gemini AI**: enable Gemini in Google Cloud, get an API key.
   * **Google Maps**: enable Geocoding API & Places API, get an API key.
   * Create `api_keys.py` at the project root (gitignored) with:

     ```python
     gemini_api_key = "YOUR_GEMINI_API_KEY"
     maps_api_key   = "YOUR_GOOGLE_MAPS_API_KEY"
     ```

5. **Run locally**

   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment on Streamlit Cloud

1. Push your code to GitHub (exclude `api_keys.py`).
2. (Optional) Use Streamlit Secrets by adding `.streamlit/secrets.toml`:

   ```toml
   [gemini]
   api_key = "YOUR_GEMINI_API_KEY"

   [google_maps]
   api_key = "YOUR_GOOGLE_MAPS_API_KEY"
   ```
3. Create a new app at [streamlit.io/cloud](https://streamlit.io/cloud), point it at your repo’s `main` branch and `app.py`.

---

## 📝 License

MIT © Manasvinitroshan

````
