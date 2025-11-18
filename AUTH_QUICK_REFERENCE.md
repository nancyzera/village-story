# Authentication System - Quick Reference

## 🚀 Getting Started

### Sign Up
1. Navigate to `/auth/signup`
2. Fill in username (3+ chars), email, password (6+ chars)
3. Confirm password
4. Click "Create Account"
5. Automatically logged in ✓

### Log In
1. Navigate to `/auth/login`
2. Enter username and password
3. Click "Login"
4. Session created for 7 days ✓

### Log Out
1. Click "Logout" button in navigation
2. Session cleared immediately ✓

## 📝 User Workflows

### Upload a Story
1. Must be logged in (redirects to login if not)
2. Click "Upload" in navigation
3. Fill story form with:
   - Speaker name (required)
   - District (optional)
   - Story text OR audio file
   - Cover image (optional)
   - Generate TTS checkbox (optional)
4. Submit
5. Story linked to your account ✓
6. View in your profile

### View Your Profile
1. Click your username in navigation
2. See account details:
   - Username
   - Email
   - Member since date
   - Total stories uploaded
3. Table of all your uploaded stories
4. Click "View" to read any story

### Search Stories
- Public! No login needed
- Search by keywords, emotion, topic
- View any story by clicking on results
- View story details including:
  - Speaker name
  - District
  - Full text
  - Original audio (if uploaded)
  - Generated TTS (if enabled)
  - Emotion tags

## 🔑 API Endpoints

### Authentication

**POST /auth/signup**
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
  }'
```

**POST /auth/login**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**GET /auth/api/user** (requires login)
```bash
curl -X GET http://localhost:5000/auth/api/user \
  -H "Cookie: session=your-session-cookie"
```

**POST /auth/logout**
```bash
curl -X POST http://localhost:5000/auth/logout
```

### Protected Routes (Require Login)

**GET /upload** - Upload form
**POST /api/upload** - Upload story

### Public Routes (No Login)

**POST /api/search** - Search stories
**GET /story/<story_id>** - View story
**GET /** - Home
**GET /search** - Search form

## 🗄️ Database Schema

```sql
-- Users Table
users (
  id                TEXT PRIMARY KEY,
  username          TEXT NOT NULL UNIQUE,
  email             TEXT NOT NULL UNIQUE,
  password_hash     TEXT NOT NULL,
  created_at        TIMESTAMP,
  updated_at        TIMESTAMP
)

-- Stories Table (updated)
stories (
  id                        TEXT PRIMARY KEY,
  user_id                   TEXT (FOREIGN KEY),
  speaker_name              TEXT NOT NULL,
  district                  TEXT,
  story_text                TEXT,
  transcription_text        TEXT,
  audio_filename            TEXT,
  cover_image_filename      TEXT,
  tts_audio_filename        TEXT,
  emotion_tag               TEXT,
  created_at                TIMESTAMP,
  file_type                 TEXT
)
```

## 🔒 Security Features

✓ Passwords hashed with PBKDF2
✓ HttpOnly cookies (can't be accessed by JS)
✓ SameSite cookie policy (CSRF protection)
✓ Unique email and username enforcement
✓ Session timeout (7 days)
✓ SQL injection prevention (parameterized queries)
✓ Input validation (length, format, uniqueness)

## 🧪 Testing

Run authentication tests:
```bash
python test_auth_system.py
```

Expected output:
```
=== Testing Health Endpoint ===
Status: 200

=== Testing User Signup ===
Status: 201
✓ Account created

=== Testing Get Current User ===
Status: 200
✓ Logged in

=== Testing Logout ===
Status: 200
✓ Session cleared

=== Testing Upload Without Authentication ===
Status: 302
✓ Redirects to login

=== Testing User Login ===
Status: 200
✓ Logged in again

=== Testing Duplicate Signup ===
Status: 400
✓ Prevented duplicate

=== Testing Public Search ===
Status: 200
✓ Public access works

==================================================
✅ All authentication tests passed!
==================================================
```

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| "Username already exists" | Choose a different username or login if you have an account |
| Session lost after refresh | Check if cookies are enabled in browser |
| Upload page shows login | Your session expired; login again |
| Password verification failed | Ensure password has no spaces; try copying/pasting |
| Can't find my stories | Go to your profile (click your username) |

## 📱 Navigation Flow

```
Home (/)
├── Not Logged In
│   ├── Login (/auth/login)
│   │   └── Sign Up (/auth/signup)
│   ├── Search (/search) [public]
│   └── View Stories [public]
│
└── Logged In
    ├── Profile (/auth/profile)
    ├── Upload (/upload)
    ├── Search (/search)
    └── Logout
```

## ⚙️ Configuration

### Session Lifetime
Default: 7 days
Location: `app/main.py`
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60
```

### Session Security
```python
app.config['SESSION_COOKIE_HTTPONLY'] = True      # Prevent JS access
app.config['SESSION_COOKIE_SECURE'] = False       # Set True for HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'     # CSRF protection
```

### Password Requirements
- Minimum 6 characters
- Checked during signup

### Username Requirements
- Minimum 3 characters
- Must be unique (case-sensitive)

### Email Requirements
- Must be valid email format
- Must be unique

## 📚 Template Variables

All templates have access to:
```jinja2
{{ g.user }}           # Current logged-in user (or None)
{{ g.user.username }}  # Username
{{ g.user.email }}     # Email
{{ g.user.id }}        # User ID
{{ g.user.created_at }} # Account creation date
```

Example:
```html
{% if g.user %}
    Welcome, {{ g.user.username }}!
{% else %}
    Please log in to continue.
{% endif %}
```

---

**Need Help?** Check `AUTH_SYSTEM_README.md` for detailed documentation.
