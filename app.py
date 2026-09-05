import html
import secrets
from datetime import datetime
from pathlib import Path

import streamlit as st
import database
import auth
from vela_ai import tutor_answer

st.set_page_config(page_title="Vela", page_icon="V", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
    :root { --ink:#18241f; --muted:#718078; --line:#e3e9e2; --paper:#f7f8f3; --deep:#245441; --lime:#c9f464; --bubble:#dff6e8; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:#f5f7f1; }
    [data-testid="stSidebar"] { background:#fbfcf8; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] .block-container { padding:2rem 1rem; }
    h1,h2,h3 { font-family:'Manrope',sans-serif; letter-spacing:-.05em; }
    h1 { font-size:2rem; }
    .brand { display:flex; align-items:center; gap:.6rem; margin-bottom:1.4rem; font:800 1.4rem Manrope,sans-serif; }
    .brand-mark { width:28px; height:28px; display:inline-block; border-radius:9px 9px 9px 3px; background:var(--deep); position:relative; }
    .brand-mark:after { content:''; width:9px; height:9px; background:var(--lime); border-radius:50%; position:absolute; right:5px; top:5px; }
    .hero-kicker { color:#89958d; text-transform:uppercase; letter-spacing:.1em; font-size:.7rem; font-weight:700; }
    .hero-title { margin:.3rem 0 1.2rem; font:800 2rem/1.05 Manrope,sans-serif; }
    .chat-card { padding:1rem 1.1rem; border:1px solid var(--line); border-radius:20px; background:white; }
    .chat-header { display:flex; align-items:center; gap:.7rem; padding-bottom:.8rem; border-bottom:1px solid var(--line); }
    .avatar { width:42px; height:42px; display:grid; place-items:center; border-radius:13px; color:white; font-weight:800; }
    .avatar.green { background:#559676; } .avatar.yellow { background:#d29a4f; } .avatar.rose { background:#cc7d79; } .avatar.blue { background:#668bb4; } .avatar.violet { background:#9a86b7; }
    .status-dot { width:9px; height:9px; display:inline-block; border-radius:50%; background:#77d493; margin-left:.3rem; }
    .bubble { max-width:80%; margin:.7rem 0; padding:.7rem .85rem; border-radius:6px 16px 16px 16px; background:#f0f3ed; font-size:.86rem; line-height:1.4; }
    .bubble.out { margin-left:auto; border-radius:16px 6px 16px 16px; background:var(--bubble); }
    .bubble small { display:block; margin-top:.35rem; color:#91a097; text-align:right; font-size:.65rem; }
    .feature-card { min-height:190px; padding:1.2rem; border:1px solid var(--line); border-radius:20px; background:white; }
    .feature-card p { color:#7b8980; font-size:.82rem; line-height:1.5; }
    .drop-card { padding:2rem 1rem; border:1px dashed #bdd5c2; border-radius:15px; color:#6d7e73; background:#f5faf3; text-align:center; }
    .online-card { padding:1rem 1.1rem; border:1px solid var(--line); border-radius:20px; background:white; }
    .online-row { display:flex; align-items:center; gap:.7rem; padding:.65rem 0; border-bottom:1px solid #eff2ed; }
    .online-row:last-child { border-bottom:0; }
    .online-row small { display:block; color:#89968e; margin-top:.2rem; }
    .stButton > button { border-radius:11px; border:1px solid var(--line); font-weight:600; }
    .stButton > button[kind="primary"] { background:var(--lime); color:#1d3e2d; border:0; }
    .login-card { max-width:430px; margin:8vh auto; padding:2rem; border:1px solid var(--line); border-radius:25px; background:white; box-shadow:0 25px 70px rgba(35,67,49,.12); }
    @keyframes vela-rise { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
    @keyframes vela-pulse { 0%,100% { box-shadow:0 0 0 0 rgba(119,212,147,.35); } 50% { box-shadow:0 0 0 7px rgba(119,212,147,0); } }
    @keyframes vela-blink { 0%,100% { opacity:.3; transform:scale(.8); } 50% { opacity:1; transform:scale(1); } }
    @keyframes vela-shimmer { 0% { background-position:200% 0; } 100% { background-position:-200% 0; } }
    .main .block-container { animation:vela-rise .45s ease both; }
    .hero-kicker { animation:vela-rise .35s ease both; }
    .hero-title { animation:vela-rise .45s .06s ease both; }
    .activity-strip { display:flex; align-items:center; gap:.5rem; width:max-content; max-width:100%; margin:-.65rem 0 1.1rem; padding:.38rem .65rem; border:1px solid #dce8dc; border-radius:999px; color:#718078; background:rgba(255,255,255,.7); font-size:.72rem; animation:vela-rise .5s .12s ease both; }
    .activity-pulse { width:7px; height:7px; border-radius:50%; background:#77d493; animation:vela-pulse 1.8s ease-out infinite; }
    .activity-dots { display:inline-flex; gap:3px; margin-left:.1rem; }
    .activity-dots i { width:3px; height:3px; border-radius:50%; background:#77a487; animation:vela-blink 1.1s ease-in-out infinite; }
    .activity-dots i:nth-child(2) { animation-delay:.18s; } .activity-dots i:nth-child(3) { animation-delay:.36s; }
    .chat-card, .feature-card, .online-card, .login-card { animation:vela-rise .5s ease both; }
    .stButton > button { transition:transform .2s ease, box-shadow .2s ease, background .2s ease; }
    .stButton > button:hover { transform:translateY(-2px); box-shadow:0 8px 18px rgba(36,84,65,.12); }
    .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] > div, .stFileUploader section { transition:border-color .2s ease, box-shadow .2s ease, background .2s ease; }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color:#9bcbaa; box-shadow:0 0 0 3px rgba(155,203,170,.18); }
    .stFileUploader section { border-color:#bdd5c2; background:linear-gradient(90deg,#f5faf3,#ffffff,#f5faf3); background-size:200% 100%; animation:vela-shimmer 5s linear infinite; }
    .call-card { padding:1.2rem; margin-bottom:1rem; border:1px solid #b8dcc5; border-radius:20px; color:#eef9f0; background:linear-gradient(135deg,#245441,#183d30); animation:vela-rise .4s ease both; }
    .call-card strong { font:700 1.15rem Manrope,sans-serif; }
    .call-card p { margin:.35rem 0 1rem; color:#c7dfcc; font-size:.8rem; }
    .call-live { display:inline-flex; align-items:center; gap:.4rem; color:#c9f464; font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
    .voice-message { display:flex; align-items:center; gap:.6rem; }
    .voice-icon { width:28px; height:28px; display:grid; place-items:center; border-radius:9px; color:#234a36; background:#c9f464; font-size:.8rem; }
    .compact-actions { display:flex; align-items:center; gap:.4rem; margin:.6rem 0 .25rem; }
    .compact-actions + div { margin-top:0; }
    .attachment-menu { padding:.2rem 0; }
    .attachment-menu small { color:#718078; }
    .stPopover button { min-width:42px; min-height:40px; padding:.4rem .65rem; font-size:1.1rem; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton:nth-child(1) button { color:#2d73d5; background:#eaf2ff; border-color:#c9dcff; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton:nth-child(2) button { color:#c45b37; background:#fff0e9; border-color:#ffd4c5; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton:nth-child(3) button { color:#8b5fc5; background:#f4edff; border-color:#dfceff; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton:nth-child(4) button { color:#2d9a6b; background:#e8f8ef; border-color:#c6ead5; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton button { animation:vela-icon-in .45s ease both; }
    .stPopover [data-testid="stHorizontalBlock"] .stButton button:hover { transform:translateY(-4px) rotate(-3deg); box-shadow:0 9px 16px rgba(36,84,65,.18); }
    @keyframes vela-icon-in { from { opacity:0; transform:scale(.75) rotate(8deg); } to { opacity:1; transform:scale(1) rotate(0); } }
    .stPopover [data-testid="stHorizontalBlock"]:nth-of-type(2) .stButton button { animation-delay:.06s; }
    .stPopover [data-testid="stHorizontalBlock"]:nth-of-type(3) .stButton button { animation-delay:.12s; }
    .stPopover [data-testid="stHorizontalBlock"]:nth-of-type(4) .stButton button { animation-delay:.18s; }
    .stPopover [data-testid="stHorizontalBlock"]:nth-of-type(5) .stButton button { animation-delay:.24s; }
    @media (max-width:600px) {
        .main .block-container { padding:1rem .65rem 4rem; }
        .chat-card { padding:.7rem; border-radius:15px; }
        .compact-actions { gap:.25rem; }
        .stPopover button { min-width:40px; }
        .hero-title { font-size:1.45rem; overflow-wrap:anywhere; }
        .hero-kicker { font-size:.62rem; }
        .activity-strip { width:100%; margin-bottom:.8rem; font-size:.68rem; }
        .bubble { max-width:92%; font-size:.8rem; overflow-wrap:anywhere; }
        .chat-header { gap:.5rem; }
        .chat-header strong { font-size:.88rem; overflow-wrap:anywhere; }
        .stButton > button { min-height:38px; padding:.45rem .55rem; font-size:.82rem; }
        .stFileUploader section { min-height:92px; padding:.6rem; }
        .stFileUploader section small, .stFileUploader section span { overflow-wrap:anywhere; }
        [data-testid="stHorizontalBlock"] { gap:.45rem; }
        [data-testid="stSidebar"] .block-container { padding:.9rem .65rem; }
    }
    @media (max-width:380px) {
        .main .block-container { padding-left:.45rem; padding-right:.45rem; }
        .chat-card { padding:.55rem; }
        .avatar { width:34px; height:34px; border-radius:10px; font-size:.72rem; }
        .stButton > button { font-size:.75rem; }
        .stPopover button { min-width:36px; padding:.3rem; }
    }
    [data-testid="stSidebar"] .stButton > button { transition:transform .18s ease, background .18s ease; }
    [data-testid="stSidebar"] .stButton > button:hover { transform:translateX(3px); }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; } }
    @media (max-width: 800px) {
        .hero-title { font-size:1.65rem; }
        .feature-card { min-height:auto; }
        [data-testid="stSidebar"] { width:min(86vw, 320px); }
        [data-testid="stSidebar"] .stButton > button { min-height:42px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_CHATS = [
    {"name": "Sofia Carter", "initials": "SC", "color": "green", "preview": "The little things are the big things", "status": "online now", "messages": [("in", "The little things are the big things", "10:40 AM"), ("out", "Coffee walk this afternoon?", "10:41 AM"), ("in", "Absolutely. I know the perfect spot by the park.", "10:42 AM")]},
    {"name": "The Weekend Crew", "initials": "WC", "color": "yellow", "preview": "Nora: Sent a photo", "status": "4 members online", "messages": [("in", "Nora sent a photo", "9:18 AM"), ("in", "That sunset was unreal!", "9:18 AM")]},
    {"name": "Jordan Williams", "initials": "JW", "color": "rose", "preview": "Voice message - 0:34", "status": "last seen yesterday", "messages": [("out", "I will send the details over tonight.", "Yesterday"), ("in", "Perfect, thank you!", "Yesterday")]},
    {"name": "Ari & Miles", "initials": "AM", "color": "blue", "preview": "You: See you soon", "status": "last seen Monday", "messages": [("out", "See you soon!", "Monday")]},
    {"name": "Lena Ortiz", "initials": "LO", "color": "violet", "preview": "Loved that playlist", "status": "last seen Sunday", "messages": [("in", "Loved that playlist", "Sunday")]},
]

DEFAULT_POSTS = [
    {"id": 1, "author": "Sofia Carter", "initials": "SC", "color": "green", "time": "12 minutes ago", "text": "The little things are the big things.", "media": None, "likes": 12, "liked": False, "comments": ["This made my day."]},
    {"id": 2, "author": "The Weekend Crew", "initials": "WC", "color": "yellow", "time": "1 hour ago", "text": "Sunset walks and good company.", "media": None, "likes": 24, "liked": False, "comments": []},
]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "phone" not in st.session_state:
    st.session_state.phone = ""
if "chats" not in st.session_state:
    st.session_state.chats = [dict(chat) for chat in DEFAULT_CHATS]
    for chat, default in zip(st.session_state.chats, DEFAULT_CHATS):
        chat["messages"] = list(default["messages"])
if "active_chat" not in st.session_state:
    st.session_state.active_chat = 0
if "show_online" not in st.session_state:
    st.session_state.show_online = False
if "last_attachment" not in st.session_state:
    st.session_state.last_attachment = None
if "feed_posts" not in st.session_state:
    st.session_state.feed_posts = [dict(post) for post in DEFAULT_POSTS]
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "active_call" not in st.session_state:
    st.session_state.active_call = None
if "database_ready" not in st.session_state:
    try:
        database.initialize(DEFAULT_CHATS, DEFAULT_POSTS)
        st.session_state.chats = database.load_chats()
        st.session_state.feed_posts = database.load_posts()
        st.session_state.database_ready = True
        st.session_state.database_error = None
    except Exception as error:
        st.session_state.database_ready = False
        st.session_state.database_error = str(error)
else:
    try:
        database.health_check()
        st.session_state.database_error = None
    except Exception as error:
        st.session_state.database_error = str(error)


def avatar(chat: dict) -> str:
    return f'<span class="avatar {chat["color"]}">{html.escape(chat["initials"])}</span>'


def send_message(text: str, file_name: str | None = None, file_size: int | None = None) -> None:
    if not text and not file_name:
        return
    now = datetime.now().strftime("%I:%M %p").lstrip("0")
    if file_name:
        size_text = f" ({file_size:,} bytes)" if file_size is not None else ""
        text = f"Attached file: {file_name}{size_text}"
    chat = st.session_state.chats[st.session_state.active_chat]
    chat["messages"].append(("out", text, now))
    chat["preview"] = text
    try:
        database.save_message(chat["name"], "out", text, now, preview=text)
    except Exception as error:
        st.session_state.database_error = str(error)


def database_save_voice(chat: dict, content: bytes, sent_at: str) -> None:
    try:
        database.save_message(chat["name"], "out", content, sent_at, kind="voice", preview="Voice message")
    except Exception as error:
        st.session_state.database_error = str(error)


def start_call(mode: str, chat: dict) -> None:
    st.session_state.active_call = {"mode": mode, "name": chat["name"], "initials": chat["initials"], "color": chat["color"]}


def end_call() -> None:
    st.session_state.active_call = None


def render_login() -> None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="brand"><span class="brand-mark"></span>vela</div>', unsafe_allow_html=True)
    if not st.session_state.otp_sent:
        st.markdown("## Welcome to Vela")
        login_provider = auth.provider()
        login_label = "Mobile number" if login_provider == "sms" else "Email address" if login_provider == "email" else "Mobile number or email"
        login_placeholder = "+91 98765 43210" if login_provider == "sms" else "you@example.com" if login_provider == "email" else "+91 98765 43210"
        st.write("Sign in with a verified mobile number or email address to keep your conversations, scans, and files together.")
        if login_provider == "demo":
            st.info("Free email OTP is not configured yet. Add SMTP secrets to enable email verification.")
        phone = st.text_input(login_label, value=st.session_state.phone, key="phone", placeholder=login_placeholder)
        if st.button("Send OTP", type="primary", use_container_width=True):
            if phone.strip():
                normalized_phone = phone.strip()
                if login_provider == "sms":
                    if auth.send_code(normalized_phone):
                        st.session_state.otp_sent = True
                        st.rerun()
                    error_detail = auth.last_error or "Check the phone number and Twilio Verify settings."
                    st.error(f"Could not send the verification code: {error_detail}")
                elif login_provider == "email":
                    code = f"{secrets.randbelow(1_000_000):06d}"
                    if auth.send_email_code(normalized_phone, code):
                        st.session_state.otp_code = code
                        st.session_state.otp_sent = True
                        st.rerun()
                    st.error(f"Could not send the verification code: {auth.last_error}")
                else:
                    st.session_state.otp_sent = True
                    st.rerun()
    else:
        st.markdown("## Check your messages")
        contact_label = {"sms": "mobile number", "email": "email address"}.get(auth.provider(), "contact")
        st.write(f"We sent a one-time code to your {contact_label}.")
        otp = st.text_input("6-digit OTP", max_chars=6, key="otp")
        if auth.provider() == "sms":
            st.caption("Enter the verification code sent by SMS.")
        elif auth.provider() == "email":
            st.caption("Enter the verification code sent by email.")
        else:
            st.caption("Demo OTP: 123456. Configure Twilio for real verification.")
        if st.button("Verify and open Vela", type="primary", use_container_width=True):
            if auth.provider() == "sms":
                verified = auth.verify_code(st.session_state.phone, otp)
            elif auth.provider() == "email":
                verified = secrets.compare_digest(st.session_state.get("otp_code", ""), otp)
            else:
                verified = otp == "123456"
            if verified:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("That verification code is invalid or expired.")
        if st.button("Edit number", use_container_width=True):
            st.session_state.otp_sent = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.logged_in:
    render_login()
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark"></span>vela</div>', unsafe_allow_html=True)
    st.text_input("Search conversations", key="search", label_visibility="collapsed", placeholder="Search conversations")
    st.caption("MESSAGES")
    search = st.session_state.get("search", "").lower()
    for index, chat in enumerate(st.session_state.chats):
        if search and search not in chat["name"].lower():
            continue
        label = f"{chat['name']}  |  {chat['preview'][:25]}"
        if st.button(label, key=f"chat_{index}", use_container_width=True):
            st.session_state.active_chat = index
            st.session_state.page = "Chats"
            st.rerun()
    st.divider()
    if st.button("Mark all read", use_container_width=True):
        st.toast("All conversations marked as read")
    page = st.radio("Open section", ["Chats", "Feed", "AI Tutor", "Status", "Calls", "Files", "Scan", "Settings"], label_visibility="collapsed")
    st.caption("Signed in as Maya Chen")
    if st.button("Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

st.markdown('<div class="hero-kicker">Tuesday, October 24</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero-title">{html.escape(page)}</div>', unsafe_allow_html=True)
activity = {
    "Chats": "Conversations are live",
    "Feed": "Checking in with your people",
    "AI Tutor": "Tutor workspace is ready",
    "Status": "Your circle is up to date",
    "Calls": "Call history is synced",
    "Files": "Workspace is ready",
    "Scan": "Scanner is standing by",
    "Settings": "Preferences are saved locally",
}.get(page, "Vela is ready")
st.markdown(f'<div class="activity-strip"><span class="activity-pulse"></span><span>{activity}</span><span class="activity-dots"><i></i><i></i><i></i></span></div>', unsafe_allow_html=True)
if st.session_state.get("database_error"):
    st.warning("Local database is temporarily unavailable. Changes will stay in this session until storage reconnects.")

if page == "Chats":
    chat = st.session_state.chats[st.session_state.active_chat]
    left, right = st.columns([2.2, 1], gap="large")
    with left:
        voice_call_col, video_call_col = st.columns(2)
        with voice_call_col:
            if st.button("☎", use_container_width=True, key="chat_voice_call", help="Start voice call"):
                start_call("Voice", chat)
                st.rerun()
        with video_call_col:
            if st.button("▣", use_container_width=True, key="chat_video_call", help="Start video call"):
                start_call("Video", chat)
                st.rerun()
        if st.session_state.active_call is not None:
            call = st.session_state.active_call
            st.markdown(f'<div class="call-card"><span class="call-live"><span class="activity-pulse"></span> Live preview call</span><br><strong>{call["mode"]} call with {html.escape(call["name"])}</strong><p>Microphone and camera controls are ready in this local preview. A real internet call needs a WebRTC signaling service.</p></div>', unsafe_allow_html=True)
            if call["mode"] == "Video":
                camera_call = st.camera_input("Camera preview", key="active_video_call_camera")
                if camera_call is not None:
                    st.image(camera_call, caption="Your video preview", use_container_width=True)
            else:
                st.info("Voice channel is ready. Use the voice recorder below to send a live voice message.")
            if st.button("End call", type="primary", key="end_active_call"):
                end_call()
                st.rerun()
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-header">{avatar(chat)}<div><strong>{html.escape(chat["name"])}</strong><br><small>{html.escape(chat["status"])} <span class="status-dot"></span></small></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
        for item in chat["messages"]:
            direction, message, time = item[:3]
            if direction == "voice":
                st.markdown(f'<div class="bubble out"><div class="voice-message"><span class="voice-icon">&#9835;</span><strong>Voice message</strong></div><small>{html.escape(time)}  delivered</small></div>', unsafe_allow_html=True)
                st.audio(message, format="audio/wav")
                continue
            safe_message = html.escape(message)
            css_class = "bubble out" if direction == "out" else "bubble"
            st.markdown(f'<div class="{css_class}">{safe_message}<small>{html.escape(time)}' + ("  delivered" if direction == "out" else "") + '</small></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        action_col, voice_col, send_col = st.columns([1, 1, 5])
        with action_col:
            with st.popover("＋", help="Send a photo, video, file, GIF, location, payment, audio, or document"):
                attachment_icons = [("▧", "Image"), ("▶", "Video"), ("♫", "Audio"), ("▤", "Document"), ("GIF", "GIF"), ("⌁", "File"), ("⌖", "Live location"), ("¤", "Payment")]
                if "attachment_kind" not in st.session_state:
                    st.session_state.attachment_kind = "Image"
                icon_columns = st.columns(4)
                for icon_column, (icon, kind) in zip(icon_columns * 2, attachment_icons):
                    with icon_column:
                        if st.button(icon, key=f"attachment_{kind}", help=kind, use_container_width=True):
                            st.session_state.attachment_kind = kind
                attachment_kind = st.session_state.attachment_kind
                if attachment_kind == "Live location":
                    location_name = st.text_input("Location name", placeholder="Current location", key="location_name")
                    if st.button("⌖", type="primary", use_container_width=True, help="Share location"):
                        location = location_name.strip() or "Current location"
                        send_message(f"Location shared: {location}")
                        st.toast("Location shared")
                        st.rerun()
                elif attachment_kind == "Payment":
                    payment_amount = st.number_input("Amount", min_value=0.0, step=1.0, format="%.2f", key="payment_amount")
                    payment_note = st.text_input("Note", placeholder="Dinner, tickets...", key="payment_note")
                    if st.button("¤", type="primary", use_container_width=True, help="Send payment"):
                        note = f" - {payment_note.strip()}" if payment_note.strip() else ""
                        send_message(f"Payment request: {payment_amount:.2f}{note}")
                        st.toast("Payment shared in preview")
                        st.rerun()
                else:
                    shared_file = st.file_uploader(f"Choose {attachment_kind.lower()}", type=None, key=f"shared_{attachment_kind.lower()}")
                    if shared_file is not None:
                        shared_id = f"{attachment_kind}:{shared_file.name}:{shared_file.size}"
                        if shared_id != st.session_state.get("last_shared_attachment"):
                            st.session_state.last_shared_attachment = shared_id
                            send_message("", shared_file.name, shared_file.size)
                            st.toast(f"{attachment_kind} shared")
                            st.rerun()
        with voice_col:
            voice_message = st.audio_input("Voice", key="chat_voice_message", label_visibility="collapsed")
        with send_col:
            with st.form("message_form", clear_on_submit=True):
                message = st.text_input("Write a message", label_visibility="collapsed", placeholder="Message...")
                send_clicked = st.form_submit_button("➤", use_container_width=True, help="Send message")
        if voice_message is not None:
            voice_id = f"{voice_message.name}:{voice_message.size}"
            if voice_id != st.session_state.get("last_voice_message"):
                now = datetime.now().strftime("%I:%M %p").lstrip("0")
                chat["messages"].append(("voice", voice_message.getvalue(), now, voice_message.size))
                chat["preview"] = "Voice message"
                database_save_voice(chat, voice_message.getvalue(), now)
                st.session_state.last_voice_message = voice_id
                st.toast("Voice message sent")
                st.rerun()
        if send_clicked:
            send_message(message)
            st.rerun()
    with right:
        st.markdown('<div class="feature-card"><h3>Online now</h3><p>Friends ready to chat.</p></div>', unsafe_allow_html=True)
        for online_chat in st.session_state.chats:
            st.markdown(f'<div class="online-row">{avatar(online_chat)}<div><strong>{html.escape(online_chat["name"])}</strong><small>Available to chat</small></div></div>', unsafe_allow_html=True)
        if st.button("View all online friends", use_container_width=True):
            st.session_state.show_online = not st.session_state.show_online
        if st.session_state.show_online:
            st.markdown('<div class="online-card"><strong>All online friends</strong><p>5 friends available to chat right now.</p>', unsafe_allow_html=True)
            for online_chat in st.session_state.chats:
                st.markdown(f'{avatar(online_chat)} <strong>{html.escape(online_chat["name"])}</strong><br>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "AI Tutor":
    st.subheader("Vela AI Tutor")
    st.write("Create study material, understand difficult answers, and build a revision plan.")
    st.caption("Works offline for free. Add OPENAI_API_KEY and optionally OPENAI_BASE_URL/OPENAI_MODEL for an OpenAI-compatible provider.")
    task = st.selectbox("What should Vela make?", ["Make a quiz", "Explain an answer", "Make flashcards", "Summarize notes", "Make a study plan", "Ask Vela anything"])
    subject = st.text_input("Subject or topic", placeholder="Biology - cell division")
    material = st.text_area("Question, notes, or learning material", placeholder="Paste notes or ask a question here...", height=150)
    settings_col, count_col = st.columns(2)
    with settings_col:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    with count_col:
        count = st.slider("Quiz/cards count", min_value=1, max_value=20, value=5)
    if st.button("Generate with Vela", type="primary", use_container_width=True):
        with st.spinner("Vela is preparing your study help..."):
            st.session_state.ai_result = tutor_answer(task, subject, material, difficulty, count)
    if st.session_state.ai_result:
        result = st.session_state.ai_result
        st.success(f"Ready - {result['provider']}")
        st.markdown(result["text"])
        st.download_button("Download study material", result["text"], file_name="vela-study-material.txt", mime="text/plain")

elif page == "Feed":
    st.subheader("Feed")
    st.write("Share anything with your people: thoughts, photos, videos, documents, links, or updates.")
    with st.form("feed_post_form", clear_on_submit=True):
        post_text = st.text_area("Create a post", placeholder="What is on your mind?", height=100)
        post_media = st.file_uploader("Add any photo, video, document, or file", type=None, key="feed_media")
        post_button = st.form_submit_button("Post to feed", type="primary", use_container_width=True)
        if post_button:
            if post_text.strip() or post_media is not None:
                st.session_state.feed_posts.insert(0, {"id": datetime.now().timestamp(), "author": "Maya Chen", "initials": "MC", "color": "green", "time": "just now", "text": post_text.strip(), "media": post_media, "likes": 0, "liked": False, "comments": []})
                try:
                    database.save_post(st.session_state.feed_posts[0])
                except Exception as error:
                    st.session_state.database_error = str(error)
                st.success("Your post is live in this preview session.")
                st.rerun()
            else:
                st.warning("Add text or a file before posting.")
    st.divider()
    for post in st.session_state.feed_posts:
        st.markdown(f'<div class="feature-card"><div class="online-row">{avatar(post)}<div><strong>{html.escape(post["author"])}</strong><small>{html.escape(post["time"])}</small></div></div>', unsafe_allow_html=True)
        if post["text"]:
            st.markdown(html.escape(post["text"]))
        if post["media"] is not None:
            media = post["media"]
            st.caption(f"Attached: {media.name} ({media.size:,} bytes)")
            if media.type.startswith("image/"):
                st.image(media, use_container_width=True)
        like_col, comment_col = st.columns([1, 4])
        with like_col:
            like_label = f"Liked {post['likes']}" if post["liked"] else f"Like {post['likes']}"
            if st.button(like_label, key=f"like_{post['id']}"):
                post["liked"] = not post["liked"]
                post["likes"] += 1 if post["liked"] else -1
                try:
                    database.save_post(post)
                except Exception as error:
                    st.session_state.database_error = str(error)
                st.rerun()
        with comment_col:
            with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                comment = st.text_input("Add a comment", label_visibility="collapsed", placeholder="Add a comment...")
                if st.form_submit_button("Comment") and comment.strip():
                    post["comments"].append(comment.strip())
                    try:
                        database.save_post(post)
                    except Exception as error:
                        st.session_state.database_error = str(error)
                    st.rerun()
        for comment in post["comments"]:
            st.caption(f"{comment}")
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Status":
    st.subheader("Updates")
    st.info("Share text, photos, videos, GIFs, and voice updates with your contacts.")
    status_text = st.text_area("Create a status", placeholder="What is happening?")
    status_file = st.file_uploader("Add media", type=None, key="status_upload")
    if st.button("Post status", type="primary"):
        st.success("Your status is live for this preview session.")
    st.subheader("Recent updates")
    st.write("Sofia Carter - 12 minutes ago")
    st.write("The Weekend Crew - 1 hour ago")

elif page == "Calls":
    st.subheader("Calls")
    st.info("Start a voice or video call from any conversation. This preview uses your local microphone and camera.")
    call_person = st.selectbox("Contact", [chat["name"] for chat in st.session_state.chats], key="call_contact")
    selected_chat = next(chat for chat in st.session_state.chats if chat["name"] == call_person)
    call_voice_col, call_video_col = st.columns(2)
    with call_voice_col:
        if st.button("☎", type="primary", use_container_width=True, help="Start voice call"):
            start_call("Voice", selected_chat)
            st.rerun()
    with call_video_col:
        if st.button("▣", type="primary", use_container_width=True, help="Start video call"):
            start_call("Video", selected_chat)
            st.rerun()
    if st.session_state.active_call is not None:
        call = st.session_state.active_call
        st.markdown(f'<div class="call-card"><span class="call-live"><span class="activity-pulse"></span> Connected in preview</span><br><strong>{call["mode"]} call with {html.escape(call["name"])}</strong><p>Keep this tab open while testing your call controls.</p></div>', unsafe_allow_html=True)
        if call["mode"] == "Video":
            call_camera = st.camera_input("Your camera", key="calls_video_camera")
            if call_camera is not None:
                st.image(call_camera, caption="Video frame captured", use_container_width=True)
        else:
            st.audio_input("Record a voice message during this call", key="calls_voice_message")
        if st.button("End call", key="end_calls_page"):
            end_call()
            st.rerun()
    st.subheader("Recent calls")
    for person, kind, time in [("Sofia Carter", "Video call", "Today, 10:15 AM"), ("Jordan Williams", "Voice call", "Yesterday, 6:30 PM"), ("The Weekend Crew", "Group call", "Monday, 8:00 PM")]:
        st.markdown(f"**{person}**  \n{kind} - {time}")
        st.divider()

elif page == "Files":
    st.subheader("File converter")
    st.write("Convert documents, images, audio, video, and archives. This preview applies no app-level file type or size restriction.")
    file_kind = st.selectbox("Output format", ["PDF", "DOCX", "JPG", "PNG", "TXT", "Keep original"])
    conversion_file = st.file_uploader("Choose any file to convert", type=None, key="conversion_upload")
    if conversion_file is not None:
        st.success(f"{conversion_file.name} is ready to convert to {file_kind}.")
        if st.button("Convert file", type="primary"):
            st.success("Conversion queued for this preview session.")
    st.subheader("Recent files")
    st.dataframe([{"File": "Project brief.pdf", "Status": "Converted", "Size": "2.4 MB"}, {"File": "Meeting notes.docx", "Status": "Converted", "Size": "840 KB"}, {"File": "Receipt-october.jpg", "Status": "Scanned", "Size": "1.1 MB"}], use_container_width=True, hide_index=True)

elif page == "Scan":
    st.subheader("Scan a document")
    document_type = st.selectbox("Document type", ["ID card", "Passport", "Receipt", "Invoice", "Contract", "Notes", "Other"])
    camera_image = st.camera_input(f"Scan {document_type}")
    if camera_image is not None:
        st.image(camera_image, caption=f"{document_type} captured")
        st.success("Document enhanced, edges detected, and ready to export as PDF.")
        if st.button("Export scan", type="primary"):
            st.success("Scan exported to your Files workspace.")
    with st.expander("Scan settings"):
        st.checkbox("Auto-crop and enhance", value=True)
        st.selectbox("Output format", ["PDF document", "JPG image", "PNG image"])

else:
    st.subheader("Settings")
    st.toggle("Read receipts", value=True)
    st.toggle("Last seen and online", value=True)
    st.toggle("Notifications", value=True)
    st.toggle("Dark mode", value=False)
    st.selectbox("App language", ["English", "Hindi", "Spanish", "French"])
    st.info("End-to-end encryption, account security, linked devices, blocked contacts, storage management, and privacy controls belong here in a production build.")
