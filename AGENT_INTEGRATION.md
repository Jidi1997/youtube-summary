# MCP Integration Guide

This guide shows how to add **YouTube Summary** as an MCP tool in your AI coding assistant.

After setup, ask in chat — *"Summarize this video: https://www.youtube.com/watch?v=..."* — and the assistant calls the tool automatically.

---

## 1. Add the MCP server

Put this block in your assistant's MCP configuration (Cursor, Claude Code, Cline, Windsurf, Claude Desktop, or Antigravity):

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/absolute/path/to/youtube-summary/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your_key_here"
      }
    }
  }
}
```

> [!NOTE]
> Replace `/absolute/path/to/youtube-summary` with the actual path on your computer.

---

## 2. Two modes

| Mode | Condition | Behavior |
|---|---|---|
| **API mode** | `GEMINI_API_KEY` is set | The tool processes the video, scores the summary, and returns the complete Markdown report. |
| **Agent-cooperative mode** | Key is empty | The tool extracts and cleans the transcript. Your assistant reads the clean text and writes the summary in chat. |

---

## 3. Tool schema

Use this schema if your agent framework needs a manual tool declaration:

```json
{
  "name": "youtube_transcript_summarizer",
  "description": "Download YouTube subtitles, clean scrolling text, and generate a structured summary.",
  "parameters": {
    "type": "object",
    "properties": {
      "urls": {
        "type": "array",
        "items": { "type": "string" },
        "description": "One or more YouTube video URLs or IDs."
      }
    },
    "required": ["urls"]
  }
}
```

---

## 4. System prompt snippet

Add this to your assistant's custom instructions:

```text
You have a tool called `youtube_transcript_summarizer`.
When the user asks to summarize one or more YouTube videos:
1. Extract the video URLs from the message.
2. Call `youtube_transcript_summarizer` with {"urls": ["..."]}.
3. Show the Markdown summary to the user.
```
