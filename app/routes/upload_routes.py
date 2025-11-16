from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from pathlib import Path

import config
from app.models import save_story
from app.embeddings import get_text_embedding, get_emotion_embedding, get_topic_embedding, detect_emotion
from app.vector_db import store_story_vectors
from app.utils.audio_to_text import transcribe_audio, is_audio_file
from app.utils.text_cleaner import clean_text

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@upload_bp.route('/api/upload', methods=['POST'])
def upload_story():
    try:
        speaker_name = request.form.get('speaker_name', '').strip()
        district = request.form.get('district', '').strip()
        story_text = request.form.get('story_text', '').strip()
        
        if not speaker_name:
            return jsonify({'error': 'Speaker name is required'}), 400
        
        story_id = str(uuid.uuid4())
        audio_filename = None
        transcription_text = None
        file_type = 'text'
        
        if 'audio_file' in request.files:
            audio_file = request.files['audio_file']
            if audio_file.filename and is_audio_file(audio_file.filename):
                filename = secure_filename(f"{story_id}_{audio_file.filename}")
                audio_path = config.UPLOAD_FOLDER / filename
                config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
                audio_file.save(audio_path)
                
                try:
                    transcription_text = transcribe_audio(str(audio_path))
                    story_text = transcription_text if not story_text else story_text
                    audio_filename = filename
                    file_type = 'audio'
                except Exception as e:
                    return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
        
        if not story_text:
            return jsonify({'error': 'Story text or audio file is required'}), 400
        
        story_text = clean_text(story_text)
        
        emotion_tag = detect_emotion(story_text)
        
        try:
            text_vector = get_text_embedding(story_text)
            emotion_vector = get_emotion_embedding(story_text)
            topic_vector = get_topic_embedding(story_text)
        except Exception as e:
            return jsonify({'error': f'Embedding generation failed: {str(e)}'}), 500
        
        save_story(
            story_id=story_id,
            speaker_name=speaker_name,
            district=district,
            story_text=story_text,
            transcription_text=transcription_text,
            audio_filename=audio_filename,
            emotion_tag=emotion_tag,
            file_type=file_type
        )
        
        metadata = {
            'speaker_name': speaker_name,
            'district': district,
            'story_text': story_text,
            'emotion_tag': emotion_tag,
            'timestamp': datetime.now().isoformat(),
            'file_type': file_type
        }
        
        store_story_vectors(story_id, text_vector, emotion_vector, topic_vector, metadata)
        
        return jsonify({
            'success': True,
            'story_id': story_id,
            'emotion_tag': emotion_tag,
            'message': 'Story uploaded successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
