# 🎵 Musiflow

Musiflow is a Flask-based web app that lets you **search and explore music videos on YouTube** using the `yt-dlp` library.  
It provides a simple backend service with endpoints for searching and fetching results, making it easy to integrate into other projects or run standalone.

---

## 🚀 Features
- 🔍 Search YouTube for music videos by keyword
- 📄 Get structured JSON responses with titles, links, and metadata
- ⚡ Lightweight Flask backend — quick to run locally
- 🐳 Docker support for easy deployment
- 🌍 Share publicly using ngrok

---

## 📦 Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (to clone the repo)

### Steps
```bash
# Clone the repository
git clone https://github.com/harshk007-p/Musiflow.git
cd Musiflow

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
