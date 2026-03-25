# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import hashlib
import sqlite3
import re
from datetime import datetime

# =====================================================
# 1. PAGE CONFIG & STYLING
# =====================================================
st.set_page_config(page_title="Ghar ka GPT Pro by Naved", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    /* Clean Sidebar Styling */
    .stButton > button { border-radius: 8px !important; }
    .stDownloadButton > button { background-color: #10a37f !important; color: white !important; }
    /* Model Selector Styling */
    .stSelectbox label { font-weight: bold !important; color: #667eea !important; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. DATABASE ARCHITECTURE
# =====================================================
DB_PATH = 'dev_bot_v2.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (pin_hash TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS threads (id INTEGER PRIMARY KEY, title TEXT, created_at TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history (thread_id INTEGER, role TEXT, content TEXT)')
    c.execute('SELECT * FROM users')
    if not c.fetchone():
        c.execute('INSERT INTO users VALUES (?)', (hashlib.sha256("6767".encode()).hexdigest(),))
    conn.commit()
    conn.close()

def get_all_threads():
    conn = sqlite3.connect(DB_PATH)
    threads = conn.execute('SELECT id, title FROM threads ORDER BY id DESC').fetchall()
    conn.close()
    return threads

def delete_thread(tid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM threads WHERE id = ?', (tid,))
    conn.execute('DELETE FROM history WHERE thread_id = ?', (tid,))
    conn.commit()
    conn.close()

def create_thread(title):
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute('INSERT INTO threads (title, created_at) VALUES (?, ?)', (title, datetime.now().strftime("%Y-%m-%d %H:%M")))
    new_id = curr.lastrowid
    conn.commit()
    conn.close()
    return new_id

def load_messages(thread_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT role, content FROM history WHERE thread_id = ?', (thread_id,)).fetchall()
    conn.close()
    return [{"role": r, "content": m} for r, m in rows]

def save_msg(thread_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO history VALUES (?, ?, ?)', (thread_id, role, content))
    conn.commit()
    conn.close()

init_db()

# =====================================================
# 3. AUTHENTICATION
# =====================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, col, _ = st.columns([1,1,1])
    with col:
        st.markdown("<h2 style='text-align: center;'>Naved GPT Pro</h2>", unsafe_allow_html=True)
        pin = st.text_input("Developer PIN", type="password")
        if st.button("Unlock Chats", use_container_width=True):
            db_pin = sqlite3.connect(DB_PATH).execute('SELECT pin_hash FROM users').fetchone()[0]
            if hashlib.sha256(pin.encode()).hexdigest() == db_pin:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid PIN")
    st.stop()

# =====================================================
# 4. SIDEBAR (MODEL SELECTOR & HISTORY)
# =====================================================
with st.sidebar:
    st.title("⚙️ Ghar ka GPT")
    
    # --- MODEL SELECTION (HARDCODED) ---
    AVAILABLE_MODELS = {
        "Qwen 2.5 Coder (Best for Code)": "qwen2.5-coder:3b",
        "Qwen 2.5 (Fast Analysis)": "qwen2.5:3b",
        "Qwen 3.5 (Fast Analysis)": "qwen3.5:2b",
        "Cogito 3b (Fast Analysis)": "cogito:3b"
    }
    
    selected_model_name = st.selectbox(
        "Select AI Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
        help="Switch between models depending on your task."
    )
    target_model = AVAILABLE_MODELS[selected_model_name]
    
    st.divider()
    
    if st.button("➕ Start New Chat", use_container_width=True):
        st.session_state.current_thread_id = None
        st.rerun()
    
    st.divider()
    st.write("**Chat History**")
    
    for tid, title in get_all_threads():
        col_name, col_del = st.columns([4, 1])
        with col_name:
            if st.button(f"📄 {title[:20]}...", key=f"th_{tid}", use_container_width=True):
                st.session_state.current_thread_id = tid
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{tid}", help="Delete Chat"):
                delete_thread(tid)
                if st.session_state.get("current_thread_id") == tid:
                    st.session_state.current_thread_id = None
                st.rerun()
    
    st.divider()
    
    # --- CODE EXPORTER ---
    if st.session_state.get("current_thread_id"):
        msgs = load_messages(st.session_state.current_thread_id)
        last_code = ""
        for m in reversed(msgs):
            if m["role"] == "assistant":
                blocks = re.findall(r"```python\n(.*?)\n```", m["content"], re.DOTALL)
                if blocks:
                    last_code = blocks[-1]
                    break
        if last_code:
            st.download_button("📥 Download app.py", last_code, file_name="generated_app.py", use_container_width=True)

# =====================================================
# 5. MAIN CHAT INTERFACE
# =====================================================
if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = None

if st.session_state.current_thread_id is None:
    st.info(f"Using **{selected_model_name}**. Start typing below to begin.")
    messages = []
else:
    messages = load_messages(st.session_state.current_thread_id)

# Render Chat
for m in messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Logic
if prompt := st.chat_input("Ask me to build a function or a full dashboard..."):
    if st.session_state.current_thread_id is None:
        st.session_state.current_thread_id = create_thread(prompt[:30])
    
    save_msg(st.session_state.current_thread_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response_place = st.empty()
        full_res = ""
        
        try:
            client = OpenAI(
                base_url="https://test.mynewgen.xyz/v1", 
                api_key=st.secrets.get("OLLAMA_API_KEY", "ollama")
            )
            
            # Send context to AI
            current_history = load_messages(st.session_state.current_thread_id)
            
            stream = client.chat.completions.create(
                model=target_model,  # Uses the dynamically selected model!
                messages=[{"role": "system", "content": "You are a Senior Developer. Use ```python blocks for code."}] + current_history,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    response_place.markdown(full_res + "▌")
            
            response_place.markdown(full_res)
            save_msg(st.session_state.current_thread_id, "assistant", full_res)
            st.rerun()
            
        except Exception as e:
            st.error("Home Server Connection Lost. Ensure Ollama is running.")
