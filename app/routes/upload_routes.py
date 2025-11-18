from flask import Blueprint, request, jsonify, render_template, current_app, url_for, session
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from pathlib import Path

import config
from app.models import save_story_with_user
from app.embeddings import get_text_embedding, get_emotion_embedding, get_topic_embedding, detect_emotion
from app.vector_db import store_story_vectors
from app.utils.audio_to_text import transcribe_audio, is_audio_file
from app.utils.text_cleaner import clean_text
from app.utils.tts import synthesize_text_to_speech
from app.routes.auth_routes import login_required

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET'])
@login_required
def upload_page():
    return render_template('upload.html')

@upload_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_story():
    try:
        # Get user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        speaker_name = request.form.get('speaker_name', '').strip()
        district = request.form.get('district', '').strip()
        story_text = request.form.get('story_text', '').strip()
        
        if not speaker_name:
            return jsonify({'error': 'Speaker name is required'}), 400
        
        story_id = str(uuid.uuid4())
        audio_filename = None
        transcription_text = None
        cover_image_filename = None
        tts_audio_filename = None
        file_type = 'text'
        
        # Handle audio upload (voice -> text)
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
                        # Don't fail the whole upload if transcription fails (e.g., missing API key).
                        # Log the issue and continue saving the story without transcription.
                        current_app.logger.warning(f"Transcription failed for {filename}: {e}")
                        transcription_text = None
                        audio_filename = filename
                        file_type = 'audio'
        
        # Handle cover image upload
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            if cover_file and cover_file.filename:
                # basic allowed-check by extension
                ext = cover_file.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    cover_name = secure_filename(f"{story_id}_cover.{ext}")
                    cover_path = config.UPLOAD_FOLDER / cover_name
                    config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
                    cover_file.save(cover_path)
                    cover_image_filename = cover_name

        # If user requested TTS generation from text
        generate_tts = request.form.get('generate_tts') in ('1', 'true', 'on')

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
        
        save_story_with_user(
            story_id=story_id,
            user_id=user_id,
            speaker_name=speaker_name,
            district=district,
            story_text=story_text,
            transcription_text=transcription_text,
            audio_filename=audio_filename,
            cover_image_filename=cover_image_filename,
            tts_audio_filename=tts_audio_filename,
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
        # After storing story and vectors, optionally generate TTS audio and update the DB
        if generate_tts and story_text:
            try:
                tts_filename = f"{story_id}_tts.mp3"
                tts_path = config.UPLOAD_FOLDER / tts_filename
                ok = synthesize_text_to_speech(story_text, str(tts_path))
                if ok:
                    # update DB record with tts filename
                    from app.models import get_db_connection
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute('UPDATE stories SET tts_audio_filename = ? WHERE id = ?', (tts_filename, story_id))
                    conn.commit()
                    conn.close()
                    tts_audio_filename = tts_filename
            except Exception as e:
                current_app.logger.warning(f"TTS generation failed for {story_id}: {e}")

        return jsonify({
            'success': True,
            'story_id': story_id,
            'emotion_tag': emotion_tag,
            'message': 'Story uploaded successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500
