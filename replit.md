# Memory of the Village - Project Documentation

## Overview
A full-stack web application for preserving and discovering village stories through semantic search. Users can upload voice recordings or text stories, which are transcribed, embedded, and stored for semantic search using vector similarity.

## Current State
- **Status**: Fully functional MVP deployed
- **Last Updated**: November 16, 2025
- **Tech Stack**: Flask, Qdrant (in-memory), OpenAI APIs, SQLite, TailwindCSS

## Project Structure

```
/
├── app/
│   ├── main.py              # Flask application entry point
│   ├── models.py            # SQLite database models and operations
│   ├── embeddings.py        # OpenAI embedding generation
│   ├── vector_db.py         # Qdrant vector database operations
│   ├── routes/
│   │   ├── upload_routes.py # Story upload endpoints
│   │   └── search_routes.py # Search and story retrieval endpoints
│   └── utils/
│       ├── audio_to_text.py # Whisper transcription
│       └── text_cleaner.py  # Text processing utilities
├── templates/               # Jinja2 HTML templates
│   ├── index.html          # Landing page
│   ├── upload.html         # Story upload interface
│   ├── search.html         # Semantic search interface
│   ├── story_page.html     # Individual story display
│   └── admin.html          # Admin dashboard
├── static/                  # Static assets
├── uploads/                 # Audio file storage
├── config.py               # Application configuration
└── README.md               # User documentation
```

## Key Features

1. **Story Upload**
   - Text and audio (MP3, WAV, OGG, M4A, FLAC)
   - Automatic transcription via Whisper API
   - Emotion detection and tagging
   
2. **Vector Embeddings**
   - Text embeddings: OpenAI text-embedding-3-small (384d)
   - Emotion embeddings: Emotional tone analysis
   - Topic embeddings: Theme extraction
   
3. **Semantic Search**
   - Multi-vector search (text, emotion, topic)
   - Similarity scoring and ranking
   - Real-time results
   
4. **Admin Panel**
   - Story archive view
   - Qdrant collection statistics
   - Search analytics

## Architecture Decisions

### Why OpenAI Embeddings Instead of SentenceTransformers?
- **Disk Space**: PyTorch and CUDA dependencies exceeded disk quota
- **Quality**: OpenAI text-embedding-3-small provides excellent embeddings
- **Simplicity**: No model management, automatic updates
- **Cost**: Pay-per-use vs. infrastructure costs

### Why In-Memory Qdrant?
- **Simplicity**: No external database setup needed
- **Development**: Perfect for MVP and testing
- **Migration Path**: Easy to switch to persistent Qdrant later

### File Organization
- Renamed `qdrant_client.py` to `vector_db.py` to avoid naming conflict with the qdrant-client package

## Environment Variables

Required:
- `OPENAI_API_KEY` - For Whisper transcription and embeddings
- `SESSION_SECRET` - Flask session security

Optional:
- `QDRANT_HOST` - Qdrant server host (default: localhost)
- `QDRANT_PORT` - Qdrant port (default: 6333)
- `QDRANT_API_KEY` - For cloud Qdrant
- `QDRANT_USE_MEMORY` - Use in-memory mode (default: true)

## API Endpoints

- `POST /api/upload` - Upload story (text or audio)
- `POST /api/search` - Semantic search
- `GET /api/story/<id>` - Get story details
- `GET /api/health` - Health check

## Recent Changes

### November 16, 2025 - Initial Implementation
- Created complete application structure
- Implemented all backend modules
- Built all frontend templates
- Set up Flask workflow
- Fixed import path issues
- Resolved naming conflicts (qdrant_client → vector_db)
- Application running successfully on port 5000

## Known Limitations

1. **Production Readiness**
   - Using development Flask server (not WSGI)
   - TailwindCSS via CDN (should use build process)
   - In-memory Qdrant (data lost on restart)
   
2. **Scalability**
   - No pagination in admin panel
   - Limited error handling for large files
   - No rate limiting on API endpoints

## Future Enhancements

1. User authentication and personal collections
2. Persistent Qdrant database
3. Advanced filtering (by district, emotion, date)
4. Export functionality
5. Audio playback controls
6. Enhanced emotion detection models
7. Multi-language support

## Development Notes

- Always restart workflow after code changes
- Check logs for errors: `refresh_all_logs`
- Database file: `stories.db` in root
- Audio files: `uploads/` directory
