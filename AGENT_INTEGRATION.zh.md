# AI 智能体 MCP 集成指南

本指南介绍如何将 **Agentic YouTube Summary** 作为 MCP (Model Context Protocol) 工具接入主流 AI 编程助手（如 **Cursor**、**Claude Code**、**Cline**、**Windsurf** 及 **Claude Desktop**）。

接入后，您只需在聊天框中使用自然语言（例如：“*帮我总结这个视频：https://www.youtube.com/watch?v=PDZf7EiKwyw*”），编程助手就会自动调用后台服务完成处理并展示结构化报告。

---

### 1. 一键 MCP 配置

在您的 AI 编程助手 MCP 设置中，添加以下 JSON 配置：

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/绝对路径/to/youtube_processor/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "您的Gemini_API密钥"
      }
    }
  }
}
```

> [!NOTE]
> 请将 `/绝对路径/to/youtube_processor` 替换为您本地解压/克隆该仓库的真实绝对路径。

---

### 2. 双模运行机制

1. **API 自动化模式（带 Key）**：
   - 当配置了 `GEMINI_API_KEY` 时，服务通过 API 自动完成视频处理与质量打分，直接在对话框中输出完成的 Markdown 总结。
2. **智能体协同模式（无 Key 零配置）**：
   - 若未填写 `GEMINI_API_KEY`，程序自动完成字幕抓取与文本去重，并将干净文本直接回传给当前的 AI 编程助手，由助手在对话框中为您生成总结。

---

### 3. 工具声明规范 (JSON Schema)

若需在自定义插件中手动声明工具字段：

```json
{
  "name": "youtube_transcript_summarizer",
  "description": "下载 YouTube 字幕，清洗滚动重复文本，并为一个或多个视频链接生成结构化摘要。",
  "parameters": {
    "type": "object",
    "properties": {
      "urls": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "YouTube 视频 URL 或 ID 列表。"
      }
    },
    "required": ["urls"]
  }
}
```

---

### 4. 智能体系统提示词建议 (System Prompt)

您可以将以下提示词添加到编程助手的 Custom Instructions 中：

```text
你拥有调用 `youtube_transcript_summarizer` 工具的能力。
当用户请求总结或分析一个或多个 YouTube 视频时：
1. 从对话中提取视频 URL。
2. 调用工具 `youtube_transcript_summarizer`，传入 `{"urls": ["..."]}`。
3. 将返回的 Markdown 结构化摘要呈现在聊天界面中。
```
