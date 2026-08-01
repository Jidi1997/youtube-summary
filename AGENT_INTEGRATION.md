# AI Agent MCP Integration Guide

This guide explains how to register **YouTube Summary** as an MCP (Model Context Protocol) tool in modern AI coding assistants (such as **Cursor**, **Claude Code**, **Cline**, **Windsurf**, and **Claude Desktop**).

Once configured, you can simply ask your coding assistant in plain chat (e.g. *"Summarize this YouTube video: https://www.youtube.com/watch?v=PDZf7EiKwyw"*), and the agent will automatically execute the tool.

---

### 1. 1-Step MCP Configuration

Add the following block to your agent's MCP configuration settings:

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/absolute/path/to/youtube_processor/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

> [!NOTE]
> Replace `/absolute/path/to/youtube_processor` with the actual local folder path on your computer.

---

### 2. Supported Execution Modes

1. **Automated API Mode (Default with Key)**:
   - When `GEMINI_API_KEY` is provided in `env`, the tool automatically processes the video, evaluates summary quality, and returns the complete Markdown report to your chat interface.
2. **Agent-Cooperative Mode (Zero-Key Setup)**:
   - If `GEMINI_API_KEY` is left empty, the tool extracts and cleans the video transcript, passing the clean text directly to your AI Coding Assistant for in-chat summary generation.

---

### 3. Tool Definition (JSON Schema)

If registering tools manually in custom agent configurations:

```json
{
  "name": "youtube_transcript_summarizer",
  "description": "Downloads YouTube subtitles, cleans scrolling repetitive text, and generates structured summaries for video URLs.",
  "parameters": {
    "type": "object",
    "properties": {
      "urls": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of YouTube video URLs or Video IDs."
      }
    },
    "required": ["urls"]
  }
}
```

---

### 4. System Prompt Guidance for Agents

You can add this snippet to your agent's custom instructions:

```text
You have access to the tool `youtube_transcript_summarizer`.
When the user asks to summarize or extract key points from one or more YouTube URLs:
1. Parse the video URLs from chat.
2. Call `youtube_transcript_summarizer` with `{"urls": ["..."]}`.
3. Present the resulting structured Markdown summary directly to the user.
```
