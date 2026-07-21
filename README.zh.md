# Agentic YouTube Summary (YouTube 视频字幕与 AI 摘要管线)

[English](README.md) | [中文](README.zh.md)

---

**Agentic YouTube Summary** 是一个专为高效获取视频信息设计的自动化工作流工具。它可以自动抓取 YouTube 视频字幕、智能清洗滚动字幕的重复噪声，并生成结构清晰的 AI 内容摘要。

本工具既可以作为独立的命令行工具使用，也可以通过 MCP (Model Context Protocol) 协议无缝集成到 AI 编程助手（如 **Cursor**、**Claude Code**、**Cline**、**Windsurf** 及 **Claude Desktop**）中，让用户直接在聊天框里通过自然语言对话完成视频摘要。

---

### 🌟 适用场景与主要作用

- **长视频快速精读**：无需完整观看数小时的教程、技术演讲、学术讲座或播客，几秒钟内即可提取核心观点与结构化大纲。
- **多语言视频阅读**：支持中英文 YouTube 视频的自动识别与提取，生成匹配语种的高质量总结。
- **对话式智能体交互**：嵌入 AI 编程助手后，只需在聊天框发送类似 *“帮我总结这个视频：<链接>”*，即可在工作区内获取完整总结。

---

### ✨ 核心功能

- **字幕自动提取**：优先下载视频内置或自动生成的字幕轨，具备完善的异常回退机制。
- **文本智能去重清洗**：去除 WebVTT/SRT 标签，并自动过滤自动字幕中的滑动重叠重复文本，排版为人类易读的段落。
- **结构化 Markdown 报告**：自动生成包含“一句话总结”、“核心要点”与“分章节大纲拆解”的完整 Markdown 报告。
- **双层自我修正质检**：从准确性、完整度与精炼度维度对草稿进行评估打分，确保输出质量稳定可靠。
- **灵活的运行模式**：
  - **API 模式**：配置 API 密钥后，自动调用 Gemini 进行摘要生成与质检。
  - **智能体协同模式**：未配置 API 密钥时，自动提取并清洗字幕，交由当前的 AI 编程助手在对话框中免费生成总结。

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
