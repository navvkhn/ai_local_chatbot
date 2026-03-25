# 🚀 Naved GPT Pro: AI App Builder

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange)](https://ollama.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Naved GPT Pro** is a private, secure, and high-performance AI Chatbot interface designed specifically for developers. It connects a sleek ChatGPT-style frontend to your local **Ollama** models, allowing you to build apps, write code, and analyze data without your prompts ever leaving your private infrastructure.



---

## ✨ Key Features

- **🧠 Multi-Model Intelligence:** Switch between specialized models (Qwen Coder, Llama 3.2, etc.) directly from the UI.
- **🔐 Secure Access:** Integrated 4-digit PIN authentication with SHA-256 hashing to protect your local compute resources.
- **💾 Persistent Projects:** Full SQLite integration for project history. Start a project today, finish it next week—the AI remembers everything.
- **📥 One-Click Export:** Automatically detects Python code blocks and provides an instant `.py` file download button.
- **🎨 ChatGPT UX:** A familiar, clean interface with sidebar history, markdown support, and real-time streaming responses.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI Engine:** [Ollama](https://ollama.com/) (Local LLM Server)
- **Database:** SQLite3
- **Networking:** Cloudflare Tunnels (for secure remote access)
- **Language:** Python 3.10+

---

## 🚀 Getting Started

### 1. Prerequisite: Setup Ollama
Ensure Ollama is running on your host machine and you have pulled the required models:
```bash
ollama pull qwen2.5-coder:3b
ollama pull llama3.2:3b

2. Installation
Clone the repository and install the dependencies:

Bash
git clone [[https://github.com/navvkhn/ai_local_chatbot/]]([https://github.com/navvkhn/csv-analysis.git)
cd csv-analysis
pip install -r requirements.txt
3. Environment Secrets
Create a .streamlit/secrets.toml file to store your API configuration:

Ini, TOML
OLLAMA_API_KEY = "your_secure_api_key_here"
4. Launch
Bash
streamlit run app.py
📂 Project Structure
Plaintext
├── .streamlit/
│   └── secrets.toml      # API Keys (Git-ignored)
├── app.py                # Main Application Logic
├── dev_bot_v2.db         # SQLite Database (Local only)
├── requirements.txt      # Python Dependencies
└── README.md             # Project Documentation
🛡️ Privacy & Security
This project is built with a Privacy-First philosophy:

Local Inference: Your data stays on your hardware. No third-party AI provider sees your proprietary code.

Encrypted Auth: Access is gated by a PIN system, ensuring that only authorized developers can trigger the LLM.

Encrypted Tunneling: When accessed remotely, all traffic is encrypted via Cloudflare's global network.

🤝 Contributing
Contributions are welcome! If you have a feature request or a bug report, please open an issue or submit a pull request.

Developed with ❤️ by Naved
```bash
ollama pull qwen2.5-coder:3b
ollama pull llama3.2:3b
