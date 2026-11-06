import base64

import streamlit as st
from ai_engine import QUESTIONS, stream_reply, transcribe_audio

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide")

GREETINGS = {
    "English": "Hi, welcome to AiJaga! I'm Dr. Aijaga. Ask me a health question by typing, adding a photo, or recording a voice note.",
    "Bahasa Melayu": "Hai, selamat datang ke AiJaga! Saya Dr. Aijaga. Tanya soalan kesihatan dengan menaip, menambah gambar atau merakam nota suara.",
    "Mix of both (Manglish)": "Hi, welcome to AiJaga! Saya Dr. Aijaga. Ask me a health question by typing, adding a photo, atau record voice note.",
}

QUICK_QUESTIONS = [
    "Why do I get headaches?",
    "How to lower blood pressure?",
    "First aid for burns",
    "Tips for better sleep",
]

QUIZ_QUESTIONS = [
    {
        "question": "How long should you scrub your hands with soap when washing them?",
        "options": ["About 5 seconds", "At least 20 seconds", "Exactly 2 minutes"],
        "answer": 1,
        "explanation": "Scrub with soap for at least 20 seconds, including the backs of your hands and between your fingers.",
    },
    {
        "question": "What should you do first for a small burn?",
        "options": ["Cool it under cool running water", "Put ice directly on it", "Cover it with butter"],
        "answer": 0,
        "explanation": "Cool the burn under cool running water for 20 minutes. Tell an adult and get medical help for a serious burn.",
    },
    {
        "question": "How much sleep do most teenagers need each night?",
        "options": ["5–6 hours", "8–10 hours", "12–14 hours"],
        "answer": 1,
        "explanation": "Most teenagers need 8–10 hours of sleep each night to support their health and learning.",
    },
    {
        "question": "For a balanced plate, what should fill about half the plate?",
        "options": ["Fruit and vegetables", "Rice and bread", "Meat and fish"],
        "answer": 0,
        "explanation": "A balanced plate includes plenty of fruit and vegetables, alongside grains and protein.",
    },
    {
        "question": "Which can be a sign that you need more fluids?",
        "options": ["Dark urine and feeling thirsty", "Clear vision", "Feeling hungry after a meal"],
        "answer": 0,
        "explanation": "Thirst and darker urine can be signs to drink water. If someone feels very unwell, tell an adult.",
    },
]

