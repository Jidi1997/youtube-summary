import os
import subprocess
import json
import glob
import re
import urllib.request
import urllib.error
import config

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    HAS_TRANSCRIPT_API = True
except ImportError:
    HAS_TRANSCRIPT_API = False

class DownloadError(Exception):
    pass

def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")

def normalize_url(url):
    if url.startswith('-'):
        return f"https://www.youtube.com/watch?v={url}"
    return url

def extract_video_id(url):
    if not url:
        return None
    if not url.startswith("http") and not "/" in url:
        return url
    if "v=" in url:
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            return match.group(1)
    match = re.search(r'youtu\.be\/([^?&]+)', url)
    if match:
        return match.group(1)
    for pattern in [r'/embed/([^?&]+)', r'/v/([^?&]+)', r'/shorts/([^?&]+)']:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    parts = url.rstrip("/").split("/")
    if parts:
        last = parts[-1]
        if "?" in last:
            last = last.split("?")[0]
        return last
    return url

def get_video_metadata(url):
    url = normalize_url(url)
    print(f"Fetching metadata for: {url}")
    cmd = ["yt-dlp", "-j", "--no-playlist", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        meta = json.loads(result.stdout)
        video_id = meta.get("id")
        title = meta.get("title")
        extracted_meta = {
            "id": video_id,
            "title": title,
            "channel": meta.get("channel"),
            "duration": meta.get("duration"),
            "webpage_url": meta.get("webpage_url"),
            "safe_title": clean_filename(title)
        }
        meta_path = os.path.join(config.METADATA_DIR, f"{video_id}_meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_meta, f, indent=4, ensure_ascii=False)
        return extracted_meta
    except Exception as e:
        raise DownloadError(f"Failed to fetch metadata via yt-dlp: {str(e)}")

def update_meta_language(video_id, language_code):
    meta_path = os.path.join(config.METADATA_DIR, f"{video_id}_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            meta["language"] = language_code
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

def transcribe_audio_groq(audio_path, video_id):
    groq_key = config.GROQ_API_KEY
    if not groq_key:
        raise DownloadError("GROQ_API_KEY is not configured.")
        
    print(f"Transcribing audio via Groq Cloud Whisper API for video ID: {video_id}...")
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = []
    
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-large-v3\r\n".encode('utf-8'))
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"response_format\"\r\n\r\nverbose_json\r\n".encode('utf-8'))
    
    filename = os.path.basename(audio_path)
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\nContent-Type: audio/m4a\r\n\r\n".encode('utf-8'))
    with open(audio_path, 'rb') as f:
        body.append(f.read())
    body.append(f"\r\n--{boundary}--\r\n".encode('utf-8'))
    
    payload = b"".join(body)
    
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        data=payload,
        headers={
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res_json = json.loads(resp.read().decode('utf-8'))
            segments = res_json.get("segments", [])
            formatted_lines = []
            for seg in segments:
                start = seg.get("start", 0.0)
                text = seg.get("text", "").strip()
                formatted_lines.append(f"[{start:.2f}] {text}")
                
            txt_path = os.path.join(config.METADATA_DIR, f"{video_id}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(formatted_lines))
            print(f"Groq Whisper transcription complete. Saved to {txt_path}")
            return txt_path
    except Exception as e:
        raise DownloadError(f"Groq Cloud Whisper transcription failed: {str(e)}")

def download_subtitles(url, video_id):
    url = normalize_url(url)
    languages_priority = ["zh-Hans", "zh-CN", "zh-TW", "zh-HK", "zh", "en"]
    
    if HAS_TRANSCRIPT_API:
        print(f"Attempting transcript fetch via youtube-transcript-api for video ID: {video_id}...")
        try:
            api = YouTubeTranscriptApi()
            if hasattr(api, 'list'):
                transcript_list = api.list(video_id)
            elif hasattr(YouTubeTranscriptApi, 'list_transcripts'):
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            else:
                transcript_list = YouTubeTranscriptApi().list_transcripts(video_id)
                
            transcript = None
            try:
                transcript = transcript_list.find_transcript(languages_priority)
            except Exception:
                for t in transcript_list:
                    transcript = t
                    break
            
            if transcript:
                data = transcript.fetch()
                formatted_lines = []
                for entry in data:
                    text = getattr(entry, 'text', None) or (entry.get('text') if isinstance(entry, dict) else str(entry))
                    start = getattr(entry, 'start', 0.0) or (entry.get('start', 0.0) if isinstance(entry, dict) else 0.0)
                    formatted_lines.append(f"[{float(start):.2f}] {str(text).strip()}")
                    
                txt_path = os.path.join(config.METADATA_DIR, f"{video_id}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(formatted_lines))
                lang_code = getattr(transcript, "language_code", "unknown")
                update_meta_language(video_id, lang_code)
                return txt_path, False
        except Exception as e:
            print(f"youtube-transcript-api fallback to yt-dlp: {e}")

    output_template = os.path.join(config.METADATA_DIR, f"{video_id}.%(ext)s")
    cmd = [
        "yt-dlp", "--write-subs", "--write-auto-subs", "--skip-download",
        "--sub-format", "vtt", "--sub-langs", ",".join(languages_priority),
        "-o", output_template, "--no-playlist", url
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception:
        pass
        
    downloaded_files = glob.glob(os.path.join(config.METADATA_DIR, f"{video_id}.*.vtt"))
    if not downloaded_files:
        if not config.GROQ_API_KEY:
            raise DownloadError(f"No subtitles found for video ID: {video_id} (ASR skipped: GROQ_API_KEY not set).")
        print(f"No subtitles found for video ID: {video_id}. Attempting ASR fallback...")
        output_audio_template = os.path.join(config.METADATA_DIR, f"{video_id}.%(ext)s")
        audio_cmd = [
            "yt-dlp", "-x", "--audio-format", "m4a", "-f", "ba[ext=m4a]/ba",
            "-o", output_audio_template, "--no-playlist", url
        ]
        audio_extensions = {".m4a", ".webm", ".opus", ".mp3", ".wav"}
        temp_extensions = {".part", ".ytdl", ".temp"}
        
        try:
            print("Downloading audio track via yt-dlp...")
            subprocess.run(audio_cmd, capture_output=True, text=True, check=True)
            all_files = glob.glob(os.path.join(config.METADATA_DIR, f"{video_id}.*"))
            audio_path = None
            for f in all_files:
                ext = os.path.splitext(f)[1].lower()
                if ext in audio_extensions:
                    audio_path = f
                    break
            if not audio_path:
                raise DownloadError(f"Audio file was not created in {config.METADATA_DIR}")
                
            if config.GROQ_API_KEY:
                txt_path = transcribe_audio_groq(audio_path, video_id)
            else:
                raise DownloadError(
                    "No subtitles found for this video. To transcribe audio via fast cloud API,\n"
                    "set GROQ_API_KEY=your_key in your .env file."
                )
                    
            update_meta_language(video_id, "auto")
            return txt_path, False
        finally:
            for f in glob.glob(os.path.join(config.METADATA_DIR, f"{video_id}.*")):
                ext = os.path.splitext(f)[1].lower()
                is_audio = ext in audio_extensions
                is_temp = ext in temp_extensions or any(t_ext in f.lower() for t_ext in temp_extensions)
                if (is_audio or is_temp) and os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception:
                        pass
                        
    selected_file = downloaded_files[0]
    update_meta_language(video_id, "unknown")
    return selected_file, True
