# 🚀 Quick Start Guide - Authentication System

## Getting Started

### 1. Start the Flask Server

```bash
cd "c:\Users\iTek\OneDrive\village memory\village-story"
python -m app.main
```

The server will start on `http://localhost:5000`

### 2. Create an Account

Navigate to: **http://localhost:5000/auth/signup**

Fill in:
- **Username**: Choose a unique username (3+ characters)
- **Email**: Your email address
- **Password**: Strong password (6+ characters)
- **Confirm Password**: Re-enter password

Click **Create Account** and you'll be automatically logged in!

### 3. Upload Your First Story

Navigate to: **http://localhost:5000/upload**

Fill in:
- **Speaker Name**: Your name or character name
- **District**: Location (optional)
- **Story Text**: Write or paste your story
- **Upload Audio** (optional): Record or upload audio file
- **Generate Audio from Text** (optional): Check to create TTS audio
- **Cover Image** (optional): Upload a cover photo

Click **Upload Story** and your story is saved!

### 4. Search and View Stories

Navigate to: **http://localhost:5000/search**

- Type keywords to search all stories
- View any story by clicking on it
- Search results show speaker name, district, and preview

### 5. View Your Profile

Click your username in the top-right corner or navigate to: **http://localhost:5000/auth/profile**

Your profile shows:
- Account details (username, email, join date)
- Count of stories you've uploaded
- List of all your stories

### 6. Logout

Click **Logout** in the top-right corner to end your session.

## Common Tasks

### Login to Existing Account
1. Go to **http://localhost:5000/auth/login**
2. Enter your username and password
3. Click **Login**

### Update Your Story
Stories are stored in the database. To edit:
1. View your profile
2. Click the story you want to view
3. Currently view-only; editing coming soon

### Search for Stories by Theme
Use the search function to find stories by:
- **Text search**: Keywords from story content
- **Emotion search**: Happy, sad, inspiring, etc.
- **Topic search**: Village history, legends, traditions, etc.

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Go to Home | `Ctrl+Home` |
| Go to Upload | `Ctrl+U` |
| Go to Search | `Ctrl+F` |
| Go to Profile | `Ctrl+P` |

## Troubleshooting

### "Username already exists"
- The username is already taken
- Choose a different username
- Username is case-sensitive

### "Invalid username or password"
- Double-check your password (case-sensitive)
- Ensure username is correct
- Create a new account if you forget the password

### "Session expired"
- You've been logged out after 7 days of inactivity
- Log in again

### "Upload requires authentication"
- You must be logged in to upload stories
- Log in or create an account first

## Account Security Tips

✅ **DO:**
- Use a strong, unique password
- Never share your login credentials
- Logout on shared computers
- Use different passwords for different sites

❌ **DON'T:**
- Reuse passwords from other sites
- Share your account with others
- Write down passwords
- Click suspicious login links

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers (iOS/Android)

## Need Help?

### View Full Documentation
See `AUTH_SYSTEM_README.md` for complete API documentation

### Check Logs
The Flask server logs all requests and errors in the terminal

### Test Authentication System
Run automated tests:
```bash
python test_auth_system.py
```

## Features At a Glance

| Feature | Status |
|---------|--------|
| User Registration | ✅ Complete |
| User Login | ✅ Complete |
| Password Hashing | ✅ Secure (PBKDF2) |
| Session Management | ✅ 7-day timeout |
| Upload Stories | ✅ User-owned |
| Search Stories | ✅ Public |
| View Stories | ✅ Public |
| User Profile | ✅ Dashboard |
| Role Management | 🔄 Coming Soon |
| Email Verification | 🔄 Coming Soon |
| Password Reset | 🔄 Coming Soon |

---

**Last Updated**: November 18, 2025  
**Status**: ✅ Ready to Use
