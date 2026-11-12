import os
import re
from pydub import AudioSegment
import yt_dlp

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _get_cookie_file() -> str | None:
  """Write YOUTUBE_COOKIES from environment or Streamlit secrets to a temporary cookies.txt file."""
  cookie_content = os.getenv("YOUTUBE_COOKIES")
  if not cookie_content:
    try:
      import streamlit as st

      cookie_content = st.secrets.get("YOUTUBE_COOKIES")
    except Exception:
      pass

  if cookie_content and cookie_content.strip():
    cookie_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
    with open(cookie_path, "w", encoding="utf-8") as f:
      f.write(cookie_content.strip() + "\n")
    return cookie_path
  return None


def extract_video_id(url: str) -> str | None:
  match = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
  return match.group(1) if match else None


def fetch_youtube_transcript_fallback(url: str) -> str:
  """Fallback when yt-dlp is blocked by YouTube datacenter IP checks."""
  from youtube_transcript_api import YouTubeTranscriptApi

  video_id = extract_video_id(url)
  if not video_id:
    raise ValueError("Could not extract YouTube Video ID from URL.")

  api = YouTubeTranscriptApi()
  transcript_list = api.fetch(video_id, languages=["en", "hi"])
  return " ".join(entry.text for entry in transcript_list)


def download_youtube_audio(url: str) -> str:
  output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
  ydl_opts = {
      "format": "bestaudio/best",
      "outtmpl": output_path,
      "postprocessors": [{
          "key": "FFmpegExtractAudio",
          "preferredcodec": "wav",
          "preferredquality": "192",
      }],
      "js_runtimes": {"node": {}},
      "extractor_args": {
          "youtube": {"player_client": ["mweb", "web"]},
      },
      "nocheckcertificate": True,
      "quiet": True,
  }

  cookie_file = _get_cookie_file()
  if cookie_file:
    ydl_opts["cookiefile"] = cookie_file

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    base_name = os.path.splitext(ydl.prepare_filename(info))[0]
    filename = f"{base_name}.wav"
  return filename


def convert_to_wav(input_path: str) -> str:
  """Convert any audio/video file to 16kHz mono WAV format using pydub."""
  output_path = os.path.splitext(input_path)[0] + "_converted.wav"
  audio = AudioSegment.from_file(input_path)
  audio = audio.set_channels(1).set_frame_rate(16000)
  audio.export(output_path, format="wav")
  return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
  audio = AudioSegment.from_wav(wav_path)
  chunk_ms = chunk_minutes * 60 * 1000
  chunks = []

  for i, start in enumerate(range(0, len(audio), chunk_ms)):
    chunk = audio[start : start + chunk_ms]
    chunk_path = f"{wav_path}_chunk_{i}.wav"
    chunk.export(chunk_path, format="wav")
    chunks.append(chunk_path)

  return chunks


def process_input(source: str) -> list | str:
  if source.startswith("http://") or source.startswith("https://"):
    try:
      print("Detected YouTube URL. Downloading audio...")
      wav_path = download_youtube_audio(source)
      print("Chunking audio...")
      chunks = chunk_audio(wav_path)
      print(f"Audio ready — {len(chunks)} chunk(s) created.")
      return chunks
    except Exception as e:
      print(f"yt-dlp blocked ({e}). Trying YouTube Transcript fallback...")
      return f"DIRECT_TRANSCRIPT::{fetch_youtube_transcript_fallback(source)}"
  else:
    print("Detected local file. Converting to WAV...")
    wav_path = convert_to_wav(source)
    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks