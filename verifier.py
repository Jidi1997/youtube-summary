import os
import re
import config
from summarizer import call_gemini_rest_api

class VerificationError(Exception):
    pass

def static_validation(summary_text):
    if not summary_text or len(summary_text.strip()) < 100:
        is_english = not bool(re.search(r'[\u4e00-\u9fff]', summary_text or ''))
        if is_english:
            return False, "Summary content is too short (less than 100 characters)."
        return False, "总结字数过少（小于100字），生成可能失败。"
        
    is_english = not bool(re.search(r'[\u4e00-\u9fff]', summary_text))
    
    if is_english:
        required_headers = [
            r"#\s+.*Video Summary",
            r"##\s+.*One-Sentence Summary",
            r"##\s+.*Key Takeaways",
            r"##\s+.*Outline & Detailed Breakdown"
        ]
        fail_msg = "Required header format not detected: '{header_name}'."
    else:
        required_headers = [
            r"#\s+.*视频总结",
            r"##\s+.*一句话总结",
            r"##\s+.*核心要点",
            r"##\s+.*内容大纲与细节拆解"
        ]
        fail_msg = "未检测到规范的标题格式：'{header_name}'。"
    
    for pattern in required_headers:
        if not re.search(pattern, summary_text, re.IGNORECASE):
            header_name = pattern.split(".*")[-1]
            return False, fail_msg.format(header_name=header_name)
            
    return True, ""

def run_llm_evaluation(metadata, transcript_text, summary_draft):
    if not config.GEMINI_API_KEY:
        raise VerificationError("GEMINI_API_KEY is not set.")
        
    title = metadata.get("title", "Unknown Title")
    video_id = metadata.get("id", "")
    
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
                
    if not language or language in ("auto", "unknown"):
        if re.search(r'[\u4e00-\u9fff]', transcript_text):
            language = "zh"
        else:
            language = "en"

    is_english = language.lower().startswith("en")
    
    if is_english:
        prompt = f"""
Evaluate the generated [Summary Draft] against [Raw Transcript].

[Video Title]: {title}

[Raw Transcript]
{transcript_text[:30000]}

[Summary Draft]
{summary_draft}

Grade 1-10 and output decision PASS/FAIL:
[ACCURACY_SCORE]: <score 1-10>
[COMPLETENESS_SCORE]: <score 1-10>
[CONCISENESS_SCORE]: <score 1-10>
[DECISION]: <PASS or FAIL>
[FEEDBACK]:
- <feedback points>
"""
        default_feedback = "Please optimize layout and ensure no omissions."
    else:
        prompt = f"""
请对照【原始字幕】评估生成的【总结草稿】。

【视频名称】: {title}

【原始字幕】
{transcript_text[:30000]}

【总结草稿】
{summary_draft}

请打分（1-10）并给出判定结果（PASS 或 FAIL）：
[ACCURACY_SCORE]: <分数 1-10>
[COMPLETENESS_SCORE]: <分数 1-10>
[CONCISENESS_SCORE]: <分数 1-10>
[DECISION]: <PASS 或 FAIL>
[FEEDBACK]:
- <具体意见>
"""
        default_feedback = "请进一步优化逻辑排版，确保没有遗漏和废话。"
        
    print("Sending draft to Verification Layer via zero-SDK REST API...")
    try:
        eval_report = call_gemini_rest_api(prompt)
        
        accuracy = 0
        completeness = 0
        conciseness = 0
        decision = "FAIL"
        feedback = ""
        
        acc_match = re.search(r"\[ACCURACY_SCORE\]:\s*(\d+)", eval_report)
        comp_match = re.search(r"\[COMPLETENESS_SCORE\]:\s*(\d+)", eval_report)
        con_match = re.search(r"\[CONCISENESS_SCORE\]:\s*(\d+)", eval_report)
        dec_match = re.search(r"\[DECISION\]:\s*(PASS|FAIL)", eval_report, re.IGNORECASE)
        
        if acc_match: accuracy = int(acc_match.group(1))
        if comp_match: completeness = int(comp_match.group(1))
        if con_match: conciseness = int(con_match.group(1))
        if dec_match: decision = dec_match.group(1).upper()
        
        feedback_start = eval_report.find("[FEEDBACK]:")
        if feedback_start != -1:
            feedback = eval_report[feedback_start + len("[FEEDBACK]:"):].strip()
        else:
            feedback = default_feedback
            
        scores = {
            "accuracy": accuracy,
            "completeness": completeness,
            "conciseness": conciseness
        }
        
        is_passed = (decision == "PASS") and (accuracy >= 8) and (completeness >= 8) and (conciseness >= 8)
        return is_passed, scores, feedback, eval_report
        
    except Exception as e:
        raise RuntimeError(f"Error during LLM evaluation in verification layer: {str(e)}")
