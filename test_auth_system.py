#!/usr/bin/env python3
"""
Test authentication system: signup, login, upload story, search
"""
import requests
import json
from time import sleep, time

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

# Generate unique username based on timestamp
UNIQUE_USERNAME = f"testuser_{int(time() * 1000)}"
UNIQUE_EMAIL = f"testuser_{int(time() * 1000)}@example.com"

def test_signup():
    """Test user signup"""
    print("\n=== Testing User Signup ===")
    data = {
        'username': UNIQUE_USERNAME,
        'email': UNIQUE_EMAIL,
        'password': 'testpass123',
        'password_confirm': 'testpass123'
    }
    
    resp = SESSION.post(f"{BASE_URL}/auth/signup", json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 201 and resp.json().get('success')

def test_signup_duplicate():
    """Test signup with duplicate username"""
    print("\n=== Testing Duplicate Signup ===")
    data = {
        'username': UNIQUE_USERNAME,
        'email': 'another@example.com',
        'password': 'testpass123',
        'password_confirm': 'testpass123'
    }
    
    resp = SESSION.post(f"{BASE_URL}/auth/signup", json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 400

def test_get_current_user():
    """Test getting current user info"""
    print("\n=== Testing Get Current User ===")
    resp = SESSION.get(f"{BASE_URL}/auth/api/user")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 200 and resp.json().get('authenticated')

def test_logout():
    """Test logout"""
    print("\n=== Testing Logout ===")
    resp = SESSION.post(f"{BASE_URL}/auth/logout", json={})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 200

def test_upload_without_auth():
    """Test that upload requires authentication"""
    print("\n=== Testing Upload Without Authentication ===")
    # Use a fresh session without cookies
    fresh_session = requests.Session()
    resp = fresh_session.get(f"{BASE_URL}/upload", allow_redirects=False)
    print(f"Status: {resp.status_code}")
    print(f"Headers: {resp.headers}")
    # Should redirect (302) or return 401
    return resp.status_code in [302, 401]

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    data = {
        'username': UNIQUE_USERNAME,
        'email': UNIQUE_EMAIL,
        'password': 'testpass123'
    }
    
    resp = SESSION.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 200 and resp.json().get('success')

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 200

def test_search_public():
    """Test that search is public (no auth required)"""
    print("\n=== Testing Public Search ===")
    resp = SESSION.get(f"{BASE_URL}/search")
    print(f"Status: {resp.status_code}")
    # Should render search page without requiring auth
    return resp.status_code == 200

if __name__ == '__main__':
    print("Starting Authentication System Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Test health first
    if not test_health():
        print("ERROR: Server is not responding!")
        exit(1)
    
    # Create a new session for fresh testing
    SESSION = requests.Session()
    
    # Test signup
    if not test_signup():
        print("ERROR: Signup failed!")
        exit(1)
    
    # Test current user (should be logged in after signup)
    if not test_get_current_user():
        print("ERROR: Get current user failed!")
        exit(1)
    
    # Test logout
    if not test_logout():
        print("ERROR: Logout failed!")
        exit(1)
    
    # Test that upload is protected
    if not test_upload_without_auth():
        print("ERROR: Upload protection check failed!")
        exit(1)
    
    # Test login
    if not test_login():
        print("ERROR: Login failed!")
        exit(1)
    
    # Test duplicate signup
    if not test_signup_duplicate():
        print("ERROR: Duplicate signup check failed!")
        exit(1)
    
    # Test public search
    if not test_search_public():
        print("ERROR: Public search failed!")
        exit(1)
    
    print("\n" + "="*50)
    print("✅ All authentication tests passed!")
    print("="*50)
