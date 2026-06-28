import os
import glob
import time
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from flask import Flask, jsonify, request, send_from_directory, redirect
import yt_dlp

app = Flask(__name__, static_folder="static")

CACHE_DIR = os.path.join("static", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

YDL_OPTS_SEARCH = {
    "quiet": True,
    "no_warnings": True,
    "extract_flat": True,
    "skip_download": True,
    "extractor_args": {"youtube": {"player_client": ["android", "ios", "web"]}},
}

YDL_OPTS_STREAM = {
    "quiet": True,
    "no_warnings": True,
    "format": "bestaudio/best",
    "extractor_args": {"youtube": {"player_client": ["android", "ios", "web"]}},
}

# ── In-memory cache (TTL) ──
_CACHE: Dict[str, Tuple[float, Any]] = {}
_CACHE_TTL = 3600  # 1 hour

def cache_get(key: str):
    entry = _CACHE.get(key)
    if not entry:
        return None
    ts, data = entry
    if time.time() - ts > _CACHE_TTL:
        del _CACHE[key]
        return None
    return data

def cache_set(key: str, data):
    _CACHE[key] = (time.time(), data)
    if len(_CACHE) > 500:
        oldest = sorted(_CACHE.items(), key=lambda x: x[1][0])[:50]
        for k, _ in oldest:
            del _CACHE[k]

def cleanup_cache_dir():
    # Keep the cache dir under 1 GB
    MAX_SIZE = 1024 * 1024 * 1024
    files = []
    total_size = 0
    for f in glob.glob(os.path.join(CACHE_DIR, "*")):
        if os.path.isfile(f):
            size = os.path.getsize(f)
            files.append((f, os.path.getmtime(f), size))
            total_size += size
            
    if total_size > MAX_SIZE:
        files.sort(key=lambda x: x[1])
        for f, mtime, size in files:
            try:
                os.remove(f)
                total_size -= size
                if total_size <= MAX_SIZE * 0.8:
                    break
            except Exception:
                pass

def is_clean_title(title: str) -> bool:
    """Filter out covers, karaoke, 8D, slowed, etc."""
    lower = title.lower()
    junk_words = ["cover", "karaoke", "8d", "slowed", "reverb", "1 hour", "playlist", "instrumental", "type beat", "live at", "live performance", "bass boosted"]
    for w in junk_words:
        if w in lower:
            return False
    return True

def _format_entry(entry: dict) -> Optional[dict]:
    if not entry:
        return None
    vid_id = entry.get("id", "")
    if not vid_id:
        return None
    title = entry.get("title", "")
    if not is_clean_title(title):
        return None
        
    duration_sec = entry.get("duration") or 0
    mins, secs = divmod(int(duration_sec), 60)
    duration_str = f"{mins}:{secs:02d}" if duration_sec else ""
    views = entry.get("view_count") or 0
    views_str = f"{views:,}" if views else ""
    thumb = f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg"
    return {
        "id": vid_id,
        "title": title,
        "channel": entry.get("uploader") or entry.get("channel", ""),
        "thumbnail": thumb,
        "duration": duration_str,
        "views": views_str,
    }

def yt_search(query: str, limit: int = 15) -> Tuple[List[dict], bool]:
    key = f"ytsearch_{query}_{limit}"
    cached = cache_get(key)
    if cached is not None:
        return cached, True
        
    # We ask for a bit more results than needed so we can filter out junk and still have enough
    with yt_dlp.YoutubeDL(YDL_OPTS_SEARCH) as ydl:
        info = ydl.extract_info(f"ytsearch{limit + 5}:{query} official music", download=False)
        
    results = []
    for entry in info.get("entries", []):
        item = _format_entry(entry)
        if item:
            results.append(item)
            if len(results) >= limit:
                break
                
    cache_set(key, results)
    return results, False

GENRES = [
    "Pop", "Rock", "Hip-Hop", "R&B", "Bollywood", "Punjabi",
    "Electronic", "Lo-Fi", "Jazz", "Classical", "K-Pop", "Country",
]

LANGUAGES = [
    "English", "Hindi", "Punjabi", "Tamil", "Telugu",
    "Spanish", "Korean", "Arabic", "Bengali", "Marathi",
]

POPULAR_ARTISTS = [
    "Taylor Swift", "The Weeknd", "Lana Del Rey", "Billie Eilish", "Drake",
    "Ariana Grande", "Ed Sheeran", "Dua Lipa", "Rihanna", "Post Malone",
    "Eminem", "Harry Styles", "Olivia Rodrigo", "SZA", "Bad Bunny",
]

POPULAR_HITS = [
    "Taylor Swift - Cruel Summer",
    "The Weeknd - Blinding Lights",
    "Lana Del Rey - Summertime Sadness",
    "Billie Eilish - Birds of a Feather",
    "Drake - One Dance",
]

TRENDING_DEFAULT = (
    "Taylor Swift Cruel Summer The Weeknd Blinding Lights "
    "Lana Del Rey Video Games Billie Eilish official music video"
)

def _match_popular(query: str) -> List[str]:
    q = query.lower().strip()
    if not q:
        return POPULAR_ARTISTS[:8]
    seen = set()
    out = []
    for item in POPULAR_HITS + POPULAR_ARTISTS:
        if q in item.lower() and item.lower() not in seen:
            seen.add(item.lower())
            out.append(item)
    for item in POPULAR_ARTISTS:
        words = item.lower().split()
        if any(w.startswith(q) for w in words) and item.lower() not in seen:
            seen.add(item.lower())
            out.append(item)
    return out[:8]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/meta")
def meta():
    return jsonify({
        "genres": GENRES,
        "languages": LANGUAGES,
        "popular_artists": POPULAR_ARTISTS[:16],
        "popular_hits": POPULAR_HITS,
    })

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": [], "cached": False})
    try:
        results, from_cache = yt_search(query, 12)
        return jsonify({"results": results, "cached": from_cache})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

@app.route("/suggest")
def suggest():
    query = request.args.get("q", "").strip()
    key = f"suggest_{query.lower()}"
    cached = cache_get(key)
    if cached is not None:
        return jsonify({"suggestions": cached, "cached": True})

    matches = _match_popular(query)
    if len(matches) >= 4 or not query:
        cache_set(key, matches)
        return jsonify({"suggestions": matches, "cached": False})

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_SEARCH) as ydl:
            info = ydl.extract_info(f"ytsearch8:{query} official music", download=False)
        seen = {m.lower() for m in matches}
        for entry in info.get("entries", []):
            if not entry or len(matches) >= 8:
                break
            title = entry.get("title", "").strip()
            if not title or title.lower() in seen or not is_clean_title(title):
                continue
            seen.add(title.lower())
            matches.append(title)
        cache_set(key, matches[:8])
        return jsonify({"suggestions": matches[:8], "cached": False})
    except Exception:
        cache_set(key, matches)
        return jsonify({"suggestions": matches, "cached": False})

