import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
import config
from werkzeug.security import generate_password_hash

def get_db_connection():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Ensure default admin user exists (for local/dev)
    if config.ADMIN_DEFAULT_USERNAME and config.ADMIN_DEFAULT_PASSWORD:
        cursor.execute('SELECT id FROM users WHERE username = ?', (config.ADMIN_DEFAULT_USERNAME,))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute('SELECT id FROM users WHERE email = ?', (config.ADMIN_DEFAULT_EMAIL,))
            email_in_use = cursor.fetchone()
            admin_email = config.ADMIN_DEFAULT_EMAIL
            if email_in_use:
                admin_email = f"admin+{uuid.uuid4().hex[:8]}@local"
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                config.ADMIN_DEFAULT_USERNAME,
                admin_email,
                generate_password_hash(config.ADMIN_DEFAULT_PASSWORD)
            ))
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            speaker_name TEXT NOT NULL,
            district TEXT,
            story_text TEXT NOT NULL,
            transcription_text TEXT,
            audio_filename TEXT,
            cover_image_filename TEXT,
            tts_audio_filename TEXT,
            emotion_tag TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'in_progress',
            file_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Add user_id column if it doesn't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE stories ADD COLUMN user_id TEXT')
    except sqlite3.OperationalError:
        pass
    
    # Add cover_image_filename and tts_audio_filename columns if they don't exist
    try:
        cursor.execute('ALTER TABLE stories ADD COLUMN cover_image_filename TEXT')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE stories ADD COLUMN tts_audio_filename TEXT')
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE stories ADD COLUMN status TEXT DEFAULT 'in_progress'")
    except sqlite3.OperationalError:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS story_chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id TEXT NOT NULL,
            chapter_number INTEGER NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            tts_audio_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (story_id) REFERENCES stories(id)
        )
    ''')

    try:
        cursor.execute("ALTER TABLE story_chapters ADD COLUMN tts_audio_filename TEXT")
    except sqlite3.OperationalError:
        pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            results_count INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_story(story_id, speaker_name, district, story_text, transcription_text=None, 
               audio_filename=None, cover_image_filename=None, tts_audio_filename=None,
               emotion_tag=None, file_type='text', status='in_progress'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO stories (id, speaker_name, district, story_text, transcription_text,
                           audio_filename, cover_image_filename, tts_audio_filename,
                           emotion_tag, status, file_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (story_id, speaker_name, district, story_text, transcription_text,
          audio_filename, cover_image_filename, tts_audio_filename, emotion_tag, status, file_type))
    
    conn.commit()
    conn.close()

def get_story(story_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stories WHERE id = ?', (story_id,))
    story = cursor.fetchone()
    conn.close()
    return dict(story) if story else None

def get_all_stories(limit=100):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stories ORDER BY created_at DESC LIMIT ?', (limit,))
    stories = cursor.fetchall()
    conn.close()
    return [dict(story) for story in stories]

def log_search(query, results_count):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO search_logs (query, results_count) VALUES (?, ?)',
                  (query, results_count))
    conn.commit()
    conn.close()

# User management functions
def create_user(user_id, username, email, password_hash):
    """Create a new user account"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (id, username, email, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, email, password_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_stories(user_id, limit=100):
    """Get all stories for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', 
                   (user_id, limit))
    stories = cursor.fetchall()
    conn.close()
    return [dict(story) for story in stories]

# Update save_story to accept user_id
def save_story_with_user(story_id, user_id, speaker_name, district, story_text, transcription_text=None, 
                         audio_filename=None, cover_image_filename=None, tts_audio_filename=None,
                         emotion_tag=None, file_type='text', status='in_progress'):
    """Save a story with user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO stories (id, user_id, speaker_name, district, story_text, transcription_text,
                           audio_filename, cover_image_filename, tts_audio_filename,
                           emotion_tag, status, file_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (story_id, user_id, speaker_name, district, story_text, transcription_text,
          audio_filename, cover_image_filename, tts_audio_filename, emotion_tag, status, file_type))
    
    conn.commit()
    conn.close()

def get_story_chapters(story_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chapter_number, title, content, tts_audio_filename, created_at
        FROM story_chapters
        WHERE story_id = ?
        ORDER BY chapter_number ASC
    ''', (story_id,))
    chapters = cursor.fetchall()
    conn.close()
    return [dict(ch) for ch in chapters]

def get_next_chapter_number(story_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(chapter_number) AS max_num FROM story_chapters WHERE story_id = ?', (story_id,))
    row = cursor.fetchone()
    conn.close()
    max_num = row['max_num'] if row and row['max_num'] is not None else 0
    return int(max_num) + 1

def add_chapter(story_id, chapter_number, title, content, tts_audio_filename=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO story_chapters (story_id, chapter_number, title, content, tts_audio_filename)
        VALUES (?, ?, ?, ?, ?)
    ''', (story_id, chapter_number, title, content, tts_audio_filename))
    conn.commit()
    conn.close()

def update_story_status(story_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE stories SET status = ? WHERE id = ?', (status, story_id))
    conn.commit()
    conn.close()

def append_story_text(story_id, chapter_number, title, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT story_text FROM stories WHERE id = ?', (story_id,))
    row = cursor.fetchone()
    current = row['story_text'] if row and row['story_text'] else ''
    header = f"Chapter {chapter_number}"
    if title:
        header = f"{header}: {title}"
    addition = f"{header}\n{content}"
    new_text = current + "\n\n" + addition if current else content
    cursor.execute('UPDATE stories SET story_text = ? WHERE id = ?', (new_text, story_id))
    conn.commit()
    conn.close()
