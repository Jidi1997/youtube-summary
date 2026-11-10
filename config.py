import os

def load_dotenv():
    base = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(base, '.env'),
        os.path.abspath(os.path.join(base, '..', 'Opinion_Digest', '.env')),
        os.path.abspath(os.path.join(base, '..', 'v2_wiki_rag', '.env')),
        os.path.abspath(os.path.join(base, '..', '.env')),
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, val = line.split('=', 1)
                        k = key.strip()
                        v = val.strip().strip('"').strip("'")
                        if k not in os.environ or not os.environ[k]:
                            os.environ[k] = v

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
METADATA_DIR = os.path.join(STORAGE_DIR, 'metadata')
TRANSCRIPT_DIR = os.path.join(STORAGE_DIR, 'transcripts')
SUMMARY_DIR = METADATA_DIR

for path in [METADATA_DIR, TRANSCRIPT_DIR, SUMMARY_DIR]:
    os.makedirs(path, exist_ok=True)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
