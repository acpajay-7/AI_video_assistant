import os
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
      "extractor_args": {
          "youtube": {"player_client": ["android", "web"]},
      },
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
  audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz mono
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


def process_input(source: str) -> list:
  if source.startswith("http://") or source.startswith("https://"):
    print("Detected YouTube URL. Downloading audio...")
    wav_path = download_youtube_audio(source)
  else:
    print("Detected local file. Converting to WAV...")
    wav_path = convert_to_wav(source)

  print("Chunking audio...")
  chunks = chunk_audio(wav_path)
  print(f"Audio ready — {len(chunks)} chunk(s) created.")
  return chunks