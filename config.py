import os

def load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

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
