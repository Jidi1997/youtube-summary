import sys
import os
import json
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
from main import process_single_video
from downloader import extract_video_id, clean_filename

def write_jsonrpc_response(response_dict):
    """Write JSON-RPC message to stdout followed by newline and flush."""
    msg = json.dumps(response_dict, ensure_ascii=False)
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()

def handle_initialize(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "youtube-summary",
                "version": "2.0.0"
            }
        }
    }

def handle_tools_list(req_id):
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "tools": [
                {
                    "name": "youtube_transcript_summarizer",
                    "description": "Downloads YouTube subtitles, cleans repetitive scrolling text, and generates structured summaries for video URLs.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of YouTube video URLs or IDs."
                            }
                        },
                        "required": ["urls"]
                    }
                }
            ]
        }
    }

def handle_tools_call(req_id, params):
    name = params.get("name")
    arguments = params.get("arguments", {})
    
    if name != "youtube_transcript_summarizer":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Unknown tool: '{name}'"
            }
        }
        
    urls = arguments.get("urls", [])
    if not urls:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": "Error: No URLs provided."}]
            }
        }
        
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        results = []
        for url in urls:
            try:
                success = process_single_video(url)
                if success:
                    video_id = extract_video_id(url)
                    meta_path = os.path.join(config.METADATA_DIR, f"{video_id}_meta.json")
                    title = video_id
                    if os.path.exists(meta_path):
                        try:
                            with open(meta_path, 'r', encoding='utf-8') as f:
                                meta = json.load(f)
                                title = meta.get("title", video_id)
                        except Exception:
                            pass
                    
                    safe_title = clean_filename(title)
                    if len(safe_title) > 50:
                        safe_title = safe_title[:50].rstrip("_")
                        
                    summary_file = os.path.join(config.METADATA_DIR, f"{safe_title}_summary.md")
                    if not os.path.exists(summary_file):
                        summary_file = os.path.join(config.METADATA_DIR, f"{video_id}_summary.md")
                        
                    transcript_file = os.path.join(config.TRANSCRIPT_DIR, f"{safe_title}_transcript.txt")
                    if not os.path.exists(transcript_file):
                        transcript_file = os.path.join(config.TRANSCRIPT_DIR, f"{video_id}_transcript.txt")
                    
                    summary_content = ""
                    if os.path.exists(summary_file):
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            summary_content = f.read()
                            
                    results.append({
                        "url": url,
                        "success": True,
                        "title": title,
                        "summary_path": summary_file if os.path.exists(summary_file) else None,
                        "transcript_path": transcript_file if os.path.exists(transcript_file) else None,
                        "summary": summary_content
                    })
                else:
                    results.append({
                        "url": url,
                        "success": False,
                        "error": "Failed to process video."
                    })
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })

        output_payload = json.dumps(results, indent=2, ensure_ascii=False)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": output_payload
                    }
                ]
            }
        }
    finally:
        sys.stdout = old_stdout

def main():
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
                
            data = json.loads(line)
            method = data.get("method")
            req_id = data.get("id")
            params = data.get("params", {})
            
            if method == "initialize":
                write_jsonrpc_response(handle_initialize(req_id))
            elif method == "notifications/initialized":
                pass
            elif method == "tools/list":
                write_jsonrpc_response(handle_tools_list(req_id))
            elif method == "tools/call":
                write_jsonrpc_response(handle_tools_call(req_id, params))
            elif method == "ping":
                write_jsonrpc_response({"jsonrpc": "2.0", "id": req_id, "result": {}})
            else:
                if req_id is not None:
                    write_jsonrpc_response({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    })
        except Exception as e:
            sys.stderr.write(f"MCP Error: {e}\n{traceback.format_exc()}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
