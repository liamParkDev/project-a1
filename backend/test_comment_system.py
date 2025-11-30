import sys
import os
import json
import urllib.request
import urllib.error
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import Base, get_db
from db import models
from core.security import get_password_hash

# Configuration
API_URL = "http://127.0.0.1:8000/api"
# Use the engine from db.session
from db.session import engine, SessionLocal

def setup_data():
    db = SessionLocal()
    try:
        # 1. Ensure Region
        region = db.query(models.Region).first()
        if not region:
            region = models.Region(
                country_code="KR",
                city="Seoul",
                district="Gangnam",
                name="Gangnam-gu",
                center_lat=37.5172,
                center_lng=127.0473
            )
            db.add(region)
            db.commit()
            db.refresh(region)
        print(f"Using Region ID: {region.id}")

        # 2. Ensure User
        email = "test@example.com"
        password = "password123"
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                email=email,
                password_hash=get_password_hash(password),
                nickname="TestUser",
                home_region_id=region.id,
                role=models.UserRole.user
            )
            db.add(user)
        else:
            # Update password to ensure we can login
            user.password_hash = get_password_hash(password)
        
        db.commit()
        db.refresh(user)
        print(f"Using User ID: {user.id}")

        # 3. Ensure Post
        post = db.query(models.CommunityPost).filter(models.CommunityPost.title == "Test Post").first()
        if not post:
            post = models.CommunityPost(
                user_id=user.id,
                region_id=region.id,
                title="Test Post",
                content="This is a test post for comments.",
                category_id=None # Optional
            )
            db.add(post)
            db.commit()
            db.refresh(post)
        print(f"Using Post ID: {post.id}")
        
        user_email = user.email
        post_id = post.id
        return user_email, post_id, password
    finally:
        db.close()

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data:
        data_bytes = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        data_bytes = None

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            return json.loads(resp_body)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_comments(user_email, post_id, password):
    # 1. Login
    print("\n[1] Logging in...")
    login_payload = {"email": user_email, "password": password}
    resp = make_request(f"{API_URL}/users/login", method="POST", data=login_payload)
    if not resp:
        return
    token = resp["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Create Root Comment
    print("\n[2] Creating Root Comment...")
    comment_payload = {"content": "Root Comment 1"}
    root_comment = make_request(f"{API_URL}/community/posts/{post_id}/comments", method="POST", data=comment_payload, headers=headers)
    if not root_comment:
        return
    print(f"Created Root Comment ID: {root_comment['id']}")

    # 3. Create Reply
    print("\n[3] Creating Reply...")
    reply_payload = {"content": "Reply to Root 1", "parent_id": root_comment['id']}
    reply_comment = make_request(f"{API_URL}/community/posts/{post_id}/comments", method="POST", data=reply_payload, headers=headers)
    if not reply_comment:
        return
    print(f"Created Reply Comment ID: {reply_comment['id']}")

    # 4. Get Comments Tree
    print("\n[4] Fetching Comment Tree...")
    tree = make_request(f"{API_URL}/community/posts/{post_id}/comments", method="GET", headers=headers)
    if not tree:
        return
    
    print("\n--- Comment Tree ---")
    print(json.dumps(tree, indent=2, ensure_ascii=False))

    # Verification
    # Find our root comment
    found_root = next((c for c in tree if c['id'] == root_comment['id']), None)
    if found_root:
        print("\n[PASS] Root comment found.")
        if found_root['children'] and found_root['children'][0]['id'] == reply_comment['id']:
            print("[PASS] Reply comment found nested correctly.")
            print(f"[PASS] User Nickname: {found_root['user_nickname']}")
        else:
            print("[FAIL] Reply comment not nested correctly.")
    else:
        print("[FAIL] Root comment not found.")

if __name__ == "__main__":
    try:
        user_email, post_id, password = setup_data()
        test_comments(user_email, post_id, password)
    except Exception as e:
        print(f"An error occurred: {e}")
