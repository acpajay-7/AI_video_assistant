🎬 AI Video Assistant · Meeting & Video Intelligence SystemAn end-to-end AI pipeline built with LangChain, OpenAI Whisper, Sarvam AI, ChromaDB, and Streamlit. The application ingests YouTube URLs or local audio/video files, transcribes English or Hinglish speech, generates structured executive insights, and provides a Retrieval-Augmented Generation (RAG) chat interface grounded strictly in the video transcript.📌 Table of ContentsSystem Architecture & Pipeline FlowKey FeaturesTech StackProject StructureInstallation & SetupEnvironment Configuration (.env)Running the ApplicationTroubleshooting🚀 System Architecture & Pipeline Flow  ┌──────────────────────────────────────────┐
  │  Input: YouTube URL or Local Audio/Video │
  └────────────────────┬─────────────────────┘
                       │
                       ▼
  [1. Audio Processor] ──(yt-dlp + pydub)───► 16 kHz Mono WAV + 10-min Chunks
                       │
                       ▼
  [2. Transcriber] ──────(Whisper / Sarvam)─► Unified English Transcript
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
  [3. Summarizer] [4. Extractor] [5. Vector Store]
  (Map-Reduce)    (Actions,      (ChromaDB +
   & Title         Decisions,     MiniLM-L6-v2)
                   Questions)          │
                                       ▼
                             [6. RAG Chat Engine]
                             (Grounded Q&A UI/CLI)
✨ Key FeaturesMulti-Source Audio Ingestion (utils/audio_processor.py): Automatically downloads audio from YouTube links via yt-dlp or converts local media files using pydub, normalizing audio to 16 kHz mono WAV and slicing it into 10-minute chunks.Dual-Engine Transcription (core/transcriber.py):English Mode: Uses local OpenAI Whisper (small by default) for accurate offline transcription.Hinglish Mode: Slices audio into $\le 25\text{s}$ segments and routes them through Sarvam AI's speech-to-text translation API to produce clean English transcripts.Map-Reduce Summarization & Title Generation (core/summarizer.py): Splits long transcripts into 3,000-character chunks, summarizes each chunk independently, combines them into an executive bullet-point summary, and generates a concise session title.Structured Information Extraction (core/extractor.py): Extracts Action Items (with owners and deadlines), Key Decisions, and Open Questions into numbered lists.Grounded RAG Q&A (core/vector_store.py & core/rag_engine.py): Embeds transcript chunks (500 chars, 50 overlap) using all-MiniLM-L6-v2 into a local ChromaDB vector store, allowing users to ask follow-up questions answered strictly from the transcript context.Dual Interfaces: Includes a custom dark-themed Streamlit web dashboard (app.py) with real-time pipeline status indicators and a standalone CLI (main.py).🛠️ Tech StackOrchestration & LLM Chains: LangChain (langchain, langchain-core, langchain-community, langchain-text-splitters)LLM Inference: Groq (ChatGroq — openai/gpt-oss-20b / llama-3.1-8b-instant) or Google Gemini (ChatGoogleGenerativeAI)Speech-to-Text: OpenAI Whisper (Local) & Sarvam AI API (saaras:v2.5)Vector Database & Embeddings: ChromaDB (langchain-chroma) & HuggingFace all-MiniLM-L6-v2 (sentence-transformers)Media Processing: yt-dlp, pydub, FFmpegFrontend UI: Streamlit📁 Project StructureAI_video_assistant/
├── app.py                     # Streamlit web interface with live status & RAG chat
├── main.py                    # Standalone CLI pipeline & interactive terminal chat
├── test.py                    # Dry-run test script for transcription & extraction
├── core/
│   ├── transcriber.py         # Whisper & Sarvam AI transcription router
│   ├── summarizer.py          # Map-Reduce summarizer & title generator
│   ├── extractor.py           # Action items, decisions & questions extractor
│   ├── vector_store.py        # ChromaDB builder, loader & similarity retriever
│   └── rag_engine.py          # LCEL Retrieval-Augmented Generation chain
├── utils/
│   └── audio_processor.py     # YouTube downloader, WAV converter & audio chunker
├── requirements.txt           # Project dependencies
├── .env                       # API keys & model settings (excluded from Git)
└── README.md                  # Project documentation
⚙️ Installation & SetupPrerequisitesPython 3.12+FFmpeg installed and available in your system PATH (required by yt-dlp, pydub, and whisper).1. Clone the Repositorygit clone https://github.com/acpajay-7/AI_video_assistant.git
cd AI_video_assistant
2. Create Virtual Environment & Install DependenciesUsing uv:uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
Using standard pip:python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
🔑 Environment Configuration (.env)Create a .env file in the root directory (AI_video_assistant/.env):# ── Required: LLM Provider API Key (Groq or Google Gemini) ──
GROQ_API_KEY=gsk_your_groq_api_key_here
# GOOGLE_API_KEY=AIzaSy_your_gemini_api_key_here

# ── Required for Hinglish Transcription: Sarvam AI ──
SARVAM_API_KEY=your_sarvam_api_key_here

# ── Optional Model Overrides ──
WHISPER_MODEL=small
SARVAM_STT_MODEL=saaras:v2.5
🖥️ Running the ApplicationOption 1: Streamlit Web Dashboard (Recommended)uv run --no-project streamlit run app.py
Open http://localhost:8501 in your browser.Paste a YouTube URL or local file path in the sidebar.Choose english or hinglish and click ⚡ Analyse.Review the generated summary, action items, decisions, and chat with the video transcript.Option 2: Command-Line Interface (CLI)uv run --no-project main.py
Follow the terminal prompts to enter a media source, choose a language, view extracted insights, and ask questions in the interactive CLI chat loop.🔧 TroubleshootingRuntimeError: Expected one of cpu, cuda... device string: gpu: PyTorch requires "cpu" or "cuda" rather than "gpu". Ensure model_kwargs={"device": "cpu"} is set inside core/vector_store.py.yt-dlp FFmpeg Errors: Verify FFmpeg is installed by running ffmpeg -version in your terminal.Streamlit Cloud Deployment: Add GROQ_API_KEY (or GOOGLE_API_KEY) and SARVAM_API_KEY under App Settings → Secrets in TOML format.📄 LicenseThis project is open-source and available under the MIT License.