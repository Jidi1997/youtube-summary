import os
import sys
import re
import config
from downloader import get_video_metadata, download_subtitles, DownloadError, extract_video_id
from cleaner import clean_transcript
from summarizer import generate_summary_draft, save_summary, APIKeyMissingError
from verifier import static_validation, run_llm_evaluation

def process_single_video(url, max_revisions=3):
    print("\n" + "="*60)
    print(f"🚀 Processing video: {url}")
    print("="*60)
    
    video_id = None
    try:
        video_id = extract_video_id(url)
    except Exception:
        pass
        
    try:
        metadata = get_video_metadata(url)
        if metadata and "id" in metadata:
            video_id = metadata["id"]
        title = metadata["title"]
        
        safe_title = metadata.get("safe_title", video_id)
        if len(safe_title) > 50:
            safe_title = safe_title[:50].rstrip("_")
            
        file_prefix = safe_title
        subtitle_path, is_raw_vtt = download_subtitles(url, video_id)
        cleaned_path = clean_transcript(subtitle_path, file_prefix, is_raw_vtt=is_raw_vtt)

        with open(cleaned_path, 'r', encoding='utf-8') as f:
            transcript_text = f.read()
            
        if not transcript_text.strip():
            print(f"❌ Error: Cleaned transcript for '{title}' is empty.")
            return False
            
        print(f"✅ Transcript extracted & cleaned (Length: {len(transcript_text)} chars)")
        print(f"📂 Saved transcript to: {cleaned_path}")
        
        if not config.GEMINI_API_KEY:
            print("\n⚠️ Note: GEMINI_API_KEY is not set.")
            print("💡 Local LLM summarization is skipped. Your AI assistant (Cursor / Claude Code / Antigravity)")
            print("   can summarize the clean transcript file directly!")
            print("-" * 60)
            return True
            
        revision = 0
        feedback = None
        summary_draft = None
        
        while revision <= max_revisions:
            if revision == 0:
                print("📝 Generating initial summary draft (Zero-SDK REST API)...")
            else:
                print(f"🔄 Verification Loop: Revision {revision}/{max_revisions}...")
                
            summary_draft = generate_summary_draft(metadata, transcript_text, feedback_report=feedback)
            is_static_ok, static_err = static_validation(summary_draft)
            if not is_static_ok:
                print(f"⚠️ Static validation failed: {static_err}")
                feedback = f"静态格式校验失败: {static_err}。请重新排版。"
                revision += 1
                continue
                
            passed, scores, eval_feedback, full_report = run_llm_evaluation(metadata, transcript_text, summary_draft)
            print(f"📊 Verification Scores: Accuracy={scores['accuracy']}/10, Completeness={scores['completeness']}/10, Conciseness={scores['conciseness']}/10")
            
            if passed:
                print("🎉 Quality verification passed!")
                break
            else:
                feedback = eval_feedback
                revision += 1
                
        if summary_draft:
            saved_path = save_summary(summary_draft, file_prefix)
            print(f"✨ Success! Final summary saved to: {saved_path}")
            return True
            
    except DownloadError as e:
        print(f"❌ Download Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    return False

def main():
    urls = sys.argv[1:]
    if not urls:
        print("🎥 YouTube Summary 🎥")
        print("Please enter YouTube URL(s):")
        try:
            user_input = input("> ").strip()
            if not user_input:
                return
            urls = [u.strip() for u in re.split(r'[\s,]+', user_input) if u.strip()]
        except (KeyboardInterrupt, EOFError):
            return

    success_count = 0
    for url in urls:
        if process_single_video(url):
            success_count += 1
            
    print("\n" + "="*60)
    print(f"🏁 Processing completed: {success_count}/{len(urls)} videos.")
    print("="*60)

if __name__ == "__main__":
    main()
