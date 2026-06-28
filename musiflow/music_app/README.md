# Musiflow — YouTube Music Player

A clean, Spotify-like music player that runs locally. No API key needed.
Uses `youtubesearchpython` to search YouTube and plays via the official YouTube embed.

## Setup (one time)

```bash
cd music_app
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

## Features

- Search any song, artist, or album — no API key needed
- Card-based results grid with thumbnails, channel, duration
- Play instantly or add to queue
- Sidebar queue with reordering and remove
- Skip next / previous / shuffle / repeat
- Bottom now-playing bar
- Fully offline-capable after first load (except YouTube video itself)

## Notes

- Playback uses YouTube's official iframe embed (ToS-compliant)
- No ads injected by this app — standard YouTube ads may still appear in the player
- Works on Python 3.8+
