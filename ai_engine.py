"""
ai_engine.py  -  the AI part (your job).
Your teammate's login/design code only needs to call:
    QUESTIONS, build_system_prompt(profile), stream_reply(profile, messages)
"""
import time

import streamlit as st
from google import genai
from google.genai import types

# Change the model name here if Google releases a newer Flash model.
# Models are tried in order. If the first is busy (503), the app moves to the next.
# Run list_models.py to see which names your key can use, then add backups here.
MODELS = ["gemini-3.8-flash"]

# Backup provider (free). Used only if every Gemini model fails.
# Check console.groq.com for current model names if this one stops working.
GROQ_MODEL = "openai/gpt-oss-120b"

# Which provider to try FIRST for every message. Change to "gemini" to swap back.
PRIMARY_PROVIDER = "groq"  # "groq" or "gemini"

# ---------------------------------------------------------------------------
# 1) The 5 onboarding questions (all select-type)
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "key": "age_group",
        "question": "How old are you?",
        "options": ["12-13", "14-15", "16-17", "18 or older"],
    },
    {
        "key": "language",
        "question": "Which language do you prefer?",
        "options": ["English", "Bahasa Melayu", "Mix of both (Manglish)"],
    },
    {
        "key": "interest",
        "question": "What do you want help with the most?",
        "options": [
            "First aid practice",
            "Healthy eating",
            "Mental health & stress",
            "Exercise & fitness",
            "Everything / not sure yet",
        ],
    },
    {
        "key": "knowledge",
        "question": "How much do you already know about health?",
        "options": ["Just starting", "I know the basics", "I know quite a lot"],
    },
    {
        "key": "considerations",
        "question": "Is there anything I should keep in mind?",
        "options": [
            "Nothing special",
            "Food allergy or dietary restriction",
            "An injury or physical limitation",
            "I prefer gentle topics (I get stressed easily)",
        ],
    },
]

# ---------------------------------------------------------------------------
# 2) How the AI adjusts to age
# ---------------------------------------------------------------------------
AGE_STYLE = {
    "12-13": "Use very simple words, short sentences, friendly examples (school, sports day, canteen). Max ~120 words per reply.",
    "14-15": "Use simple clear language with a bit of science. Friendly and relatable. Max ~180 words per reply.",
    "16-17": "Use clear language and introduce correct terms (explain them briefly). Max ~250 words per reply.",
    "18 or older": "Use an adult but easy tone with more detail and reasoning. Max ~300 words per reply.",
}

LANG_STYLE = {
    "English": "Reply in English.",
    "Bahasa Melayu": "Balas dalam Bahasa Melayu yang mudah difahami.",
    "Mix of both (Manglish)": "Reply in a casual mix of English and Bahasa Melayu, like Malaysian students talk, but keep medical terms clear.",
}


def build_system_prompt(profile: dict) -> str:
    age = profile.get("age_group", "14-15")
    lang = profile.get("language", "English")
    return f"""
You are "AiJaga", a friendly health education chatbot for Malaysian secondary school students.
You help with 4 areas: (1) first aid simulator, (2) healthy eating, (3) mental health, (4) exercise.

USER PROFILE (from the intro questions):
- Age group: {age}
- Main interest: {profile.get("interest")}
- Knowledge level: {profile.get("knowledge")}
- Keep in mind: {profile.get("considerations")}

STYLE:
- {AGE_STYLE.get(age, AGE_STYLE["14-15"])}
- {LANG_STYLE.get(lang, LANG_STYLE["English"])}
- Adjust depth to the knowledge level. Be warm, encouraging, never judgmental. Use short paragraphs, light emoji is OK.
- If the user's "keep in mind" is a food allergy/restriction or injury, respect it in every food/exercise suggestion and ask for details if needed.
- If they prefer gentle topics, avoid graphic injury descriptions and be extra calm.

FIRST AID SIMULATOR MODE (when the user asks to practise first aid: broken bones, wounds/bleeding,
epilepsy/seizure, choking, CPR, AED, burns, nosebleed, fainting, etc.):
- Run it as an interactive scenario. Describe a short realistic situation (e.g. a friend collapses in the school field).
- Give ONE step at a time. Ask "What do you do first?" and wait for the user's answer.
- After each answer: say if it is correct, explain why briefly, then continue to the next step.
- Keep a score out of 5 steps and give a short summary at the end with the key take-aways.
- Always include the reminder to call 999 (or 112 from a mobile phone) for real emergencies, and to get a teacher/adult.
- Teach standard guidance only (e.g. CPR: call for help, push hard and fast in the centre of the chest; AED: turn on and follow the voice prompts).
- Make it clear this is practice, and real first aid training (St John Ambulance / Red Crescent) is recommended.

SAFETY RULES (very important):
- You are NOT a doctor. Do not diagnose. For symptoms or real injuries, give general safe advice and tell the user to see a doctor/clinic/adult.
- If the user describes a REAL emergency happening now (not breathing, severe bleeding, seizure, choking, chest pain, poisoning, etc.),
  tell them first: call 999 / 112 now and get an adult nearby, then give brief safe steps.
- Do not give medicine doses. Say to ask a pharmacist or doctor.
- Mental health: be supportive and listen. Do not diagnose. Suggest talking to a trusted adult, parent, teacher or school counsellor.
  If the user mentions self-harm, suicide, abuse or feeling unsafe: respond with care, do not give any method details, encourage them to
  reach out to a trusted adult immediately, and share Malaysian helplines: Talian Kasih 15999, Befrienders KL 03-7627 2929,
  or 999 if in immediate danger.
- Diet: promote balanced eating (e.g. Suku Suku Separuh plate idea). Never recommend extreme diets, fasting for weight loss, or calorie targets for under-18s.
  If the user shows signs of an eating disorder, do not give numbers or diet plans; gently encourage talking to a trusted adult or doctor.
- Exercise: suggest safe, beginner-friendly routines with warm-up and cool-down; tell them to stop if there is pain, dizziness or breathlessness.
- Stay on health topics. If asked something unrelated, politely steer back. Never produce sexual, violent or otherwise inappropriate content.
- If unsure, say so honestly and suggest asking a health professional.
""".strip()


