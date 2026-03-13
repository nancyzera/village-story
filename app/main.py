import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, send_from_directory, abort, g
from flask_cors import CORS
import config
from app.models import init_db, get_all_stories, get_user_by_id
from app.vector_db import init_qdrant, get_collection_info
from app.routes.upload_routes import upload_bp
from app.routes.search_routes import search_bp
from app.routes.auth_routes import auth_bp, admin_required, is_admin_user

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set True for HTTPS in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60  # 7 days
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

CORS(app)

app.register_blueprint(upload_bp)
app.register_blueprint(search_bp)
app.register_blueprint(auth_bp)

# Context processor to make user available to all templates
@app.before_request
def load_user_context():
    """Load user data into g context before each request"""
    from flask import session
    if 'user_id' in session:
        g.user = get_user_by_id(session['user_id'])
    else:
        g.user = None
    g.is_admin = is_admin_user(session)
    g.admin_route = config.ADMIN_ROUTE

# Serve uploaded files from the uploads folder. Using an explicit route keeps
# uploads out of the main static folder and allows OneDrive/workspace paths.
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        # config.UPLOAD_FOLDER is a Path; convert to string for send_from_directory
        return send_from_directory(str(app.config.get('UPLOAD_FOLDER')), filename)
    except Exception:
        abort(404)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings')
def settings():
    return render_template('settings.html',
                         openai_configured=bool(config.OPENAI_API_KEY),
                         qdrant_url=config.QDRANT_URL)

@app.route(f'/{config.ADMIN_ROUTE}')
@admin_required
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

# Ensure DB/Qdrant init for WSGI servers like gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
