import streamlit as st
from openai import OpenAI
import sqlite3
import re
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY") or "ollama"
BASE_URL = "https://test.mynewgen.xyz/v1"

# Initialize OpenAI Client
def initialize_api(api_key, base_url):
    config = OpenAI.Configuration(base_url=base_url)
    return OpenAI(config=config, api_key=api_key)

# Function to extract code blocks from a Markdown string
def extract_code_blocks(text):
    blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
    return blocks

# Function to load the full response from the API stream
def load_response(client, model, messages, stream=True):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )
    full_res = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_res += chunk.choices[0].delta.content
            response_place.markdown(full_res + "▌")
    return full_res

# Function to download the last generated code block
def download_last_code(response):
    blocks = extract_code_blocks(response)
    if blocks:
        last_code = blocks[-1]
        filename = "generated_app.py"
        with open(filename, "w") as f:
            f.write(last_code)
        st.download_button(filename, f.read(), file_name=filename, use_container_width=True)

# Initialize the database
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

# Function to get all threads
def get_all_threads():
    conn = sqlite3.connect(DB_PATH)
    threads = conn.execute('SELECT id, title FROM threads ORDER BY id DESC').fetchall()
    conn.close()
    return threads

# Function to delete a thread
def delete_thread(tid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM threads WHERE id = ?', (tid,))
    conn.execute('DELETE FROM history WHERE thread_id = ?', (tid,))
    conn.commit()
    conn.close()

# Function to create a new thread
def create_thread(title):
    conn = sqlite3.connect(DB_PATH)
    curr = conn.cursor()
    curr.execute('INSERT INTO threads (title, created_at) VALUES (?, ?)', (title, datetime.now().strftime("%Y-%m-%d %H:%M")))
    new_id = curr.lastrowid
    conn.commit()
    conn.close()
    return new_id

# Function to load messages
def load_messages(thread_id):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT role, content FROM history WHERE thread_id = ?', (thread_id,)).fetchall()
    conn.close()
    return [{"role": r, "content": m} for r, m in rows]

# Function to save a message
def save_msg(thread_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO history VALUES (?, ?, ?)', (thread_id, role, content))
    conn.commit()
    conn.close()

# Main application logic
def main():
    # Set page configuration
    st.set_page_config(page_title="Ghar ka GPT Pro by Naved", layout="wide", page_icon="🚀")

    # Styles for the app
    st.markdown("""
    <style>
        /* Clean Sidebar Styling */
        .stButton > button { border-radius: 8px !important; }
        .stDownloadButton > button { background-color: #10a37f !important; color: white !important; }
        /* Model Selector Styling */
        .stSelectbox label { font-weight: bold !important; color: #667eea !important; }
    </style>
    """, unsafe_allow_html=True)

    # Initialize database
    init_db()

    # Authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        _, col, _ = st.columns([1, 1, 1])
        with col:
            st.markdown("<h2 style='text-align: center;'>Naved GPT Pro</h2>", unsafe_allow_html=True)
            pin = st.text_input("Developer PIN", type="password")
            if st.button("Unlock Chats", use_container_width=True):
                db_pin = sqlite3.connect(DB_PATH).execute('SELECT pin_hash FROM users').fetchone()[0]
                if hashlib.sha256(pin.encode()).hexdigest() == db_pin:
                    st.session_state.authenticated = True
                    st.success("Login successful!")
                else:
                    st.error("Invalid PIN. Please try again.")
        return

    # Sidebar
    st.sidebar.title("Sidebar")
    selected_model = st.sidebar.selectbox("Choose an AI Model", ["model1", "model2", "model3"])  # Example models

    # Main chat container
    with st.container():
        chat_container = st.chat_area(take_focus=False)

    # Load response from OpenAI API
    if chat_container is not None:
        with chat_container:
            for msg in st.session_state.messages:
                st.chat_message(msg=message["role"].lower()).markdown(message["content"], unsafe_allow_html=True)

            if st.session_state.generated_message:
                st.chat_message("assistant").markdown(st.session_state.generated_message, unsafe_allow_html=True)
                st.session_state.generated_message = ""
                download_last_code(st.session_state.generated_message)

            # Input for user message
            user_input = st.chat_input("What do you want to ask about?")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                user_input = st.session_state.messages[-1]["content"]

                # Initialize the OpenAI client
                client = initialize_api(OLLAMA_API_KEY, BASE_URL)

                # Set the AI model
                selected_model = "gpt-3.5-turbo"  # Example model
                messages = [
                    {"role": "system", "content": "You are an assistant supporting the user to generate clear and concise answers."},
                    {"role": "user", "content": user_input}
                ]

                # Load the response from the API stream
                st.session_state.generated_message = load_response(client, selected_model, messages)

if __name__ == "__main__":
    main()
