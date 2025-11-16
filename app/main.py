import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import config
from app.models import init_db, get_all_stories
from app.vector_db import init_qdrant, get_collection_info
from app.routes.upload_routes import upload_bp
from app.routes.search_routes import search_bp

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

CORS(app)

app.register_blueprint(upload_bp)
app.register_blueprint(search_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    try:
        stories = get_all_stories(limit=50)
        qdrant_info = get_collection_info()
        
        return render_template('admin.html', 
                             stories=stories, 
                             qdrant_info=qdrant_info,
                             total_stories=len(stories))
    except Exception as e:
        return f"Admin panel error: {str(e)}", 500

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'qdrant': 'initialized'
    }), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

def create_app():
    init_db()
    init_qdrant()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
