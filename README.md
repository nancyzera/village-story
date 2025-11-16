# Memory of the Village

A full-stack web application for preserving and discovering village stories through semantic search powered by vector embeddings.

## Features

- **Upload Stories**: Share memories via voice recordings or written text
- **Audio Transcription**: Automatic transcription using OpenAI Whisper
- **Semantic Search**: Find stories by meaning, not just keywords
- **Emotion Detection**: AI-powered emotion tagging
- **Vector Storage**: Stories stored as embeddings in Qdrant vector database
- **Beautiful UI**: Clean, responsive design with TailwindCSS

## Tech Stack

- **Backend**: Python Flask
- **Vector Database**: Qdrant (in-memory mode)
- **Embeddings**: OpenAI text-embedding-3-small
- **Audio Processing**: OpenAI Whisper API
- **Frontend**: HTML, TailwindCSS, JavaScript
- **Storage**: SQLite + local file storage

## Setup

### Prerequisites

- Python 3.11
- OpenAI API key

### Configuration

The application requires an OpenAI API key for:
- Audio transcription (Whisper)
- Text embeddings
- Emotion and topic analysis

Set the `OPENAI_API_KEY` environment variable in your Replit Secrets.

### Installation

Dependencies are managed automatically by Replit. The required packages are:
- flask
- flask-cors
- qdrant-client
- openai
- werkzeug

### Running

The application runs automatically on Replit. Access it at:
- Home: `/`
- Upload: `/upload`
- Search: `/search`
- Admin: `/admin`

## File Structure

```
/
├── app/
│   ├── main.py              # Flask application
│   ├── models.py            # SQLite database models
│   ├── embeddings.py        # Embedding generation
│   ├── qdrant_client.py     # Vector database operations
│   ├── routes/
│   │   ├── upload_routes.py # Story upload endpoints
│   │   └── search_routes.py # Search endpoints
│   └── utils/
│       ├── audio_to_text.py # Audio transcription
│       └── text_cleaner.py  # Text processing
├── templates/               # HTML templates
├── static/                  # Static assets
├── uploads/                 # Audio file storage
└── config.py               # Configuration

## API Endpoints

### Upload Story
- **POST** `/api/upload`
- Form data: `speaker_name`, `district`, `story_text`, `audio_file`

### Search Stories
- **POST** `/api/search`
- JSON: `{"query": "...", "limit": 10, "search_type": "text"}`

### Get Story
- **GET** `/api/story/<story_id>`

### Health Check
- **GET** `/api/health`

## How It Works

1. User uploads a story (text or audio)
2. Audio is transcribed using Whisper API
3. Text is cleaned and processed
4. Three embeddings are generated:
   - Text embedding (semantic content)
   - Emotion embedding (emotional tone)
   - Topic embedding (main themes)
5. Story metadata saved to SQLite
6. Vectors stored in Qdrant
7. Users can search semantically
8. Results ranked by similarity

## Database Schema

### SQLite (stories.db)
- **stories**: story metadata, transcriptions
- **search_logs**: search analytics

### Qdrant (stories_memory collection)
- Multi-vector storage: text, emotion, topic
- 384-dimensional vectors
- Cosine similarity search

## Notes

- Qdrant runs in memory mode by default
- Audio files stored locally in `/uploads`
- Max file size: 50MB
- Supported audio: MP3, WAV, OGG, M4A, FLAC

## License

This project preserves community memories for future generations.
