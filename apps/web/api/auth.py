"""Combined auth handler for PAT, username, and status endpoints using Flask."""
from flask import Flask, request, jsonify
import json
import os
import sys
from urllib.parse import urlparse
import httpx

app = Flask(__name__)

@app.route('/api/auth/pat', methods=['POST', 'OPTIONS'])
def handle_pat():
    """Validate and store GitHub PAT."""
    if request.method == 'OPTIONS':
        return _cors_response()
    
    try:
        data = request.get_json() or {}
        pat = data.get('pat', '').strip()
        store_mode = data.get('store_mode', 'encrypted')
        
        if not pat:
            return jsonify({"ok": False, "error": "PAT is required"}), 400
        
        # Validate PAT with GitHub
        try:
            response = httpx.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {pat}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                timeout=10.0
            )
            
            if response.status_code == 401:
                return jsonify({"ok": False, "error": "Invalid PAT. Please check your token and try again."}), 401
            elif response.status_code != 200:
                return jsonify({"ok": False, "error": f"Failed to validate PAT: GitHub API returned {response.status_code}"}), 500
            
            user_data = response.json()
            
            # Store PAT in database using raw SQL
            try:
                import psycopg2
                from cryptography.fernet import Fernet
                import base64
                import hashlib
                
                # Get database URL from environment
                database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
                
                if database_url:
                    # Encrypt the PAT
                    secret_key = os.getenv("HIDEVS_SECRET_KEY", "dev-secret-change-in-production")
                    # Create a Fernet key from the secret
                    key = base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())
                    f = Fernet(key)
                    encrypted_pat = f.encrypt(pat.encode()).decode()
                    
                    # Parse connection string
                    result = urlparse(database_url)
                    
                    # Connect to database
                    conn = psycopg2.connect(
                        database=result.path[1:],
                        user=result.username,
                        password=result.password,
                        host=result.hostname,
                        port=result.port,
                        sslmode='require'
                    )
                    
                    cursor = conn.cursor()
                    
                    try:
                        # Delete existing tokens
                        cursor.execute("DELETE FROM auth_tokens")
                        
                        # Create new token
                        cursor.execute(
                            "INSERT INTO auth_tokens (encrypted_token, github_user_login, github_user_id, store_mode, created_at, updated_at) "
                            "VALUES (%s, %s, %s, %s, NOW(), NOW())",
                            (encrypted_pat, user_data.get("login"), user_data.get("id"), store_mode)
                        )
                        
                        # Update auth mode setting
                        cursor.execute(
                            "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                            ('auth_mode', 'pat')
                        )
                        
                        # Clear username setting if it exists
                        cursor.execute("DELETE FROM settings WHERE key = 'github_username'")
                        
                        conn.commit()
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                print(f"Database error: {db_error}", file=sys.stderr)
                return jsonify({"ok": False, "error": f"Failed to store PAT: {str(db_error)}"}), 500
            
            # Return success response
            return jsonify({
                "ok": True,
                "user": {
                    "login": user_data.get("login"),
                    "id": user_data.get("id"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_url")
                }
            })
            
        except httpx.RequestError as e:
            return jsonify({"ok": False, "error": f"Failed to connect to GitHub: {str(e)}"}), 500
            
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Invalid JSON in request body"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/auth/username', methods=['POST', 'OPTIONS'])
def handle_username():
    """Validate GitHub username and configure username-only mode."""
    if request.method == 'OPTIONS':
        return _cors_response()
    
    try:
        data = request.get_json() or {}
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"ok": False, "error": "Username is required"}), 400
        
        # Validate username exists on GitHub
        try:
            response = httpx.get(
                f"https://api.github.com/users/{username}",
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                },
                timeout=10.0
            )
            
            if response.status_code == 404:
                return jsonify({"ok": False, "error": f"GitHub user '{username}' not found"}), 404
            elif response.status_code != 200:
                return jsonify({"ok": False, "error": f"Failed to validate username: GitHub API returned {response.status_code}"}), 500
            
            user_data = response.json()
            
            # Store username in database using raw SQL
            try:
                import psycopg2
                
                # Get database URL from environment
                database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
                
                if database_url:
                    # Parse connection string
                    result = urlparse(database_url)
                    
                    # Connect to database
                    conn = psycopg2.connect(
                        database=result.path[1:],
                        user=result.username,
                        password=result.password,
                        host=result.hostname,
                        port=result.port,
                        sslmode='require'
                    )
                    
                    cursor = conn.cursor()
                    
                    try:
                        # Store username in settings
                        cursor.execute(
                            "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                            ('github_username', username)
                        )
                        
                        # Store auth mode
                        cursor.execute(
                            "INSERT INTO settings (key, value, created_at, updated_at) VALUES (%s, %s, NOW(), NOW()) "
                            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()",
                            ('auth_mode', 'username')
                        )
                        
                        conn.commit()
                    finally:
                        cursor.close()
                        conn.close()
            except Exception as db_error:
                # If database fails, still return success but log the error
                print(f"Database error: {db_error}", file=sys.stderr)
            
            # Return success response
            return jsonify({
                "ok": True,
                "user": {
                    "login": user_data.get("login"),
                    "id": user_data.get("id"),
                    "name": user_data.get("name"),
                    "avatar_url": user_data.get("avatar_url")
                }
            })
            
        except httpx.RequestError as e:
            return jsonify({"ok": False, "error": f"Failed to connect to GitHub: {str(e)}"}), 500
            
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "Invalid JSON in request body"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/auth/status', methods=['GET', 'OPTIONS'])
def handle_status():
    """Get authentication status from database."""
    if request.method == 'OPTIONS':
        return _cors_response()
    
    try:
        configured = False
        user_info = None
        
        # Check database for authentication using raw SQL
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # Get database URL from environment
            database_url = os.getenv("POSTGRES_URL_NON_POOLING") or os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
            
            if database_url:
                # Parse connection string
                result = urlparse(database_url)
                
                # Connect to database
                conn = psycopg2.connect(
                    database=result.path[1:],
                    user=result.username,
                    password=result.password,
                    host=result.hostname,
                    port=result.port,
                    sslmode='require'
                )
                
                cursor = conn.cursor()
                
                try:
                    # Check for PAT authentication
                    cursor.execute("SELECT github_user_login, github_user_id FROM auth_tokens LIMIT 1")
                    auth_token = cursor.fetchone()
                    
                    if auth_token:
                        configured = True
                        user_info = {
                            "login": auth_token[0],
                            "id": auth_token[1]
                        }
                    else:
                        # Check for username-only mode
                        cursor.execute("SELECT value FROM settings WHERE key = 'github_username' LIMIT 1")
                        username_row = cursor.fetchone()
                        
                        if username_row and username_row[0]:
                            configured = True
                            username = username_row[0]
                            
                            # Fetch user info from GitHub
                            try:
                                response = httpx.get(
                                    f"https://api.github.com/users/{username}",
                                    headers={
                                        "Accept": "application/vnd.github+json",
                                        "X-GitHub-Api-Version": "2022-11-28"
                                    },
                                    timeout=5.0
                                )
                                if response.status_code == 200:
                                    user_data = response.json()
                                    user_info = {
                                        "login": user_data.get("login"),
                                        "id": user_data.get("id"),
                                        "name": user_data.get("name"),
                                        "avatar_url": user_data.get("avatar_url")
                                    }
                            except Exception:
                                pass
                finally:
                    cursor.close()
                    conn.close()
        except Exception as db_error:
            print(f"Database error: {db_error}", file=sys.stderr)
        
        payload = {
            "ok": True,
            "configured": configured,
        }
        
        if user_info:
            payload["user"] = user_info
        
        return jsonify(payload)
        
    except Exception as e:
        return jsonify({"ok": False, "error": f"Internal server error: {str(e)}"}), 500

def _cors_response():
    """Return CORS preflight response."""
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Export app for Vercel
# Vercel will detect this as the WSGI application
