from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, g, abort, current_app
from app.embeddings import get_text_embedding, get_emotion_embedding, get_topic_embedding
from app.vector_db import search_stories, is_using_fallback
from app.models import (
    get_story, log_search, get_all_stories, get_story_chapters,
    get_next_chapter_number, add_chapter, append_story_text, update_story_status
)
import re
from app.utils.text_cleaner import extract_summary
from app.utils.tts import synthesize_text_to_speech
import config
from app.routes.auth_routes import login_required

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_page():
    return render_template('search.html')

@search_bp.route('/api/search', methods=['POST'])
def search_api():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = min(int(data.get('limit', 10)), 50)
        search_type = data.get('search_type', 'text')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        try:
            if search_type == 'emotion':
                query_vector = get_emotion_embedding(query)
            elif search_type == 'topic':
                query_vector = get_topic_embedding(query)
            else:
                query_vector = get_text_embedding(query)
        except Exception as e:
            return jsonify({'error': f'Failed to generate query embedding: {str(e)}'}), 500
        
        results = search_stories(query_vector, limit=limit, vector_name=search_type)

        # If we are running with the in-memory fallback (no qdrant client)
        # or the qdrant search returned no results, perform a simple keyword
        # search over the SQLite stories table so search remains usable.
        if is_using_fallback() or not results:
            # basic keyword scoring: count matches of query words in story_text
            terms = [t for t in re.split(r"\W+", query.lower()) if t]
            all_stories = get_all_stories(limit=1000)

            scored = []
            for s in all_stories:
                text = (s.get('story_text') or '').lower()
                score = 0
                for t in terms:
                    # weight longer terms slightly higher
                    score += text.count(t) * (1 + len(t) / 10.0)
                if score > 0:
                    payload = {
                        'story_id': s.get('id'),
                        'speaker_name': s.get('speaker_name', 'Unknown'),
                        'district': s.get('district', 'Unknown'),
                        'story_text': s.get('story_text', ''),
                        'emotion_tag': s.get('emotion_tag', 'neutral'),
                        'timestamp': s.get('created_at', ''),
                        'file_type': s.get('file_type', 'text')
                    }
                    scored.append((payload, float(score)))

            # sort by score desc and limit
            scored.sort(key=lambda x: x[1], reverse=True)
            scored = scored[:limit]

            # Build results similar to qdrant result objects expected by formatter
            class _R:
                def __init__(self, payload, score):
                    self.payload = payload
                    self.score = score

            results = [ _R(p, s) for (p, s) in scored ]

        formatted_results = []
        for result in results:
            story_data = {
                'story_id': result.payload.get('story_id'),
                'speaker_name': result.payload.get('speaker_name', 'Unknown'),
                'district': result.payload.get('district', 'Unknown'),
                'summary': extract_summary(result.payload.get('story_text', '')),
                'emotion_tag': result.payload.get('emotion_tag', 'neutral'),
                'similarity_score': round(result.score, 3) if isinstance(result.score, (int, float)) else None,
                'timestamp': result.payload.get('timestamp', ''),
                'file_type': result.payload.get('file_type', 'text')
            }
            formatted_results.append(story_data)

        log_search(query, len(formatted_results))

        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@search_bp.route('/story/<story_id>', methods=['GET'])
def story_page(story_id):
    story = get_story(story_id)
    if not story:
        return "Story not found", 404
    chapters = get_story_chapters(story_id)
    if not chapters:
        chapters = [{
            'chapter_number': 1,
            'title': 'Chapter 1',
            'content': story.get('story_text', ''),
            'created_at': story.get('created_at', '')
        }]
    is_owner = bool(g.user and g.user.get('id') == story.get('user_id'))
    status = story.get('status') or 'in_progress'
    story['status'] = status
    return render_template('story_page.html', story=story, chapters=chapters, is_owner=is_owner)

@search_bp.route('/story/<story_id>/chapters', methods=['POST'])
@login_required
def add_story_chapter(story_id):
    story = get_story(story_id)
    if not story:
        return "Story not found", 404
    user_id = session.get('user_id')
    if not user_id or story.get('user_id') != user_id:
        abort(404)

    chapter_title = request.form.get('chapter_title', '').strip()
    chapter_content = request.form.get('chapter_content', '').strip()
    generate_tts = request.form.get('generate_tts') in ('1', 'true', 'on')
    if not chapter_content:
        return "Chapter content is required", 400

    chapter_number = get_next_chapter_number(story_id)
    if not chapter_title:
        chapter_title = f"Chapter {chapter_number}"

    chapter_tts_filename = None
    if generate_tts:
        try:
            tts_filename = f"{story_id}_ch{chapter_number}_tts.mp3"
            tts_path = config.UPLOAD_FOLDER / tts_filename
            config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            ok = synthesize_text_to_speech(chapter_content, str(tts_path))
            if ok:
                chapter_tts_filename = tts_filename
        except Exception as e:
            current_app.logger.warning(f"Chapter TTS generation failed for {story_id}: {e}")

    add_chapter(story_id, chapter_number, chapter_title, chapter_content, chapter_tts_filename)
    append_story_text(story_id, chapter_number, chapter_title, chapter_content)

    new_status = request.form.get('story_status', '').strip().lower()
    if new_status in ('in_progress', 'completed'):
        update_story_status(story_id, new_status)

    return redirect(url_for('search.story_page', story_id=story_id))

@search_bp.route('/story/<story_id>/status', methods=['POST'])
@login_required
def update_story_status_route(story_id):
    story = get_story(story_id)
    if not story:
        return "Story not found", 404
    user_id = session.get('user_id')
    if not user_id or story.get('user_id') != user_id:
        abort(404)

    new_status = request.form.get('status', '').strip().lower()
    if new_status not in ('in_progress', 'completed'):
        return "Invalid status", 400
    update_story_status(story_id, new_status)
    return redirect(url_for('search.story_page', story_id=story_id))

@search_bp.route('/api/story/<story_id>', methods=['GET'])
def get_story_api(story_id):
    try:
        story = get_story(story_id)
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        return jsonify({
            'success': True,
            'story': story
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch story: {str(e)}'}), 500
