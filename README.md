# 🎵 Musiflow

A free, local music streaming app built with Flask and yt-dlp. No API keys. No subscriptions. Just music.

---

## What it does

- Searches YouTube for any song, artist, or album
- Downloads and streams audio directly — no YouTube embeds, no "video unavailable"
- Personalized genre + language onboarding on first visit
- Trending, suggested, and genre-specific sections loaded on home screen
- Live search suggestions as you type
- Synced lyrics (karaoke-style highlighting) via lrclib + lyrics.ovh fallback
- Queue management — add, remove, reorder, shuffle, repeat
- Top 10 most played tracker (per browser)
- Ambient background that shifts color with each song
- Fully mobile responsive with a slide-up queue drawer
- Smart caching — searches, suggestions, and lyrics cached server-side and in localStorage

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.8+ · Flask |
| Audio | yt-dlp (downloads best audio, serves locally) |
| Lyrics | lrclib.net (synced LRC) · lyrics.ovh (fallback) |
| Frontend | Vanilla HTML/CSS/JS — zero dependencies |
| Caching | In-memory TTL cache (server) + localStorage (browser) |

---

## Setup

**1. Install dependencies**
```bash
pip install flask yt-dlp
```

**2. Run the server**
```bash
cd music_app
py app.py          # Windows
python3 app.py     # Mac / Linux
```

**3. Open in browser**
```
http://localhost:5000
```

That's it.

---

## Sharing with friends (ngrok)

Want to share with friends over the internet for free?

**1. Install ngrok** → https://ngrok.com/download

**2. Start your Flask server** in one terminal:
```bash
py app.py
```

**3. Start ngrok** in a second terminal:
```bash
ngrok http 5000
```

**4. Share the ngrok URL** (looks like `https://abc123.ngrok-free.app`) with friends.

> ⚠️ Keep both terminals open. If either closes, the app goes down.
> Free ngrok URLs change every restart — sign up for a free account to get a static domain.

Each friend gets their own independent player — their own queue, their own playback, their own experience. Video streams from YouTube directly to their browser, not through your PC.

---

## Project structure

```
music_app/
├── app.py               # Flask backend — search, stream, lyrics, suggestions
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── static/
    ├── index.html       # Entire frontend (HTML + CSS + JS in one file)
    └── cache/           # Downloaded audio files (auto-managed, max 1GB)
```

---

## How audio streaming works

```
You search "Arijit Singh Kesariya"
        ↓
Flask calls yt-dlp → searches YouTube → returns results
        ↓
You click Play
        ↓
Flask calls yt-dlp again → downloads best audio for that video ID
        ↓
File saved to static/cache/<md5hash>.webm (or .mp4)
        ↓
Browser's <audio> element plays the file directly
        ↓
Next time the same song is played → file already cached → instant playback
```

Cache is automatically cleaned when it exceeds 1GB, removing oldest files first.

---

## How lyrics work

```
Song starts playing
        ↓
Frontend extracts artist name + song title from the result
        ↓
Calls lrclib.net → tries to find synced LRC lyrics (with timestamps)
        ↓
If found → lyrics panel shows karaoke-style highlighting in sync with audio
If not found → falls back to lyrics.ovh for plain text lyrics
If neither → shows "No lyrics found"
        ↓
Result cached in localStorage for 1 hour
```

---

## Updating yt-dlp

YouTube changes its internals regularly. If search or streaming breaks, run:
```bash
pip install -U yt-dlp
```

---

## Notes

- Audio files in `static/cache/` are temporary — safe to delete anytime
- The app is stateless — no database, no user accounts, no login
- Each browser tab is independent — no shared playback between users
- Works best on Chrome / Edge / Firefox desktop and mobile
- Not intended for public deployment — for personal and friend use only

---

## Built by

Harshvardhan · Vibe coded with Claude 🤖
