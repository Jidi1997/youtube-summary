# YouTube Summary

[English](README.md) | [中文](README.zh.md)

<p align="center"><b>粘贴一条 YouTube 链接，获取干净的逐字稿和结构化摘要。</b><br>
<sub>两个 Python 文件，三个依赖，外加一个可选的 MCP 服务。全部在本地运行。</sub></p>

<p align="center">
<a href="https://github.com/Jidi1997/youtube-summary/stargazers"><img src="https://img.shields.io/github/stars/Jidi1997/youtube-summary?style=flat-square" alt="GitHub stars"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/Jidi1997/youtube-summary?style=flat-square" alt="MIT license"></a>
</p>

---

看视频很花时间。YouTube Summary 帮你提取字幕、清除自动字幕的重复噪声，然后生成一份几分钟就能读完的 Markdown 报告。

它既可以作为命令行工具使用，也可以作为 MCP 服务接入 AI 编程助手（Cursor、Claude Code、Cline、Windsurf、Antigravity）。

## 工作流程

1. **提取字幕。** 按以下顺序依次尝试三种来源：
   - 通过 `youtube-transcript-api` 获取官方或自动生成的字幕。
   - 通过 `yt-dlp` 下载字幕文件。
   - 通过 `yt-dlp` 下载音频轨道，再调用 Groq Whisper (`whisper-large-v3`) 转写为文字。

2. **清洗文本。** 自动字幕会在重叠的时间窗口中产生大量重复片段。清洗器去除 WebVTT 标签，合并重复段落，输出连贯可读的正文。

3. **生成摘要。** 配置了 Gemini API Key 后，工具自动生成结构化 Markdown 报告（核心概要、要点提炼、分章节大纲），并执行多轮质量评估。未配置 Key 时，工具保存清洗后的逐字稿，由你的 AI 助手在对话中完成总结。

## 安装

需要 Python 3.9 及以上版本和 `ffmpeg`。

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg
```

克隆仓库并安装依赖：

```bash
git clone https://github.com/Jidi1997/youtube-summary.git
cd youtube-summary
pip install -r requirements.txt
```

将 `.env.example` 复制为 `.env`，按需填写：

```ini
GEMINI_API_KEY=          # 可选 — 启用自动摘要与质量校验
GEMINI_MODEL=gemini-1.5-flash   # 可选 — 摘要使用的模型（或 gemini-2.0-flash）
GROQ_API_KEY=            # 可选 — 为无字幕视频启用 Whisper 语音转写
```

留空即跳过对应功能。不填任何 Key 也能正常运行。

## 使用

### 命令行

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

清洗后的逐字稿保存在 `storage/transcripts/`，摘要保存在 `storage/metadata/`。

### MCP 服务（AI 助手集成）

在你的 AI 编程助手 MCP 设置中添加：

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": ["/你的绝对路径/youtube-summary/mcp_server.py"],
      "env": {
        "GEMINI_API_KEY": "你的密钥"
      }
    }
  }
}
```

然后在对话框中直接说：*"帮我总结这个视频：https://www.youtube.com/watch?v=..."* — 助手会自动调用工具并展示报告。

完整接入指南请参阅 [AGENT_INTEGRATION.zh.md](AGENT_INTEGRATION.zh.md)。

## 双模运行

| 模式 | 条件 | 行为 |
|---|---|---|
| **API 模式** | 配置了 `GEMINI_API_KEY` | 自动生成摘要，从准确性和完整度两个维度评分，最多修订三轮。 |
| **智能体协同模式** | 未配置 Key | 仅提取并清洗逐字稿。由你的 AI 助手读取文本并在对话中生成总结。 |

## 项目结构

```text
youtube-summary/
├── main.py               # 命令行入口
├── downloader.py          # 字幕与音频提取
├── cleaner.py             # 文本去重与段落格式化
├── summarizer.py          # 基于 Gemini 的摘要生成
├── verifier.py            # 多轮质量评分
├── mcp_server.py          # MCP 服务（JSON-RPC over stdio）
├── config.py              # 路径与环境变量加载
├── requirements.txt       # yt-dlp, youtube-transcript-api
├── .env.example           # 环境变量模板
├── AGENT_INTEGRATION.md   # MCP 接入指南（英文）
└── AGENT_INTEGRATION.zh.md # MCP 接入指南（中文）
```

## 开源许可

MIT
