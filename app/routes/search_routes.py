from flask import Blueprint, request, jsonify, render_template
from app.embeddings import get_text_embedding, get_emotion_embedding, get_topic_embedding
from app.vector_db import search_stories
from app.models import get_story, log_search
from app.utils.text_cleaner import extract_summary

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
        
        formatted_results = []
        for result in results:
            story_data = {
                'story_id': result.payload.get('story_id'),
                'speaker_name': result.payload.get('speaker_name', 'Unknown'),
                'district': result.payload.get('district', 'Unknown'),
                'summary': extract_summary(result.payload.get('story_text', '')),
                'emotion_tag': result.payload.get('emotion_tag', 'neutral'),
                'similarity_score': round(result.score, 3),
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
    return render_template('story_page.html', story=story)

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
