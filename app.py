import streamlit as st
import anthropic
import hashlib
import json
import datetime
# 1. CLOUD SECRETS SETUP
# We will set the API_KEY in the Streamlit Cloud Dashboard later
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-5"

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
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system="You are the Reasoning Lab Coach.",
        messages=[{"role": "user", "content": prompt}],
    )
    coach_text = response.content[0].text

    with st.chat_message("assistant"):
        st.markdown(coach_text)
        st.session_state.chat_history.append({"role": "assistant", "content": coach_text})

    # HIDDEN AUDITOR (Induction)
    audit_response = client.messages.create(
        model=MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": f"Audit this response for reasoning quality (0.0 to 1.0). Return ONLY a number: {prompt}"}],
    )
    try:
        audit_score = float(audit_response.content[0].text.strip())
    except (ValueError, IndexError):
        audit_score = 0.5
    update_bayesian(audit_score)

    # HASHING (Trust Anchor)
    block = f"{prompt}|{st.session_state.alpha}|{datetime.datetime.now()}"
    st.sidebar.write(f"Session Hash: {hashlib.sha256(block.encode()).hexdigest()[:10]}...")

