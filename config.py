import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
DATABASE_PATH = BASE_DIR / 'stories.db'

QDRANT_HOST = os.getenv('QDRANT_HOST', 'localhost')
QDRANT_PORT = int(os.getenv('QDRANT_PORT', 6333))
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY', None)
QDRANT_USE_MEMORY = os.getenv('QDRANT_USE_MEMORY', 'true').lower() == 'true'

COLLECTION_NAME = 'stories_memory'
VECTOR_SIZE = 384

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
MAX_FILE_SIZE = 50 * 1024 * 1024

SECRET_KEY = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
