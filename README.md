# YouTube Summary

[English](README.md) | [中文](README.zh.md)

<p align="center"><b>Paste a YouTube link. Get a clean transcript and a structured summary.</b><br>
<sub>Two Python files, three dependencies, and an optional MCP server. Everything runs on your computer.</sub></p>

<p align="center">
<a href="https://github.com/Jidi1997/youtube-summary/stargazers"><img src="https://img.shields.io/github/stars/Jidi1997/youtube-summary?style=flat-square" alt="GitHub stars"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/Jidi1997/youtube-summary?style=flat-square" alt="MIT license"></a>
</p>

---

YouTube videos carry information that takes time to watch. YouTube Summary extracts the transcript, removes the noise that auto-captions add, and produces a Markdown report you can read in minutes.

It works as a command-line tool or as an MCP server inside AI coding assistants (Cursor, Claude Code, Cline, Windsurf, Antigravity).

## What it does

1. **Gets the transcript.** It tries three sources, in order:
   - Official or auto-generated subtitles, via `youtube-transcript-api`.
   - Subtitle files downloaded by `yt-dlp`.
   - Audio track downloaded by `yt-dlp`, transcribed by Groq Whisper (`whisper-large-v3`).

2. **Cleans the text.** Auto-captions repeat words across overlapping time windows. The cleaner strips WebVTT tags, merges duplicate segments, and joins the result into readable paragraphs.

3. **Writes a summary.** With a Gemini API key, the tool generates a structured Markdown report (executive summary, key takeaways, section breakdown) and runs it through a multi-round quality check. Without a key, it saves the clean transcript and lets your AI assistant write the summary.

## Install

You need Python 3.9 or later and `ffmpeg`.

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg
```

Clone the repository and install the two Python dependencies:

```bash
git clone https://github.com/Jidi1997/youtube-summary.git
cd youtube-summary
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Fill in the keys you have:

```ini
GEMINI_API_KEY=          # optional — enables auto-summary and quality verification
GEMINI_MODEL=gemini-1.5-flash   # optional — default model for summaries (or gemini-2.0-flash)
GROQ_API_KEY=            # optional — enables Whisper ASR for videos without subtitles
```

Leave a key empty to skip that feature. The tool still works with no keys at all.

## Use

### Command line

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

The cleaned transcript goes to `storage/transcripts/`. The summary goes to `storage/metadata/`.

### MCP server (AI assistant integration)

Add this block to your assistant's MCP settings:

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": ["/absolute/path/to/youtube-summary/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

Then ask in chat: *"Summarize this video: https://www.youtube.com/watch?v=..."* — the assistant calls the tool and shows the report.

See [AGENT_INTEGRATION.md](AGENT_INTEGRATION.md) for the full setup guide.

## Two modes

| Mode | When | What happens |
|---|---|---|
| **API mode** | `GEMINI_API_KEY` is set | The tool generates the summary, scores it for accuracy and completeness, and revises it up to three times. |
| **Agent-cooperative mode** | No key | The tool extracts and cleans the transcript only. Your AI assistant reads it and writes the summary in chat. |

## Repository structure

```text
youtube-summary/
├── main.py               # CLI entry point
├── downloader.py          # Subtitle and audio extraction
├── cleaner.py             # Text deduplication and paragraph formatting
├── summarizer.py          # Gemini-based summary generation
├── verifier.py            # Multi-round quality scoring
├── mcp_server.py          # MCP server (JSON-RPC over stdio)
├── config.py              # Paths and environment loading
├── requirements.txt       # yt-dlp, youtube-transcript-api
├── .env.example           # Environment variable template
├── AGENT_INTEGRATION.md   # MCP setup guide (English)
└── AGENT_INTEGRATION.zh.md # MCP setup guide (Chinese)
```

## License

MIT
