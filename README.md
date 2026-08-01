# YouTube Summary

[English](README.md) | [中文](README.zh.md)

---

**YouTube Summary** is an automated workflow designed to download YouTube subtitles, clean scrolling transcript noise, and generate structured AI summaries. It can run as a standalone command-line tool or integrate seamlessly into AI coding assistants (Cursor, Claude Code, Cline, Windsurf) via the Model Context Protocol (MCP).

---

### ✨ Key Features & Under the Hood

- **Adaptive Transcript Extraction**:
  - **Subtitle First**: Downloads official or auto-generated subtitle tracks using `youtube-transcript-api` and `yt-dlp`.
  - **Audio & Whisper Fallback**: If subtitles are missing, downloads the video's audio track in `.m4a` format via `yt-dlp` and transcribes it using Groq Cloud's Whisper API (`whisper-large-v3`).
- **Smart Text Clean & Deduplication**: Parses WebVTT/SRT tags and automatically merges overlapping/scrolling sentences from live/auto-captions into clean, readable paragraphs.
- **AI Summary & Multi-Stage Review**: Generates structured Markdown reports (Executive Summary, Key Takeaways, Section Breakdown) and iterates through an automated quality review loop for accuracy.
- **Flexible Execution Modes**:
  - **API Mode**: Automatically requests Gemini API for structured summary generation and quality validation.
  - **Agent-Cooperative Mode**: Cleans transcripts locally, allowing your AI assistant to generate summaries directly in the chat without API keys.

---

### 📁 Repository Structure

```text
youtube_processor/
├── config.py             # System configuration and directory setup
├── downloader.py         # Subtitle extraction and metadata fetching
├── cleaner.py            # Transcript deduplication and paragraph formatting
├── summarizer.py         # AI summary generation engine
├── verifier.py           # Output quality verification layer
├── main.py               # Command-line interface entrypoint
├── mcp_server.py         # Model Context Protocol (MCP) server
├── requirements.txt      # Project dependencies
├── AGENT_INTEGRATION.md  # AI Agent integration guide
└── .env.example          # Environment configuration template
```

---

### 🛠️ Getting Started

#### 1. System Requirements
This tool requires `ffmpeg` for media handling.
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`

#### 2. Installation
```bash
pip install -r requirements.txt
```

#### 3. Configuration
Copy `.env.example` to `.env` and set your API key:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

---

### 💻 Usage

#### Command Line Interface (CLI)
Process one or multiple YouTube URLs:
```bash
python main.py "https://www.youtube.com/watch?v=PDZf7EiKwyw"
```

- **Cleaned Transcript**: Saved to `storage/transcripts/`
- **Summary Report**: Saved to `storage/metadata/`

#### AI Assistant Integration (MCP)
Add `mcp_server.py` to your AI Assistant's MCP configuration:

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/absolute/path/to/youtube_processor/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

For detailed agent setup instructions, see [**AGENT_INTEGRATION.md**](AGENT_INTEGRATION.md).

---

## License

This project is open-source under the [MIT License](LICENSE).
