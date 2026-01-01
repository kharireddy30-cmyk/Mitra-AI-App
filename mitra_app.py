import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
import time

# 1. సీక్రెట్ కీ ని లోడ్ చేయడం
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. వెబ్ పేజీ సెట్టింగ్స్
st.set_page_config(page_title="Mitra AI Chat", page_icon="🤖", layout="wide")

# 3. క్లయింట్ సెటప్
if not api_key:
    st.error("❌ API Key దొరకలేదు! .env ఫైల్ చెక్ చేయండి.")
    st.stop()
else:
    client = genai.Client(api_key=api_key)

# 4. చాట్ హిస్టరీని దాచుకోవడానికి సెషన్ స్టేట్
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. సైడ్ బార్ - హర్ష గారి ప్రొఫైల్
with st.sidebar:
    st.title("👤 హర్ష గారి ప్రొఫైల్")
    st.markdown("---")
    st.write(f"**పేరు:** మిత్ర (హర్ష)")
    st.write("🦁 **లగ్నం:** సింహం")
    st.write("♊ **రాశి:** మిథునం")
    st.markdown("---")
    if st.button("చాట్ క్లియర్ చేయి"):
        st.session_state.messages = []
        st.rerun()
    st.info("మోడ్: ఆటో-స్విచ్ (Memory Enabled)")

# 6. ప్రధాన స్క్రీన్
st.title("Mitra AI Chat Assistant 🤖")

# గత సంభాషణను చూపించడం
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# యూజర్ ఇన్పుట్
if prompt := st.chat_input("ఇక్కడ ఏదైనా అడగండి (ఉదా: పైథాన్ గురించి లేదా మీ జాతకం గురించి)..."):
    # యూజర్ మెసేజ్ ని హిస్టరీలో చేర్చడం
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI నుండి సమాధానం పొందడం
    with st.chat_message("assistant"):
        with st.spinner("మిత్ర ఆలోచిస్తున్నాడు..."):
            # మన దగ్గర ఉన్న లిస్ట్ ప్రకారం పనిచేసే మోడల్స్
            available_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]
            full_response = ""
            success = False

            for model_name in available_models:
                try:
                    # AI కి పంపే డేటా (పూర్తి హిస్టరీతో సహా)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[{"role": "user", "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
                    )
                    full_response = response.text
                    success = True
                    break  # సమాధానం వస్తే లూప్ ఆపేస్తుంది
                except Exception as e:
                    # ఒకవేళ కోటా లిమిట్ దాటితే (429 ఎర్రర్) నెక్స్ట్ మోడల్ కి వెళ్తుంది
                    continue

            if success:
                st.markdown(full_response)
                # AI సమాధానాన్ని హిస్టరీలో దాచుకోవడం
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("క్షమించండి హర్ష గారు, గూగుల్ సర్వర్ల నుండి ప్రస్తుతానికి రెస్పాన్స్ రావడం లేదు. దయచేసి 1 నిమిషం ఆగి ప్రయత్నించండి.")

st.markdown("---")
st.caption(f"© 2026 Mitra AI | Time: {time.strftime('%H:%M')} | హర్ష గారి కోసం ప్రత్యేకం")