import os
import json
import urllib.request
import urllib.error
import config

class APIKeyMissingError(Exception):
    pass

def call_gemini_rest_api(prompt, system_instruction=None, model_name=None, api_key=None):
    api_key = api_key or config.GEMINI_API_KEY
    if not api_key:
        raise APIKeyMissingError(
            "GEMINI_API_KEY is missing. Please add GEMINI_API_KEY=your_key in your .env file."
        )
        
    model_name = model_name or config.GEMINI_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""
    except urllib.error.HTTPError as e:
        error_text = e.read().decode('utf-8') if e.fp else str(e)
        raise RuntimeError(f"Gemini API HTTP Error {e.code}: {error_text}")
    except Exception as e:
        raise RuntimeError(f"Error calling Gemini REST API: {str(e)}")

def generate_summary_draft(metadata, transcript_text, feedback_report=None):
    title = metadata.get("title", "Unknown Title")
    channel = metadata.get("channel", "Unknown Channel")
    url = metadata.get("webpage_url", "")
    duration_sec = metadata.get("duration", 0)
    video_id = metadata.get("id", "")
    
    if duration_sec:
        hours = duration_sec // 3600
        minutes = (duration_sec % 3600) // 60
        seconds = duration_sec % 60
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
    else:
        duration_str = "Unknown"

    language = metadata.get("language", "")
    if not language and video_id:
        meta_path = os.path.join(config.METADATA_DIR, f"{video_id}_meta.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    meta_disk = json.load(f)
                    language = meta_disk.get("language", "")
            except Exception:
                pass
                
    import re
    if not language or language in ("auto", "unknown"):
        if re.search(r'[\u4e00-\u9fff]', transcript_text):
            language = "zh"
        else:
            language = "en"

    is_english = language.lower().startswith("en")
    
    if is_english:
        system_instruction = (
            "You are a video content analyst. Generate a structured, concise Markdown summary from the transcript. "
            "Remove filler words and sponsor messages."
        )
        prompt = f"""
Please generate a formatted Markdown summary for this video.

【Video Info】
- Title: {title}
- Channel: {channel}
- URL: {url}
- Duration: {duration_str}

【Transcript】
{transcript_text}

【Output Format】
# 🎬 Video Summary: {title}

## 📌 One-Sentence Summary
[Summary]

## 💡 Key Takeaways
- **Takeaway 1**: [Description]
- **Takeaway 2**: [Description]
- **Takeaway 3**: [Description]

## 📖 Outline & Detailed Breakdown
### 1. [Section 1]
- **Core Idea**: [Summary]
- **Details**: [Bullet points]
"""
        if feedback_report:
            prompt += f"\n\n【Revision Request Feedback】:\n{feedback_report}"
    else:
        system_instruction = (
            "你是一个专业的视频内容分析师。根据视频字幕生成结构清晰、排版精美的 Markdown 格式视频概括。"
            "剔除口水话和广告，精炼核心事实。"
        )
        prompt = f"""
请为以下视频生成 Markdown 总结。

【视频信息】
- 视频名称：{title}
- 频道：{channel}
- 链接：{url}
- 时长：{duration_str}

【原始字幕】
{transcript_text}

【格式要求】
# 🎬 视频总结：{title}

## 📌 一句话总结
[精炼概括]

## 💡 核心要点
- **要点一**：[说明]
- **要点二**：[说明]
- **要点三**：[说明]

## 📖 内容大纲与细节拆解
### 1. [主题板块一]
- **核心观点**：[中心思想]
- **细节展开**：[无序列表记录关键事实]
"""
        if feedback_report:
            prompt += f"\n\n【修改意见】:\n{feedback_report}"

    print(f"Calling Gemini REST API ({config.GEMINI_MODEL}) via zero-SDK urllib...")
    return call_gemini_rest_api(prompt, system_instruction=system_instruction)

def save_summary(summary_content, video_id):
    output_path = os.path.join(config.SUMMARY_DIR, f"{video_id}_summary.md")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    print(f"Saved summary to {output_path}")
    return output_path
