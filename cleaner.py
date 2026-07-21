import os
import re
import config

def clean_vtt_content(vtt_content):
    if not vtt_content or not vtt_content.strip():
        raise ValueError("Empty subtitle file")
        
    def clean_tags(text):
        return re.sub(r'<[^>]+>', '', text).strip()

    lines = vtt_content.split('\n')
    cues = []
    current_cue = []
    in_header = True
    
    for line in lines:
        line = line.strip()
        if in_header:
            if line.startswith('00:') or '-->' in line:
                in_header = False
            else:
                continue
        if '-->' in line:
            if current_cue:
                cues.append(current_cue)
                current_cue = []
            continue
        if line.isdigit() or line == '':
            continue
        cleaned = clean_tags(line)
        if cleaned:
            current_cue.append(cleaned)
            
    if current_cue:
        cues.append(current_cue)
        
    final_sentences = []
    for cue in cues:
        cue_text = " ".join(cue)
        if not final_sentences:
            final_sentences.append(cue_text)
            continue
        last = final_sentences[-1]
        if cue_text == last:
            continue
        if cue_text.startswith(last) or last in cue_text:
            final_sentences[-1] = cue_text
        elif cue_text in last:
            continue
        else:
            overlap_found = False
            words_last = last.split()
            words_curr = cue_text.split()
            max_overlap = min(len(words_last), len(words_curr))
            for i in range(max_overlap, 0, -1):
                if words_last[-i:] == words_curr[:i]:
                    final_sentences[-1] = " ".join(words_last + words_curr[i:])
                    overlap_found = True
                    break
            if not overlap_found:
                max_chars = min(len(last), len(cue_text))
                for i in range(max_chars, 0, -1):
                    if last[-i:] == cue_text[:i]:
                        final_sentences[-1] = last + cue_text[i:]
                        overlap_found = True
                        break
            if not overlap_found:
                final_sentences.append(cue_text)
                
    return "\n".join(final_sentences)

def clean_formatted_transcript(txt_content):
    if not txt_content or not txt_content.strip():
        return ""

    lines = txt_content.split('\n')
    cleaned_sentences = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cleaned_line = re.sub(r'^\[\d+(?:\.\d+)?\]\s*', '', line).strip()
        if cleaned_line:
            cleaned_sentences.append(cleaned_line)
            
    paragraphs = []
    current_paragraph = []
    for sentence in cleaned_sentences:
        current_paragraph.append(sentence)
        is_ending = sentence.endswith(('.', '。', '?', '？', '!', '！'))
        if len(current_paragraph) >= 6 or (len(current_paragraph) >= 3 and is_ending):
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
        
    return "\n\n".join(paragraphs)

def clean_transcript(subtitle_file_path, video_id, is_raw_vtt=True):
    print(f"Cleaning transcript for: {subtitle_file_path}")
    if not os.path.exists(subtitle_file_path):
        raise FileNotFoundError(f"Subtitle file not found at: {subtitle_file_path}")
        
    with open(subtitle_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    if is_raw_vtt:
        cleaned_content = clean_vtt_content(content)
    else:
        cleaned_content = clean_formatted_transcript(content)
        
    cleaned_file_path = os.path.join(config.TRANSCRIPT_DIR, f"{video_id}_transcript.txt")
    with open(cleaned_file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
        
    print(f"Saved cleaned transcript to {cleaned_file_path}")
    return cleaned_file_path
