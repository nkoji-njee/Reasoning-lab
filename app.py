import streamlit as st
import google.generativeai as genai
import hashlib
import json
import datetime
# 1. CLOUD SECRETS SETUP
# We will set the API_KEY in the Streamlit Cloud Dashboard later
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# 2. BAYESIAN ENGINE
if 'alpha' not in st.session_state:
    st.session_state.alpha = 2.0
    st.session_state.beta = 8.0
    st.session_state.chat_history = []

def update_bayesian(evidence_score):
    st.session_state.alpha += evidence_score
    st.session_state.beta += (5.0 - evidence_score)
# 3. UI LAYOUT
st.title("🧠 Reasoning Lab: Pixitex Prototype")
st.subheader(f"Current Reasoning Maturity: {st.session_state.alpha / (st.session_state.alpha + st.session_state.beta):.2%}")

# Chat Window
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Student Input
if prompt := st.chat_input("Analyze the data..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
      # Call AI Coach
    response = model.generate_content(f"System: You are the Reasoning Lab Coach. Student says: {prompt}")
    
    with st.chat_message("assistant"):
        st.markdown(response.text)
        st.session_state.chat_history.append({"role": "assistant", "content": response.text})

    # HIDDEN AUDITOR (Induction)
    audit_query = f"Audit this response for reasoning quality (0.0 to 1.0). Return ONLY a number: {prompt}"
    audit_score = float(model.generate_content(audit_query).text.strip())
    update_bayesian(audit_score)

    # HASHING (Trust Anchor)
    block = f"{prompt}|{st.session_state.alpha}|{datetime.datetime.now()}"
    st.sidebar.write(f"Session Hash: {hashlib.sha256(block.encode()).hexdigest()[:10]}...")

