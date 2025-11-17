import sqlite3
from datetime import datetime
from pathlib import Path
import config

def get_db_connection():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            speaker_name TEXT NOT NULL,
            district TEXT,
            story_text TEXT NOT NULL,
            transcription_text TEXT,
            audio_filename TEXT,
            cover_image_filename TEXT,
            tts_audio_filename TEXT,
            emotion_tag TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_type TEXT
        )
    ''')
    
    # Add cover_image_filename and tts_audio_filename columns if they don't exist
    try:
        cursor.execute('ALTER TABLE stories ADD COLUMN cover_image_filename TEXT')
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute('ALTER TABLE stories ADD COLUMN tts_audio_filename TEXT')
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
               emotion_tag=None, file_type='text'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO stories (id, speaker_name, district, story_text, transcription_text,
                           audio_filename, cover_image_filename, tts_audio_filename,
                           emotion_tag, file_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (story_id, speaker_name, district, story_text, transcription_text,
          audio_filename, cover_image_filename, tts_audio_filename, emotion_tag, file_type))
    
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
