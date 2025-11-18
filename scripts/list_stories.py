import sqlite3
import config
from pathlib import Path
p = Path(__file__).parent.parent / 'stories.db'
print('DB path from config:', config.DATABASE_PATH)
try:
    conn = sqlite3.connect(str(config.DATABASE_PATH))
    cur = conn.cursor()
    cur.execute('SELECT id, speaker_name, cover_image_filename, story_text, created_at FROM stories ORDER BY created_at DESC')
    rows = cur.fetchall()
    print('stories_count=', len(rows))
    for r in rows:
        print(r[0], r[1], r[2], (r[3] or '')[:120])
    conn.close()
except Exception as e:
    print('DB_ERROR', e)
