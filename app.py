import streamlit as st
from ai_engine import QUESTIONS, stream_reply

st.set_page_config(page_title="HealthBuddy", page_icon="🩺", layout="centered")

GREETING = {
    "English": "Hi! I'm HealthBuddy 🩺 I can run first aid practice, and help with healthy eating, mental health and exercise. What would you like to start with?",
    "Bahasa Melayu": "Hai! Saya HealthBuddy 🩺 Saya boleh bantu latihan pertolongan cemas, pemakanan sihat, kesihatan mental dan senaman. Nak mula dengan apa?",
    "Mix of both (Manglish)": "Hi! Saya HealthBuddy 🩺 I boleh bantu first aid practice, healthy eating, mental health dan exercise. Nak start dengan apa?",
}

QUICK_STARTS = {
    "🚑 First aid practice": "Let's practise first aid. Give me a scenario to try.",
    "🥗 Healthy eating": "Can you give me tips on healthy eating?",
    "🧠 Mental health": "I want to talk about stress and mental health.",
    "🏃 Exercise": "Can you suggest a simple exercise routine for me?",
}


def init_state():
    st.session_state.setdefault("stage", "onboarding")   # onboarding -> chat
    st.session_state.setdefault("q_index", 0)
    st.session_state.setdefault("profile", {})
    st.session_state.setdefault("messages", [])


def onboarding():
    st.title("🩺 HealthBuddy")
    st.caption("Answer 5 quick questions so I can help you better.")

    i = st.session_state.q_index
    q = QUESTIONS[i]
    st.progress(i / len(QUESTIONS), text=f"Question {i + 1} of {len(QUESTIONS)}")

    choice = st.radio(q["question"], q["options"], index=None, key=f"q_{i}")

    if st.button("Next" if i < len(QUESTIONS) - 1 else "Start chatting", disabled=choice is None):
        st.session_state.profile[q["key"]] = choice
        if i < len(QUESTIONS) - 1:
            st.session_state.q_index += 1
        else:
            lang = st.session_state.profile.get("language", "English")
            st.session_state.messages = [{"role": "assistant", "content": GREETING[lang]}]
            st.session_state.stage = "chat"
        st.rerun()


def chat():
    profile = st.session_state.profile

    with st.sidebar:
        st.subheader("Your profile")
        st.write(f"**Age:** {profile['age_group']}")
        st.write(f"**Language:** {profile['language']}")
        st.write(f"**Focus:** {profile['interest']}")
        if st.button("Redo the 5 questions"):
            for k in ("stage", "q_index", "profile", "messages"):
                st.session_state.pop(k, None)
            st.rerun()
        st.divider()
        st.caption("HealthBuddy is for learning only and is not a doctor. In an emergency call 999 / 112.")

    st.title("🩺 HealthBuddy")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # quick-start buttons (only before the user has sent anything)
    if len(st.session_state.messages) == 1:
        cols = st.columns(2)
        for n, (label, text) in enumerate(QUICK_STARTS.items()):
            if cols[n % 2].button(label, use_container_width=True):
                st.session_state.pending = text
                st.rerun()

    prompt = st.chat_input("Ask me anything about health...") or st.session_state.pop("pending", None)

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            reply = st.write_stream(stream_reply(profile, st.session_state.messages))
        st.session_state.messages.append({"role": "assistant", "content": reply})


init_state()
if st.session_state.stage == "onboarding":
    onboarding()
else:
    chat()