@app.route("/discover/trending")
def trending():
    genre = request.args.get("genre", "").strip()
    lang = request.args.get("lang", "").strip()
    query = TRENDING_DEFAULT
    if genre or lang:
        query = f"top {lang} {genre} songs official music"
        
    try:
        results, _ = yt_search(query, 12)
        return jsonify({"results": results, "query": query})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

@app.route("/discover/picks")
def picks():
    genre = request.args.get("genre", "Pop").strip()
    lang = request.args.get("lang", "English").strip()
    query = f"best {lang} {genre} popular official music"
    try:
        results, _ = yt_search(query, 10)
        return jsonify({"results": results, "query": query})
    except Exception as e:
        return jsonify({"error": str(e), "results": []}), 500

@app.route("/stream")
def stream():
    vid_id = request.args.get("id", "").strip()
    
    if not vid_id:
        return "Missing id", 400
        
    query_hash = hashlib.md5(vid_id.encode()).hexdigest()
    
    existing_files = glob.glob(os.path.join(CACHE_DIR, f"{query_hash}.*"))
    if existing_files:
        rel_path = existing_files[0].replace('\\', '/')
        return redirect(f"/{rel_path}")
        
    cleanup_cache_dir()
    
    opts = YDL_OPTS_STREAM.copy()
    opts["outtmpl"] = os.path.join(CACHE_DIR, f"{query_hash}.%(ext)s")
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(vid_id, download=True)
            if not info:
                return "Not found", 404
                
            downloaded_files = glob.glob(os.path.join(CACHE_DIR, f"{query_hash}.*"))
            if downloaded_files:
                rel_path = downloaded_files[0].replace('\\', '/')
                return redirect(f"/{rel_path}")
            else:
                return "Download failed", 500
    except Exception as e:
        print(f"Streaming error: {e}")
        return str(e), 500

if __name__ == "__main__":
    print("\n🎵  Musiflow running at http://localhost:5000\n")
    app.run(debug=False, port=5000)


@app.route("/lyrics")
def lyrics():
    import urllib.request, urllib.parse, json as _json
    artist = request.args.get("artist", "").strip()
    title  = request.args.get("title",  "").strip()
    if not artist or not title:
        return jsonify({"synced": "", "plain": "", "source": "none"})
    key = f"lyrics:{artist.lower()}:{title.lower()}"
    cached = cache_get(key)
    if cached:
        return jsonify(cached)
    # 1) lrclib (has synced LRC)
    try:
        params = urllib.parse.urlencode({"artist_name": artist, "track_name": title})
        req = urllib.request.Request(
            f"https://lrclib.net/api/get?{params}",
            headers={"User-Agent": "Musiflow/1.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            data = _json.loads(r.read())
        result = {
            "synced": data.get("syncedLyrics") or "",
            "plain":  data.get("plainLyrics")  or "",
            "source": "lrclib"
        }
        if result["synced"] or result["plain"]:
            cache_set(key, result)
            return jsonify(result)
    except Exception:
        pass
    # 2) lyrics.ovh fallback
    try:
        a = urllib.parse.quote(artist)
        t = urllib.parse.quote(title)
        req = urllib.request.Request(
            f"https://api.lyrics.ovh/v1/{a}/{t}",
            headers={"User-Agent": "Musiflow/1.0"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            data = _json.loads(r.read())
        result = {"synced": "", "plain": data.get("lyrics", ""), "source": "lyrics.ovh"}
        if result["plain"]:
            cache_set(key, result)
            return jsonify(result)
    except Exception:
        pass
    return jsonify({"synced": "", "plain": "", "source": "none"})
