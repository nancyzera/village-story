# Authentication System Documentation

## Overview

The Village Memory application now includes a complete user authentication system with secure signup, login, and session management. All changes are backward compatible - the search and story viewing remain public.

## Features Implemented

### 1. User Registration & Authentication
- **Secure Password Hashing**: Uses `werkzeug.security.generate_password_hash` with PBKDF2
- **Session Management**: Flask sessions with secure cookies (HTTPOnly, SameSite=Lax)
- **Input Validation**: Username (3+ chars), Email (unique), Password (6+ chars with confirmation)
- **Error Handling**: Duplicate username/email prevention, detailed validation errors

### 2. Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,                    -- UUID
    username TEXT NOT NULL UNIQUE,          -- 3+ characters
    email TEXT NOT NULL UNIQUE,             -- Email format
    password_hash TEXT NOT NULL,            -- Hashed with PBKDF2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Stories Table Updated:**
- Added `user_id` foreign key linking to users table
- All future stories are associated with their creator

### 3. Authentication Routes

#### POST `/auth/signup`
Create a new user account.

**Form Data:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
}
```

**Response (Success - 201):**
```json
{
    "success": true,
    "user_id": "uuid-here"
}
```

**Response (Error - 400):**
```json
{
    "error": "Username already exists"
}
```

#### POST `/auth/login`
Authenticate a user and create a session.

**Form Data:**
```json
{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

**Response (Success - 200):**
```json
{
    "success": true,
    "user_id": "uuid-here"
}
```

**Response (Error - 401):**
```json
{
    "error": "Invalid username or password"
}
```

#### POST `/auth/logout`
Clear the user session and logout.

**Response:**
```json
{
    "success": true
}
```

#### GET `/auth/profile`
View user profile and uploaded stories (requires login).

#### GET `/auth/api/user`
Get current logged-in user info (JSON API endpoint).

**Response (Authenticated - 200):**
```json
{
    "authenticated": true,
    "user_id": "uuid-here",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-11-18 12:34:56"
}
```

**Response (Not Authenticated - 401):**
```json
{
    "authenticated": false
}
```

### 4. Protected Routes

The following routes now require authentication (configured with `@login_required` decorator):

- `GET /upload` - Upload story form (redirects to login if not authenticated)
- `POST /api/upload` - Upload story API (returns 401 if not authenticated)

**Public Routes (No authentication required):**
- `GET /` - Home page
- `GET /search` - Search page
- `POST /api/search` - Search stories by text/emotion/topic
- `GET /story/<story_id>` - View individual story

### 5. Session Configuration

**Security Settings (in `app/main.py`):**
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True        # Prevent JS access
app.config['SESSION_COOKIE_SECURE'] = False         # Set True for HTTPS in production
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'       # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60  # 7 days
```

### 6. User Context in Templates

All templates have access to the current user via `g.user`:

```html
{% if g.user %}
    <p>Welcome, {{ g.user.username }}!</p>
    <a href="{{ url_for('auth.profile') }}">My Profile</a>
    <form method="POST" action="{{ url_for('auth.logout') }}">
        <button type="submit">Logout</button>
    </form>
{% else %}
    <a href="{{ url_for('auth.login') }}">Login</a>
    <a href="{{ url_for('auth.signup') }}">Sign Up</a>
{% endif %}
```

## Files Created/Modified

### New Files
- `app/routes/auth_routes.py` - Authentication endpoints and `@login_required` decorator
- `templates/login.html` - Login form with styling
- `templates/signup.html` - Signup form with validation
- `templates/profile.html` - User profile page showing uploaded stories
- `test_auth_system.py` - Comprehensive authentication tests

### Modified Files
- `app/models.py` - Added users table schema and user management functions
- `app/main.py` - Registered auth blueprint, added session config, added user context loader
- `app/routes/upload_routes.py` - Added `@login_required` decorator, changed to use `user_id`
- `templates/index.html` - Added auth-aware navigation
- `templates/upload.html` - Added auth-aware navigation
- `.env.example` - Cleaned up API keys (removed real credentials, added placeholders)

## Model Functions (app/models.py)

### User Management
```python
create_user(user_id, username, email, password_hash) -> bool
get_user_by_username(username) -> dict | None
get_user_by_email(email) -> dict | None
get_user_by_id(user_id) -> dict | None
get_user_stories(user_id, limit=100) -> list[dict]
save_story_with_user(story_id, user_id, ...) -> None
```

## Testing

Run the comprehensive authentication test suite:

```bash
python test_auth_system.py
```

**Test Coverage:**
- ✅ Health endpoint (baseline)
- ✅ User signup with validation
- ✅ Get current user info
- ✅ Logout and session clearing
- ✅ Upload protection (requires auth)
- ✅ User login
- ✅ Duplicate signup prevention
- ✅ Public search access

All tests pass successfully! ✅

## Security Features

1. **Password Security**: PBKDF2 hashing with Werkzeug
2. **Session Security**: HttpOnly, SameSite cookies
3. **Input Validation**: Length, format, and uniqueness checks
4. **CSRF Protection**: Flask's SameSite cookie policy
5. **SQL Injection Prevention**: Parameterized queries throughout
6. **Route Protection**: Decorator-based authentication checks

## User Stories Linking

When a user uploads a story:
1. `user_id` is automatically captured from session
2. Story is saved with foreign key to users table
3. User can view their stories in profile page
4. Other users can still search and view all stories (public)

## Backward Compatibility

- Existing stories without `user_id` continue to work with fallback handling
- Search functionality remains public (no authentication required)
- Story viewing is public (anyone can read stories)
- Admin panel remains accessible

## Future Enhancements

Possible improvements:
- Email verification before account activation
- Password reset via email
- OAuth integration (Google, GitHub)
- Two-factor authentication (2FA)
- User profile customization
- Story privacy settings (public/private)
- Following other users
- Saving favorite stories
- Comments and discussions

## Environment Variables

Update your `.env` file with these optional variables (already in `.env.example`):

```bash
# These are optional - generated automatically if not set
SECRET_KEY=your-super-secret-key-change-in-production
SESSION_SECRET=your-session-secret-change-in-production
```

For production, generate secure keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Troubleshooting

### "Session appears empty" - User not staying logged in
- Ensure cookies are enabled in browser
- Check that `SESSION_COOKIE_SECURE = False` for non-HTTPS (set True for HTTPS)
- Verify session timeout hasn't expired (7 days default)

### "Username already exists" on signup
- Username is case-sensitive, try a different username
- The username was already registered; use login instead

### "Invalid username or password" on login
- Username is case-sensitive
- Double-check password (no spaces at end/beginning)
- Ensure account exists (signup first if needed)

## Database Migration Notes

If upgrading from old schema:
1. The users table is created automatically on first run
2. Stories table gets user_id column added via ALTER TABLE
3. Existing stories without user_id will have NULL user_id
4. This is handled gracefully by the application

---

**Last Updated:** November 18, 2025
**Status:** ✅ Production Ready
