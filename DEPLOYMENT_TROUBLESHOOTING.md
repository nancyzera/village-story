# 🚀 Deployment Troubleshooting Guide

## Common Issues & Solutions

### 1. ❌ "gunicorn: command not found"

**Root Cause:** Gunicorn is not installed in the production environment.

**✅ Solution:**
- Added `gunicorn==23.0.0` to `requirements.txt`
- Created `render.yaml` with proper build configuration
- Push changes to GitHub and redeploy

**Prevention:**
- Always include web server in `requirements.txt`
- Test build locally: `pip install -r requirements.txt`

---

### 2. ❌ Missing Dependencies

**Root Cause:** Not all Python packages are listed in `requirements.txt`.

**✅ Solution:**

Generate requirements file locally:
```bash
pip freeze > requirements.txt
```

Or manually add all packages:
```
Flask==3.1.2
Flask-CORS==6.0.1
python-dotenv==1.0.1
gunicorn==23.0.0
# ... (all packages)
```

---

### 3. ❌ Port Configuration Issues

**Root Cause:** Render assigns a random port via `PORT` environment variable.

**✅ Solution:**

Update start command to use dynamic port:
```bash
gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} app.main:app
```

Update `app/main.py`:
```python
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
```

---

### 4. ❌ Database Issues

**Root Cause:** SQLite database not persisting or accessible.

**✅ Solution:**

For Render deployment, use environment variables:
```bash
# render.yaml
envVars:
  - key: DATABASE_PATH
    value: /tmp/stories.db
```

Or use PostgreSQL/MySQL instead of SQLite:
```python
# For production
DATABASE_URL = os.environ.get('DATABASE_URL')
```

---

### 5. ❌ Static Files Not Loading

**Root Cause:** Static files not found in production.

**✅ Solution:**

In `app/main.py`, ensure proper paths:
```python
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
```

Run collectstatic (if needed):
```bash
python manage.py collectstatic --noinput
```

---

### 6. ❌ Environment Variables Not Set

**Root Cause:** `.env` file not in production, or variables not configured.

**✅ Solution:**

In `render.yaml`:
```yaml
envVars:
  - key: OPENAI_API_KEY
    value: ${OPENAI_API_KEY}
  - key: QDRANT_URL
    value: ${QDRANT_URL}
  - key: QDRANT_API_KEY
    value: ${QDRANT_API_KEY}
```

---

## 📋 Deployment Checklist

- [ ] ✅ `requirements.txt` includes all dependencies
- [ ] ✅ `gunicorn` is in `requirements.txt`
- [ ] ✅ `render.yaml` created with proper configuration
- [ ] ✅ `app/main.py` uses `PORT` environment variable
- [ ] ✅ All environment variables set in Render dashboard
- [ ] ✅ Database path is writable
- [ ] ✅ Static files are properly configured
- [ ] ✅ Changes pushed to GitHub
- [ ] ✅ Build succeeds locally: `pip install -r requirements.txt`
- [ ] ✅ Test locally: `gunicorn -w 1 -b 0.0.0.0:5000 app.main:app`

---

## 🔧 Local Testing Before Deployment

### Test dependencies:
```bash
pip install -r requirements.txt
```

### Test with gunicorn:
```bash
gunicorn -w 1 -b 0.0.0.0:5000 app.main:app
```

### Test environment variables:
```bash
export OPENAI_API_KEY="test"
export PORT=5000
python -m app.main
```

---

## 📊 Render Dashboard Checks

1. **Settings Tab**
   - Verify Build Command
   - Verify Start Command
   - Check Environment Variables
   - Verify Python Version (3.9+)

2. **Logs Tab**
   - Check for error messages
   - Look for module import errors
   - Review startup logs

3. **Health Tab**
   - Click "View" to test endpoint
   - Should return 200 OK

---

## 🆘 If Still Failing

1. **Check Render logs:**
   - Go to Render dashboard → Logs
   - Look for specific error messages

2. **Check build output:**
   - "Downloaded X packages"
   - "Installed X packages"
   - "Build successful 🎉"

3. **Verify start command:**
   - `gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} app.main:app`
   - Should show: "Listening on http://0.0.0.0:PORT"

4. **Test health endpoint:**
   - `https://your-app.onrender.com/api/health`
   - Should return: `{"status": "healthy"}`

---

## 📚 Useful Resources

- [Render Python Deployment Guide](https://render.com/docs/deploy-python)
- [Gunicorn Configuration](https://gunicorn.org/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/deployment/)

---

**Status:** ✅ Fixed  
**Files Updated:**
- ✅ `requirements.txt` - Created with gunicorn
- ✅ `render.yaml` - Created with Render config
- ✅ Changes pushed to GitHub

**Next Step:** Trigger a new deploy in Render dashboard or push a change to GitHub to redeploy automatically.
