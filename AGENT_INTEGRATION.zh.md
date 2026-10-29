# MCP 集成指南

本指南介绍如何将 **YouTube Summary** 作为 MCP 工具接入 AI 编程助手。

接入后，在对话框中直接说 *"帮我总结这个视频：https://www.youtube.com/watch?v=..."*，助手会自动调用工具并展示报告。

---

## 1. 添加 MCP 服务

在你的 AI 编程助手 MCP 设置中添加以下配置（Cursor、Claude Code、Cline、Windsurf、Claude Desktop 或 Antigravity 均适用）：

```json
{
  "mcpServers": {
    "youtube-summary": {
      "command": "python3",
      "args": [
        "/你的绝对路径/youtube-summary/mcp_server.py"
      ],
      "env": {
        "GEMINI_API_KEY": "你的密钥"
      }
    }
  }
}
```

> [!NOTE]
> 将 `/你的绝对路径/youtube-summary` 替换为本地实际路径。

---

## 2. 双模运行

| 模式 | 条件 | 行为 |
|---|---|---|
| **API 模式** | 配置了 `GEMINI_API_KEY` | 自动处理视频、评分摘要质量，并返回完整的 Markdown 报告。 |
| **智能体协同模式** | Key 留空 | 仅提取并清洗逐字稿。由你的 AI 助手读取文本并在对话中生成总结。 |

---

## 3. 工具声明

如需手动注册工具，使用以下 JSON Schema：

```json
{
  "name": "youtube_transcript_summarizer",
  "description": "下载 YouTube 字幕，清洗滚动重复文本，生成结构化摘要。",
  "parameters": {
    "type": "object",
    "properties": {
      "urls": {
        "type": "array",
        "items": { "type": "string" },
        "description": "一个或多个 YouTube 视频 URL 或 ID。"
      }
    },
    "required": ["urls"]
  }
}
```

---

## 4. 系统提示词

在编程助手的 Custom Instructions 中添加：

```text
你可以调用 `youtube_transcript_summarizer` 工具。
当用户要求总结一个或多个 YouTube 视频时：
1. 从消息中提取视频 URL。
2. 调用 `youtube_transcript_summarizer`，传入 {"urls": ["..."]}。
3. 将 Markdown 摘要展示给用户。
```
