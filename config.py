import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / '.env')

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
DATABASE_PATH = BASE_DIR / 'stories.db'

QDRANT_URL = os.getenv('QDRANT_URL', None)
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', None)
QDRANT_USE_MEMORY = os.getenv('QDRANT_USE_MEMORY', 'false').lower() == 'true'

COLLECTION_NAME = 'stories_memory'
VECTOR_SIZE = 384

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024

SECRET_KEY = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY',"")

# Admin access control
ADMIN_USERNAMES = {u.strip().lower() for u in os.getenv('ADMIN_USERNAMES', '').split(',') if u.strip()}
ADMIN_EMAILS = {e.strip().lower() for e in os.getenv('ADMIN_EMAILS', '').split(',') if e.strip()}
ADMIN_USER_IDS = {i.strip() for i in os.getenv('ADMIN_USER_IDS', '').split(',') if i.strip()}
ADMIN_ROUTE = os.getenv('ADMIN_ROUTE', 'admin')

# Default admin credentials (override via env in production)
ADMIN_DEFAULT_USERNAME = os.getenv('ADMIN_DEFAULT_USERNAME', 'admin').strip()
ADMIN_DEFAULT_PASSWORD = os.getenv('ADMIN_DEFAULT_PASSWORD', 'nancy2007')
ADMIN_DEFAULT_EMAIL = os.getenv('ADMIN_DEFAULT_EMAIL', 'admin@local').strip().lower()

if ADMIN_DEFAULT_USERNAME:
    ADMIN_USERNAMES.add(ADMIN_DEFAULT_USERNAME.lower())
