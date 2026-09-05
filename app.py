import html
from datetime import datetime
from pathlib import Path

import streamlit as st
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
    @media (max-width: 800px) { .hero-title { font-size:1.65rem; } .feature-card { min-height:auto; } [data-testid="stSidebar"] { display:none; } }
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
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
    st.session_state.feed_posts = [
        {"id": 1, "author": "Sofia Carter", "initials": "SC", "color": "green", "time": "12 minutes ago", "text": "The little things are the big things.", "media": None, "likes": 12, "liked": False, "comments": ["This made my day."]},
        {"id": 2, "author": "The Weekend Crew", "initials": "WC", "color": "yellow", "time": "1 hour ago", "text": "Sunset walks and good company.", "media": None, "likes": 24, "liked": False, "comments": []},
    ]
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None


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


def render_login() -> None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="brand"><span class="brand-mark"></span>vela</div>', unsafe_allow_html=True)
    if not st.session_state.otp_sent:
        st.markdown("## Welcome to Vela")
        st.write("Sign in with your mobile number to keep your conversations, scans, and files together.")
        phone = st.text_input("Mobile number", value="98765 43210", key="phone")
        if st.button("Send OTP", type="primary", use_container_width=True):
            if phone.strip():
                st.session_state.otp_sent = True
                st.rerun()
    else:
        st.markdown("## Check your messages")
        st.write("We sent a one-time code to your mobile number.")
        otp = st.text_input("6-digit OTP", max_chars=6, key="otp")
        st.caption("Demo OTP: 123456")
        if st.button("Verify and open Vela", type="primary", use_container_width=True):
            if otp == "123456":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Use the demo OTP 123456.")
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

if page == "Chats":
    chat = st.session_state.chats[st.session_state.active_chat]
    left, right = st.columns([2.2, 1], gap="large")
    with left:
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-header">{avatar(chat)}<div><strong>{html.escape(chat["name"])}</strong><br><small>{html.escape(chat["status"])} <span class="status-dot"></span></small></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="height:.7rem"></div>', unsafe_allow_html=True)
        for direction, message, time in chat["messages"]:
            safe_message = html.escape(message)
            css_class = "bubble out" if direction == "out" else "bubble"
            st.markdown(f'<div class="{css_class}">{safe_message}<small>{html.escape(time)}' + ("  delivered" if direction == "out" else "") + '</small></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        with st.form("message_form", clear_on_submit=True):
            message = st.text_input("Write a message", label_visibility="collapsed", placeholder="Write a message...")
            send_col, file_col = st.columns([1, 1])
            with send_col:
                send_clicked = st.form_submit_button("Send", use_container_width=True)
            with file_col:
                attachment = st.file_uploader("Attach any file", label_visibility="collapsed", key="chat_attachment", accept_multiple_files=False)
            if send_clicked:
                send_message(message)
                st.rerun()
        if attachment is not None:
            attachment_id = f"{attachment.name}:{attachment.size}"
            if attachment_id != st.session_state.last_attachment:
                st.session_state.last_attachment = attachment_id
                send_message("", attachment.name, attachment.size)
                st.success(f"Attached {attachment.name} - no app-level size or type limit")
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
                st.rerun()
        with comment_col:
            with st.form(f"comment_form_{post['id']}", clear_on_submit=True):
                comment = st.text_input("Add a comment", label_visibility="collapsed", placeholder="Add a comment...")
                if st.form_submit_button("Comment") and comment.strip():
                    post["comments"].append(comment.strip())
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
    st.info("Voice and video call history")
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
