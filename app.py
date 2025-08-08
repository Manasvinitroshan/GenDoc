import streamlit as st
import google.generativeai as genai
import googlemaps
from fpdf import FPDF
from api_key import gemini_api_key, maps_api_key

# ─── Configure Gemini AI ─────────────────────────────────────────────────────────
genai.configure(api_key=gemini_api_key)
generation_config = genai.GenerationConfig(
    temperature=0.7, top_p=0.9, top_k=40, max_output_tokens=2048
)
safety_settings = [
    {"category":"HARM_CATEGORY_HARASSMENT",        "threshold":"BLOCK_MEDIUM_AND_ABOVE"},
    {"category":"HARM_CATEGORY_HATE_SPEECH",       "threshold":"BLOCK_MEDIUM_AND_ABOVE"},
    {"category":"HARM_CATEGORY_SEXUALLY_EXPLICIT","threshold":"BLOCK_MEDIUM_AND_ABOVE"},
    {"category":"HARM_CATEGORY_DANGEROUS_CONTENT","threshold":"BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# ─── Configure Google Maps ───────────────────────────────────────────────────────
gmaps = googlemaps.Client(key=maps_api_key)

# ─── Prompt template ─────────────────────────────────────────────────────────────
systems_prompt = """
You are a medical image analysis assistant.

Patient info:
 • Age: {age}
 • Gender: {gender}
 • Symptom duration: {duration} days
 • Fever: {fever}

Please provide:
1) Bullet-point findings from the image.
2) Top 3 possible diagnoses (ranked).
3) Recommended next steps.
4) A disclaimer.
"""

# ─── Streamlit page config ──────────────────────────────────────────────────────
st.set_page_config(page_title="GenDoc", page_icon="🩺")
st.title("GenDoc")
st.write("Upload an image, enter patient info & ZIP code, then get findings, local specialists, chat Q&A, and a PDF report.")

# ─── Initialize session state ───────────────────────────────────────────────────
for key in ("analysis","chat_session","chat_history","places"):
    if key not in st.session_state:
        st.session_state[key] = None if key!="chat_history" else []

# ─── Sidebar inputs ─────────────────────────────────────────────────────────────
st.sidebar.header("Patient & Location Info")
age      = st.sidebar.number_input("Age", 0, 120, 30, key="age")
gender   = st.sidebar.selectbox("Gender", ["Male","Female","Other"], key="gender")
duration = st.sidebar.number_input("Symptom Duration (days)", 0, 365, 1, key="duration")
fever    = st.sidebar.checkbox("Fever present", key="fever")
zip_code = st.sidebar.text_input("ZIP Code", "", key="zip_code")

# ─── Upload & analyze image ─────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload medical image (PNG/JPG)", type=["png","jpg","jpeg"])
if uploaded and st.button("Analyze Image"):
    # Generate analysis
    img = uploaded.getvalue()
    prompt = systems_prompt.format(age=age, gender=gender, duration=duration, fever=fever)
    resp = model.generate_content({"parts":[{"mime_type":uploaded.type,"data":img},{"text":prompt}]})
    st.session_state.analysis = resp.text.strip()
    st.session_state.chat_session = model.start_chat()
    st.session_state.chat_session.send_message(st.session_state.analysis)
    st.session_state.chat_history = []
    # clear previous places
    st.session_state.places = None

# ─── Display Findings ────────────────────────────────────────────────────────────
if st.session_state.analysis:
    st.markdown("## Findings & Recommendations")
    for line in st.session_state.analysis.split("\n"):
        if line.strip():
            st.markdown(f"- {line.strip()}")

# ─── Chat follow-up Q&A ──────────────────────────────────────────────────────────
if st.session_state.chat_session:
    st.markdown("## Ask a follow-up question:")
    for role, msg in st.session_state.chat_history:
        st.chat_message(role).write(msg)
    q = st.chat_input("Your question…")
    if q:
        chat = st.session_state.chat_session
        r = chat.send_message(q)
        st.session_state.chat_history += [("user", q), ("assistant", r.text)]
        st.chat_message("user").write(q)
        st.chat_message("assistant").write(r.text)

# ─── Nearby specialists ─────────────────────────────────────────────────────────
primary_dx = None
if st.session_state.analysis and zip_code:
    # find first diagnosis line
    for ln in st.session_state.analysis.split("\n"):
        if ln.strip().startswith("2)"):
            idx = st.session_state.analysis.split("\n").index(ln)
            for cand in st.session_state.analysis.split("\n")[idx+1:]:
                if cand.strip():
                    primary_dx = cand.split(":",1)[0].strip().lstrip("123). ")
                    break
            break

    if primary_dx:
        # choose specialty
        spec = "physician"
        d = primary_dx.lower()
        if any(k in d for k in ["dermatitis","psoriasis","tinea","rash"]):
            spec = "dermatologist"
        elif "pneumonia" in d:
            spec = "pulmonologist"
        elif "diabetes" in d:
            spec = "endocrinologist"

        g = gmaps.geocode(zip_code)
        if g:
            loc = g[0]["geometry"]["location"]
            ps = gmaps.places_nearby(location=(loc["lat"],loc["lng"]), radius=20000, type="hospital", keyword=spec)
            st.session_state.places = ps.get("results",[])[:5]
            st.markdown(f"## Nearby {spec.title()} Departments / Specialists")
            for place in st.session_state.places:
                st.write(f"**{place['name']}** – {place.get('vicinity','')}")

# ─── PDF report download ─────────────────────────────────────────────────────────
if st.session_state.analysis:
    # Build PDF
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial","B",18)
    pdf.cell(0,12,"GenDoc Medical Report",ln=True,align="C")
    pdf.ln(4)

    # Patient Info
    pdf.set_font("Arial","B",14)
    pdf.cell(0,8,"Patient Information",ln=True)
    pdf.set_font("Arial",size=12)
    pdf.cell(40,6,"Age:",ln=False);      pdf.cell(0,6,str(age),ln=True)
    pdf.cell(40,6,"Gender:",ln=False);   pdf.cell(0,6,gender,ln=True)
    pdf.cell(40,6,"Duration:",ln=False); pdf.cell(0,6,f"{duration} day(s)",ln=True)
    pdf.cell(40,6,"Fever:",ln=False);    pdf.cell(0,6,"Yes" if fever else "No",ln=True)
    pdf.cell(40,6,"ZIP Code:",ln=False); pdf.cell(0,6,zip_code,ln=True)
    pdf.ln(4)

    # Findings & Recommendations as raw text
    pdf.set_font("Arial","B",14)
    pdf.cell(0,8,"Findings & Recommendations",ln=True)
    pdf.set_font("Arial",size=12)
    for line in st.session_state.analysis.split("\n"):
        if line.strip():
            pdf.multi_cell(0,6,line.strip())
    pdf.ln(4)

    # Nearby specialists, if any
    if st.session_state.places:
        pdf.set_font("Arial","B",14)
        pdf.cell(0,8,"Nearby Specialists",ln=True)
        pdf.set_font("Arial",size=12)
        for p in st.session_state.places:
            name = p["name"]
            addr = p.get("vicinity","")
            pdf.multi_cell(0,6,f"- {name} ({addr})")
        pdf.ln(4)

    # Output PDF
    data = pdf.output(dest="S").encode("latin-1","replace")
    st.download_button(
        label="📥 Download PDF Report",
        data=data,
        file_name="gendoc_report.pdf",
        mime="application/pdf"
    )