# ---------------------------------------------------------------------------
# 3) Gemini call (streaming)
# ---------------------------------------------------------------------------
@st.cache_resource
def _get_client() -> genai.Client:
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def _stream_groq(profile: dict, messages: list, max_history: int = 20):
    from groq import Groq  # imported here so the app still runs if groq is not installed

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    msgs = [{"role": "system", "content": build_system_prompt(profile)}]
    for m in messages[-max_history:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    stream = client.chat.completions.create(
        model=GROQ_MODEL, messages=msgs, temperature=0.6, stream=True
    )
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield text


def _call_gemini(model, contents, config):
    """One Gemini attempt. Raises on failure; yields text chunks on success."""
    for chunk in _get_client().models.generate_content_stream(
        model=model, contents=contents, config=config
    ):
        if chunk.text:
            yield chunk.text


def transcribe_audio(audio_data: bytes, mime_type: str) -> str:
    """Transcribe a short voice note with Gemini."""
    response = _get_client().models.generate_content(
        model=MODELS[0],
        contents=[
            types.Part.from_bytes(data=audio_data, mime_type=mime_type),
            "Transcribe this voice note accurately. Return only the spoken words.",
        ],
    )
    return (response.text or "").strip()


def stream_reply(profile: dict, messages: list, max_history: int = 20, image=None):
    """Yield text chunks. `messages` = [{"role": "user"|"assistant", "content": str}, ...]
    Tries PRIMARY_PROVIDER first; if every one of its models fails before any
    text comes back, falls through to the other provider automatically."""
    contents = []
    recent_messages = messages[-max_history:]
    for index, m in enumerate(recent_messages):
        role = "user" if m["role"] == "user" else "model"
        parts = [types.Part(text=m["content"])]
        if image and index == len(recent_messages) - 1 and role == "user":
            image_data, mime_type = image
            parts.append(types.Part.from_bytes(data=image_data, mime_type=mime_type))
        contents.append(types.Content(role=role, parts=parts))

    config = types.GenerateContentConfig(
        system_instruction=build_system_prompt(profile),
        temperature=0.6,
    )

    gemini_attempts = [("gemini", model) for model in MODELS]
    groq_attempts = [("groq", GROQ_MODEL)]
    if image:
        attempts = gemini_attempts
    else:
        attempts = (
            groq_attempts + gemini_attempts
            if PRIMARY_PROVIDER == "groq"
            else gemini_attempts + groq_attempts
        )

    got_text = False
    last_error = None
    for provider, model in attempts:
        retries = 2 if provider == "gemini" else 1  # only Gemini gets a same-model retry
        for attempt in range(retries):
            try:
                if provider == "gemini":
                    source = _call_gemini(model, contents, config)
                else:
                    if "GROQ_API_KEY" not in st.secrets:
                        raise RuntimeError("GROQ_API_KEY is not set in secrets.toml")
                    source = _stream_groq(profile, messages, max_history)

                for chunk in source:
                    got_text = True
                    yield chunk
                if got_text:
                    return
                break  # empty answer: try the next provider/model
            except Exception as e:
                last_error = e
                print(f"{provider.upper()} ERROR ({model}):", repr(e))  # shows in the VS Code terminal
                if got_text:  # failed in the middle of an answer
                    yield "\n\n⚠️ The answer was cut off. Please ask again."
                    return
                if provider == "gemini" and any(c in str(e) for c in ("503", "429", "UNAVAILABLE")) and attempt == 0:
                    time.sleep(3)
                    continue
                break  # try the next provider/model

    if last_error:
        yield f"⚠️ Sorry, I couldn't reach the AI right now. Please try again in a minute. ({type(last_error).__name__}: {str(last_error)[:300]})"
    else:
        yield "⚠️ I didn't get an answer back. Please try asking again in different words."
