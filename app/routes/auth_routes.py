from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from app.models import (
    create_user, get_user_by_username, get_user_by_email, 
    get_user_by_id, get_user_stories
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup page and endpoint"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    # POST request - process signup
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        password_confirm = data.get('password_confirm', '').strip()
        
        # Validation
        if not all([username, email, password, password_confirm]):
            error = 'All fields are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        if len(username) < 3:
            error = 'Username must be at least 3 characters'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        if len(password) < 6:
            error = 'Password must be at least 6 characters'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        if password != password_confirm:
            error = 'Passwords do not match'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        # Check if username or email already exists
        if get_user_by_username(username):
            error = 'Username already exists'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        if get_user_by_email(email):
            error = 'Email already exists'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('signup.html', error=error), 400
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        if not create_user(user_id, username, email, password_hash):
            error = 'Failed to create user'
            if request.is_json:
                return jsonify({'error': error}), 500
            return render_template('signup.html', error=error), 500
        
        # Log user in automatically
        session['user_id'] = user_id
        session['username'] = username
        
        if request.is_json:
            return jsonify({'success': True, 'user_id': user_id}), 201
        
        return redirect(url_for('index'))
    
    except Exception as e:
        error = f'Signup error: {str(e)}'
        if request.is_json:
            return jsonify({'error': error}), 500
        return render_template('signup.html', error=error), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and endpoint"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST request - process login
    try:
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Validation
        if not username or not password:
            error = 'Username and password are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            return render_template('login.html', error=error), 400
        
        # Check user exists and password is correct
        user = get_user_by_username(username)
        if not user or not check_password_hash(user['password_hash'], password):
            error = 'Invalid username or password'
            if request.is_json:
                return jsonify({'error': error}), 401
            return render_template('login.html', error=error), 401
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        
        if request.is_json:
            return jsonify({'success': True, 'user_id': user['id']}), 200
        
        return redirect(url_for('index'))
    
    except Exception as e:
        error = f'Login error: {str(e)}'
        if request.is_json:
            return jsonify({'error': error}), 500
        return render_template('login.html', error=error), 500

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout user and clear session"""
    session.clear()
    
    if request.is_json:
        return jsonify({'success': True}), 200
    
    return redirect(url_for('index'))

@auth_bp.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))
    
    # Get user's stories
    stories = get_user_stories(session['user_id'])
    
    return render_template('profile.html', user=user, stories=stories)

@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current logged-in user info (API endpoint)"""
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 401
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user_id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'created_at': user['created_at']
    }), 200

def login_required(f):
    """Decorator to require login for a route"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    
    return decorated_function