VIDEO_LESSONS = [
    {
        "title": "Washing your hands the right way",
        "category": "HYGIENE",
        "icon": "✋",
        "description": "Learn simple steps that wash away germs and help stop infections from spreading.",
        "scenes": [
            ("Wet and soap", "Wet your hands with clean water, then use soap. Soap helps lift dirt and germs from your skin."),
            ("Scrub every part", "Scrub for at least 20 seconds. Clean your palms, backs of hands, between fingers, thumbs, and under nails."),
            ("Rinse and dry", "Rinse under clean running water and dry with a clean towel. Wash before eating and after using the toilet."),
        ],
    },
    {
        "title": "First aid for burns",
        "category": "FIRST AID",
        "icon": "♨",
        "description": "Learn the first safe response to a burn and when to get adult or medical help.",
        "scenes": [
            ("Make the area safe", "Move away from the heat source if it is safe. Ask a nearby adult for help."),
            ("Cool the burn", "Hold the burn under cool running water for 20 minutes. Do not use ice, butter, or creams."),
            ("Get help", "Do not pull away clothing stuck to the burn. Cover loosely with a clean dressing and get medical help for a serious burn."),
        ],
    },
    {
        "title": "CPR basics",
        "category": "FIRST AID",
        "icon": "♥",
        "description": "Know how to get emergency help and how an AED can support a person in cardiac arrest.",
        "scenes": [
            ("Check and call", "If someone is unresponsive, get an adult and call 999. Ask someone to bring an AED if one is nearby."),
            ("Follow guidance", "If you are trained, start CPR. If not, follow the emergency call handler's instructions and ask an adult to help."),
            ("Use an AED", "Turn on the AED and follow its voice prompts. Do not touch the person while the AED is checking or advising a shock."),
        ],
    },
    {
        "title": "Building a healthy plate",
        "category": "NUTRITION",
        "icon": "🥗",
        "description": "A simple way to think about balanced meals, inspired by Malaysia's Suku Suku Separuh plate.",
        "scenes": [
            ("Fill half with plants", "Aim for about half your plate to be vegetables and fruit, with a variety of colours when available."),
            ("Add grains and protein", "Use the other half for grains or staple foods and protein such as beans, eggs, fish, or chicken."),
            ("Keep it flexible", "Choose foods that fit your culture, budget, and needs. Water is a good everyday drink."),
        ],
    },
    {
        "title": "Better sleep habits",
        "category": "WELLBEING",
        "icon": "☾",
        "description": "Small routines can make it easier for teenagers to get the rest they need.",
        "scenes": [
            ("Keep a steady schedule", "Try to go to bed and wake up at similar times each day, including weekends."),
            ("Wind down", "Make the last part of the evening calmer. Dim bright lights and put screens away before bed if you can."),
            ("Give yourself enough time", "Most teenagers need 8 to 10 hours of sleep. Tell a trusted adult if sleep problems keep affecting your day."),
        ],
    },
    {
        "title": "Spotting dehydration",
        "category": "EVERYDAY HEALTH",
        "icon": "💧",
        "description": "Notice common signs that it may be time to drink water and ask for help if someone is very unwell.",
        "scenes": [
            ("Notice thirst", "Feeling thirsty or having a dry mouth can be a reminder to drink, especially after activity or in hot weather."),
            ("Check how you feel", "Darker urine than usual can be a sign to drink more. Rest somewhere cool if you feel unwell in the heat."),
            ("Get help for severe symptoms", "Tell an adult if someone is very dizzy, confused, unusually sleepy, or getting worse. Seek urgent medical help for severe symptoms."),
        ],
    },
]

PROFILE_DEFAULTS = {
    "age_group": "14-15",
    "language": "English",
    "interest": "Everything / not sure yet",
    "knowledge": "Just starting",
    "considerations": "Nothing special",
}

PALETTES = {
    "Bright": {
        "page": "#f2d4a3",
        "screen": "#e9f1ed",
        "panel": "#ffffff",
        "text": "#1c3035",
        "muted": "#597079",
        "line": "#1c3035",
        "accent": "#17685e",
        "accent_text": "#ffffff",
        "soft": "#d8ece8",
        "coral": "#f07b57",
        "frame": "#d7ad72",
    },
    "Dark": {
        "page": "#192c2c",
        "screen": "#203535",
        "panel": "#294242",
        "text": "#eef4ef",
        "muted": "#bdd0cb",
        "line": "#b3c9c4",
        "accent": "#69b6a4",
        "accent_text": "#102b28",
        "soft": "#355653",
        "coral": "#f58b68",
        "frame": "#c99e63",
    },
}


def init_state():
    st.session_state.setdefault("mode", "home")
    st.session_state.setdefault("quiz_index", 0)
    st.session_state.setdefault("quiz_score", 0)
    st.session_state.setdefault("quiz_answered", None)
    st.session_state.setdefault("video_index", 0)
    st.session_state.setdefault("video_scene", 0)
    st.session_state.setdefault("watched_videos", [])
    st.session_state.setdefault("profile", dict(PROFILE_DEFAULTS))
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("theme", "Bright")
    st.session_state.setdefault("font_scale", 1.0)
    st.session_state.setdefault("read_aloud", False)
    if not st.session_state.messages:
        language = st.session_state.profile.get("language", "English")
        st.session_state.messages = [{"role": "assistant", "content": GREETINGS[language]}]


