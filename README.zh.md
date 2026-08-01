# YouTube Summary (YouTube 视频字幕与 AI 摘要管线)

[English](README.md) | [中文](README.zh.md)

---

**YouTube Summary** 是一个专为高效获取视频信息设计的自动化工作流工具。它可以自动下载 YouTube 视频字幕、智能清洗滚动字幕的重复噪声，并生成结构清晰的 AI 内容摘要。本工具既可以作为独立的命令行工具使用，也可以通过 MCP (Model Context Protocol) 协议无缝集成到 AI 编程助手（如 Cursor、Claude Code、Cline、Windsurf）中。

---

### ✨ 核心功能与工作原理

- **多策略音频/字幕提取**：
  - **字幕优先**：优先通过 `youtube-transcript-api` 与 `yt-dlp` 获取官方或自动生成的字幕。
  - **音频与 Whisper 降级**：若视频无字幕，自动使用 `yt-dlp` 下载 `.m4a` 格式音频轨道，并调用 Groq Cloud Whisper API (`whisper-large-v3`) 进行高精度语音转文字。
- **智能文本去重清洗**：解析 WebVTT/SRT 格式，消除自动字幕中因滑动产生的重合重复字句，智能重组为易读的常规段落。
- **结构化 AI 摘要**：生成包含一句话总结、核心要点与分章节大纲的完整 Markdown 报告。
- **双层自我修正质检**：从准确性、完整度与精炼度维度对草稿进行评估打分，确保输出质量稳定可靠。
- **双模运行机制**：
  - **API 模式**：配置 API 密钥后，自动调用 Gemini API 进行摘要生成与迭代质检。
  - **智能体协同模式**：免 Key 运行，仅在本地提取并清洗字幕后回传，由 AI 助手在对话中免费生成总结。

---

### 📁 项目结构

```text
youtube_processor/
├── config.py             # 系统配置与运行目录管理
├── downloader.py         # 字幕提取与元数据获取
├── cleaner.py            # 字幕文本去重与段落重组
├── summarizer.py         # AI 摘要生成引擎
├── verifier.py           # 摘要质量校验层
├── main.py               # 命令行入口脚本
├── mcp_server.py         # MCP 服务实现
├── requirements.txt      # 项目依赖
├── AGENT_INTEGRATION.zh.md # 智能体集成指南
└── .env.example          # 环境变量配置模板
```

---

### 🛠️ 环境准备与安装

#### 1. 系统依赖
本工具依赖 `ffmpeg` 进行媒体处理。
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`

#### 2. Python 依赖安装
```bash
pip install -r requirements.txt
```

#### 3. 配置文件 (`.env`)
复制 `.env.example` 为 `.env` 并填写 API 密钥：
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

---

### 💻 使用指南

#### 命令行方式 (CLI)
处理单个或多个 YouTube 视频链接：
```bash
python main.py "https://www.youtube.com/watch?v=PDZf7EiKwyw"
```

- **清洗后的文本**：保存至 `storage/transcripts/`
- **总结报告文件**：保存至 `storage/metadata/`

#### 编程助手嵌入集成 (MCP)
在您的 AI 编程助手 MCP 设置中添加 `mcp_server.py`：

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/绝对路径/to/youtube_processor/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "您的API密钥"
      }
    }
  }
}
```

详细接入说明请参阅 [**AGENT_INTEGRATION.zh.md**](AGENT_INTEGRATION.zh.md)。

---

## 开源许可证

本项目遵循 [MIT License](LICENSE) 开源许可证。