def apply_styles():
    colors = PALETTES[st.session_state.theme]
    variables = "".join(f"--{name}:{value};" for name, value in colors.items())
    st.markdown(f"<style>:root{{{variables}--text-scale:{st.session_state.font_scale};}}</style>", unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] { background: var(--page); color: var(--text); }
        [data-testid="stHeader"] { background: transparent; }
        .stMainBlockContainer { max-width: 1500px; padding-top: 1.2rem; padding-bottom: 2rem; }
        .st-key-tv_shell {
            background: var(--screen); border: 8px solid var(--frame); border-radius: 26px;
            padding: 1.1rem 1.25rem 1.35rem; box-shadow: 0 8px 0 rgba(68, 51, 30, .12);
        }
        .st-key-chat_panel { background: var(--panel); border: 3px solid var(--line); padding: 1rem; }
        .brand-title, .section-title, .eyebrow {
            color: var(--text); font-family: "Courier New", monospace; font-weight: 900;
        }
        .brand-title { font-size: 1.6rem; margin: 0; }
        .eyebrow { font-size: .75rem; text-transform: uppercase; }
        .assistant-card, .access-card { background: var(--panel); border: 3px solid var(--line); padding: 1rem; margin-bottom: 1rem; color: var(--text); }
        .assistant-card { text-align: center; }
        .doctor-avatar { font-size: 4.2rem; line-height: 1.2; }
        .doctor-label { display: inline-block; background: var(--coral); border: 2px solid var(--line); padding: .35rem .7rem; font-family: "Courier New", monospace; font-weight: 900; }
        .home-title, .mode-page-title { text-align: center; color: var(--text); font-family: "Courier New", monospace; font-weight: 900; }
        .home-title { font-size: 2rem; margin: 1.2rem 0 .4rem; }
        .mode-page-title { font-size: 1.6rem; margin: 1.2rem 0; }
        .mode-heading { text-align: center; color: var(--muted); font: 900 1rem "Courier New", monospace; margin: .5rem 0 1.5rem; }
        .mode-icon { color: var(--coral); text-align: center; font: 900 3.2rem "Courier New", monospace; padding: .7rem; }
        .mode-title { color: var(--accent); text-align: center; font: 900 1.25rem "Courier New", monospace; margin: .4rem 0; }
        .quiz-card { background: var(--panel); border: 3px solid var(--line); color: var(--text); padding: 1.2rem; margin: 1rem auto; max-width: 900px; }
        .quiz-card h2 { color: var(--text); font-size: 1.35rem; }
        .quiz-score { color: var(--accent); text-align: center; }
        .lesson-player { min-height: 300px; background: #1c3035; border: 3px solid var(--line); color: #eef4ef; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 2rem; }
        .lesson-player .lesson-icon { font-size: 4rem; }
        .lesson-player h2 { color: #eef4ef; }
        .lesson-player p { color: #d3e2dd; max-width: 650px; }
        .lesson-heading { color: var(--text); font: 900 1.1rem "Courier New", monospace; }
        .tv-footer { color: var(--muted); text-align: center; font: 900 .9rem "Courier New", monospace; letter-spacing: .18rem; padding: .5rem 0; }
        .status-online { color: var(--muted); font-size: .75rem; font-weight: 700; }
        .status-online::before { content: ""; display: inline-block; width: .55rem; height: .55rem; margin-right: .4rem; background: #35b86b; }
        .quick-label { color: var(--muted); font-family: "Courier New", monospace; font-size: .72rem; font-weight: 700; }
        [data-testid="stChatMessage"] { background: transparent; }
        [data-testid="stChatMessageContent"] { font-size: calc(1rem * var(--text-scale)); color: var(--text); }
        [data-testid="stChatMessageContent"] p { color: var(--text); }
        button[data-testid="stBaseButton-secondary"] {
            border: 2px solid var(--line) !important; border-radius: 2px !important;
            color: var(--text) !important; background: var(--soft) !important; font-weight: 700;
        }
        button[data-testid="stBaseButton-primary"] {
            border: 2px solid var(--line) !important; border-radius: 2px !important;
            color: var(--accent_text) !important; background: var(--accent) !important;
        }
        [data-testid="stChatInput"] { border: 2px solid var(--line); background: var(--panel) !important; }
        [data-testid="stChatInput"] [data-baseweb="textarea"] { background: var(--panel) !important; }
        [data-testid="stChatInput"] textarea { color: var(--text) !important; background: transparent !important; }
        [data-testid="stChatInput"] button { color: var(--text) !important; background: var(--soft) !important; }
        [role="progressbar"] [data-testid="stProgressBarTrack"] { background: var(--panel) !important; }
        [role="progressbar"] [data-testid="stProgressBarTrack"] > div { background: var(--coral) !important; }
        [data-testid="stCaptionContainer"] p, .stMarkdown p { color: var(--muted); }
        @media (max-width: 700px) {
            .st-key-tv_shell { border-width: 5px; border-radius: 16px; padding: .65rem; }
            .stMainBlockContainer { padding-left: .5rem; padding-right: .5rem; }
            .brand-title { font-size: 1.2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def listen_button(text: str, auto_play: bool, key: int, label: str = "🔊 Listen"):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    autoplay = "true" if auto_play else "false"
    st.iframe(
        f"""
        <button id="listen-{key}" data-text="{encoded}" style="border:2px solid #597079;background:#d8ece8;padding:8px 14px;font-weight:700;cursor:pointer;">
            {label}
        </button>
        <script>
        const button = document.getElementById("listen-{key}");
        const speak = () => {{
            const bytes = Uint8Array.from(atob(button.dataset.text), character => character.charCodeAt(0));
            const utterance = new SpeechSynthesisUtterance(new TextDecoder().decode(bytes));
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }};
        button.addEventListener("click", speak);
        if ({autoplay} && "speechSynthesis" in window) speak();
        </script>
        """,
        height=42,
        alt="Listen to this response",
    )


def render_message(message: dict, index: int, latest_assistant: bool):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("image"):
            st.image(message["image"]["data"], width=260)
        if message["role"] == "assistant":
            listen_button(message["content"], st.session_state.read_aloud and latest_assistant, index)


def update_profile():
    profile = st.session_state.profile
    st.markdown(
        """
        <div class="assistant-card">
            <div class="doctor-avatar">🧑🏻‍⚕️</div>
            <div class="doctor-label">DR. AIJAGA</div>
            <p>Your friendly medical assistant.<br>Ask about health, first aid, food, or exercise.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Personalize your assistant"):
        for question in QUESTIONS:
            current = profile.get(question["key"], question["options"][0])
            selected = st.selectbox(
                question["question"],
                question["options"],
                index=question["options"].index(current),
                key=f"profile_{question['key']}",
            )
            profile[question["key"]] = selected
        if not any(message["role"] == "user" for message in st.session_state.messages):
            st.session_state.messages[0]["content"] = GREETINGS[profile["language"]]

    st.markdown('<div class="access-card"><div class="eyebrow">Accessibility</div></div>', unsafe_allow_html=True)
    font_scales = [0.9, 1.0, 1.15]
    scale_index = min(range(len(font_scales)), key=lambda index: abs(font_scales[index] - st.session_state.font_scale))
    st.write(f"Text size: {['Small', 'Normal', 'Large'][scale_index]}")
    smaller, larger = st.columns(2)
    if smaller.button("A−", use_container_width=True, help="Decrease text size"):
        st.session_state.font_scale = font_scales[max(0, scale_index - 1)]
        st.rerun()
    if larger.button("A+", use_container_width=True, help="Increase text size"):
        st.session_state.font_scale = font_scales[min(len(font_scales) - 1, scale_index + 1)]
        st.rerun()
    st.checkbox("Read replies aloud", key="read_aloud")
    st.caption("Press Enter to send. Use Tab to move between controls.")


def render_topbar(progress_label: str, progress_value: float, show_home: bool = False):
    if show_home:
        home, brand, progress, bright, dark = st.columns(
            [0.65, 1.0, 1.6, 0.55, 0.55], vertical_alignment="center"
        )
        if home.button("◂ HOME", use_container_width=True):
            st.session_state.mode = "home"
            st.rerun()
    else:
        brand, progress, bright, dark = st.columns(
            [1.1, 1.6, 0.55, 0.55], vertical_alignment="center"
        )

    with brand:
        st.markdown('<div class="brand-title">🩺 AIJAGA</div>', unsafe_allow_html=True)
    with progress:
        st.markdown(f'<div class="eyebrow">{progress_label}</div>', unsafe_allow_html=True)
        st.progress(max(0.0, min(progress_value, 1.0)))
    if bright.button("BRIGHT", use_container_width=True, type="primary" if st.session_state.theme == "Bright" else "secondary"):
        st.session_state.theme = "Bright"
        st.rerun()
    if dark.button("DARK", use_container_width=True, type="primary" if st.session_state.theme == "Dark" else "secondary"):
        st.session_state.theme = "Dark"
        st.rerun()


def home_screen():
    with st.container(key="tv_shell"):
        render_topbar("LEVEL 1 · HEALTH HERO", 0.3)

        doctor, welcome = st.columns([0.36, 0.64], gap="large", vertical_alignment="center")
        with doctor:
            st.markdown(
                """
                <div class="assistant-card">
                    <div class="doctor-avatar">🧑🏻‍⚕️</div>
                    <div class="doctor-label">DR. AIJAGA</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with welcome:
            st.markdown('<div class="section-title">DR. AIJAGA</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="access-card">I am Dr. AiJaga, ready to help you! Pick a mode below to press start.</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<h1 class="home-title">HI, WELCOME TO AIJAGA</h1>', unsafe_allow_html=True)
        st.markdown('<div class="mode-heading">CHOOSE YOUR MODE...</div>', unsafe_allow_html=True)
        modes = [
            ("chat", "▣", "CHAT-BOX", "Ask Dr. AiJaga anything by text, photo or voice"),
            ("quiz", "?", "QUIZ", "Test your health knowledge and level up"),
            ("video", "▶", "VIDEO", "Watch short health and first-aid lessons"),
        ]
        columns = st.columns(3, gap="medium")
        for column, (mode, icon, title, description) in zip(columns, modes):
            with column:
                with st.container(border=True):
                    st.markdown(f'<div class="mode-icon">{icon}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="mode-title">{title}</div>', unsafe_allow_html=True)
                    st.caption(description)
                    if st.button("PRESS START", key=f"start_{mode}", use_container_width=True):
                        st.session_state.mode = mode
                        if mode == "quiz":
                            st.session_state.quiz_index = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_answered = None
                        if mode == "video":
                            st.session_state.video_index = 0
                            st.session_state.video_scene = 0
                        st.rerun()

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def quiz_screen():
    question_index = st.session_state.quiz_index
    score = st.session_state.quiz_score
    with st.container(key="tv_shell"):
        render_topbar(
            f"SCORE {score} / {len(QUIZ_QUESTIONS)} · QUESTION {min(question_index + 1, len(QUIZ_QUESTIONS))} OF {len(QUIZ_QUESTIONS)}",
            question_index / len(QUIZ_QUESTIONS),
            show_home=True,
        )
        st.markdown('<h1 class="mode-page-title">[ ? ] HEALTH QUIZ</h1>', unsafe_allow_html=True)

        if question_index >= len(QUIZ_QUESTIONS):
            st.markdown('<div class="quiz-card">QUIZ COMPLETE</div>', unsafe_allow_html=True)
            st.markdown(f'<h2 class="quiz-score">Your score: {score} / {len(QUIZ_QUESTIONS)}</h2>', unsafe_allow_html=True)
            st.write("Every question is a chance to learn something useful. You can play again whenever you like.")
            replay, home = st.columns(2)
            if replay.button("PLAY AGAIN", use_container_width=True):
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_answered = None
                st.rerun()
            if home.button("HOME", use_container_width=True):
                st.session_state.mode = "home"
                st.rerun()
        else:
            question = QUIZ_QUESTIONS[question_index]
            st.markdown(
                f'<div class="quiz-card"><div class="doctor-label">QUESTION {question_index + 1} OF {len(QUIZ_QUESTIONS)}</div>'
                f'<h2>{question["question"]}</h2></div>',
                unsafe_allow_html=True,
            )
            answered = st.session_state.quiz_answered
            locked = answered is not None and answered["index"] == question_index
            selected = st.radio(
                "Choose one answer",
                question["options"],
                index=answered["selected"] if locked else None,
                key=f"quiz_answer_{question_index}",
                label_visibility="collapsed",
                disabled=locked,
            )
            if not locked and st.button("CHECK ANSWER", disabled=selected is None, type="primary"):
                selected_index = question["options"].index(selected)
                correct = selected_index == question["answer"]
                st.session_state.quiz_answered = {
                    "index": question_index,
                    "selected": selected_index,
                    "correct": correct,
                }
                if correct:
                    st.session_state.quiz_score += 1
                st.rerun()

            if locked:
                if answered["correct"]:
                    st.success("Correct! " + question["explanation"])
                else:
                    st.info("Good try. " + question["explanation"])
                if st.button("SEE RESULTS" if question_index == len(QUIZ_QUESTIONS) - 1 else "NEXT QUESTION", type="primary"):
                    st.session_state.quiz_index += 1
                    st.session_state.quiz_answered = None
                    st.rerun()

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def video_screen():
    lesson_index = st.session_state.video_index
    lesson = VIDEO_LESSONS[lesson_index]
    scene_index = st.session_state.video_scene
    scene_title, scene_text = lesson["scenes"][scene_index]
    watched = st.session_state.watched_videos

    with st.container(key="tv_shell"):
        render_topbar(f"WATCHED {len(watched)} OF {len(VIDEO_LESSONS)} VIDEOS", len(watched) / len(VIDEO_LESSONS), show_home=True)
        player, playlist = st.columns([0.72, 0.28], gap="medium")
        with player:
            st.markdown('<div class="lesson-heading">NOW PLAYING</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="lesson-player"><div class="lesson-icon">{lesson["icon"]}</div>'
                f'<div class="eyebrow">SCENE {scene_index + 1} OF {len(lesson["scenes"])}</div>'
                f'<h2>{scene_title}</h2><p>{scene_text}</p></div>',
                unsafe_allow_html=True,
            )
            listen_button(
                f"{lesson['title']}. {scene_title}. {scene_text}",
                False,
                100 + lesson_index * 10 + scene_index,
                label="▶ PLAY SCENE",
            )
            st.markdown(f"### {lesson['title']}")
            st.write(lesson["description"])

            previous, next_scene, complete = st.columns([0.9, 0.9, 1.3])
            if previous.button("◂ PREV", disabled=scene_index == 0, use_container_width=True):
                st.session_state.video_scene -= 1
                st.rerun()
            if next_scene.button("NEXT ▸", disabled=scene_index == len(lesson["scenes"]) - 1, use_container_width=True):
                st.session_state.video_scene += 1
                st.rerun()
            is_watched = lesson_index in watched
            can_complete = scene_index == len(lesson["scenes"]) - 1
            if complete.button(
                "✓ WATCHED" if is_watched else "MARK WATCHED",
                disabled=is_watched or not can_complete,
                use_container_width=True,
            ):
                st.session_state.watched_videos.append(lesson_index)
                st.rerun()

            if st.button("TAKE THE QUIZ", type="primary"):
                st.session_state.mode = "quiz"
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_answered = None
                st.rerun()

        with playlist:
            st.markdown('<div class="lesson-heading">PLAYLIST</div>', unsafe_allow_html=True)
            for index, item in enumerate(VIDEO_LESSONS):
                status = "✓" if index in watched else f"{index + 1:02}"
                if st.button(
                    f"{status}  {item['title']}\n{item['category']}",
                    key=f"lesson_{index}",
                    use_container_width=True,
                    type="primary" if index == lesson_index else "secondary",
                ):
                    st.session_state.video_index = index
                    st.session_state.video_scene = 0
                    st.rerun()

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")
        st.markdown('<div class="tv-footer">AIJAGA TV</div>', unsafe_allow_html=True)


def chat():
    with st.container(key="tv_shell"):
        turns = sum(message["role"] == "user" for message in st.session_state.messages)
        render_topbar(f"LEVEL {turns // 5 + 1} · HEALTH HERO", (turns % 5) / 5, show_home=True)

        left, right = st.columns([0.32, 0.68], gap="medium")
        with left:
            update_profile()
            st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999 / 112.")

        with right:
            with st.container(key="chat_panel"):
                title, status = st.columns([0.75, 0.25], vertical_alignment="center")
                title.markdown('<div class="section-title">HI, WELCOME TO AIJAGA</div>', unsafe_allow_html=True)
                status.markdown('<div class="status-online">DR. AIJAGA IS ONLINE</div>', unsafe_allow_html=True)
                st.divider()

                with st.container(height=420, border=False):
                    messages = st.session_state.messages
                    for index, message in enumerate(messages):
                        render_message(
                            message,
                            index,
                            index == len(messages) - 1 and message["role"] == "assistant",
                        )
                    live_turn = st.empty()

                st.markdown('<div class="quick-label">QUICK QUESTIONS · SWIPE OR SCROLL SIDEWAYS →</div>', unsafe_allow_html=True)
                quick_cols = st.columns(4)
                quick_prompt = None
                for index, question in enumerate(QUICK_QUESTIONS):
                    if quick_cols[index].button(question, key=f"quick_{index}", use_container_width=True):
                        quick_prompt = question

                entry = st.chat_input(
                    "Type your healthcare question here...",
                    accept_file=True,
                    file_type=["png", "jpg", "jpeg", "webp"],
                    accept_audio=True,
                    max_upload_size=10,
                )

                prompt = quick_prompt
                image = None
                image_for_display = None
                if entry is not None:
                    prompt = entry.text.strip()
                    if entry.audio is not None:
                        try:
                            transcript = transcribe_audio(entry.audio.getvalue(), entry.audio.type or "audio/wav")
                            prompt = f"{prompt}\n{transcript}".strip()
                        except Exception:
                            st.error("I couldn't transcribe that voice note. Please try recording it again or type your question.")
                            prompt = None
                    if entry.files:
                        upload = entry.files[0]
                        image = (upload.getvalue(), upload.type or "image/jpeg")
                        image_for_display = {"data": image[0], "mime_type": image[1]}
                        if not prompt:
                            prompt = "Please describe this image and share general health information. Do not diagnose."

                if prompt:
                    user_message = {"role": "user", "content": prompt}
                    if image_for_display:
                        user_message["image"] = image_for_display
                    st.session_state.messages.append(user_message)
                    with live_turn.container():
                        render_message(user_message, len(st.session_state.messages) - 1, False)
                        with st.chat_message("assistant"):
                            reply = st.write_stream(
                                stream_reply(st.session_state.profile, st.session_state.messages, image=image)
                            )
                            listen_button(reply, st.session_state.read_aloud, len(st.session_state.messages))
                    st.session_state.messages.append({"role": "assistant", "content": reply})


init_state()
apply_styles()
if st.session_state.mode == "home":
    home_screen()
elif st.session_state.mode == "chat":
    chat()
elif st.session_state.mode == "quiz":
    quiz_screen()
elif st.session_state.mode == "video":
    video_screen()
