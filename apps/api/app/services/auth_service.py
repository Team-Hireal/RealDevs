"""Authentication service for PAT management."""
from typing import Dict, Optional
from app.models import db, AuthToken
from app.utils.encryption import TokenEncryption
from app.utils.github_client import GitHubClient
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# In-memory store for session-based tokens (when store_mode='memory')
_memory_token_store: Dict[str, str] = {}


class AuthService:
    """Manages GitHub PAT authentication and username-only mode."""
    
    @staticmethod
    def store_username(username: str) -> Dict:
        """Store GitHub username for unauthenticated access (public data only)."""
        try:
            # Validate that the username exists by fetching user info
            with GitHubClient() as client:
                user_info = client.get_user(username)
            
            if not user_info:
                raise ValueError(f"GitHub user '{username}' not found")
            
            github_id = user_info.get('id')
            github_login = user_info.get('login')
            
            if not github_login or not github_id:
                raise ValueError("Invalid GitHub user info")
            
            # Store in memory only (no PAT to encrypt)
            _memory_token_store['username_mode'] = True
            _memory_token_store['github_login'] = github_login
            _memory_token_store['github_id'] = str(github_id)
            
            logger.info(f"Username stored (unauthenticated mode) for user: {github_login}")
            
            return {
                "ok": True,
                "user": {
                    "login": github_login,
                    "id": github_id,
                    "name": user_info.get('name'),
                    "avatar_url": user_info.get('avatar_url')
                },
                "mode": "username_only"
            }
        
        except Exception as e:
            logger.error(f"Error storing username: {e}")
            raise
    
    @staticmethod
    def validate_and_store_pat(pat: str, store_mode: str = "encrypted") -> Dict:
        """Validate PAT with GitHub and store it."""
        try:
            # Validate token with GitHub
            with GitHubClient(pat) as client:
                user_info = client.validate_token()
            
            github_login = user_info.get('login')
            github_id = user_info.get('id')
            
            if not github_login or not github_id:
                raise ValueError("Invalid GitHub user info")
            
            # Handle storage based on mode
            if store_mode == "encrypted":
                # Encrypt and store in database
                encryption = TokenEncryption(current_app.config['SECRET_KEY'])
                encrypted_token = encryption.encrypt(pat)
                
                # Delete existing token if any
                AuthToken.query.delete()
                
                # Create new token record
                auth_token = AuthToken(
                    encrypted_token=encrypted_token,
                    github_user_login=github_login,
                    github_user_id=github_id,
                    store_mode=store_mode
                )
                db.session.add(auth_token)
                db.session.commit()
                
                # https://github.com/SimonSaysGiveMeSmile
                logger.info(f"PAT stored (encrypted) for user: {github_login}")
            
            elif store_mode == "memory":
                # Store in memory only (session-based)
                _memory_token_store['current_pat'] = pat
                _memory_token_store['github_login'] = github_login
                _memory_token_store['github_id'] = str(github_id)
                
                logger.info(f"PAT stored (memory) for user: {github_login}")
            
            else:
                raise ValueError(f"Invalid store_mode: {store_mode}")
            
            return {
                "ok": True,
                "user": {
                    "login": github_login,
                    "id": github_id,
                    "name": user_info.get('name'),
                    "avatar_url": user_info.get('avatar_url')
                },
                "mode": "pat"
            }
        
        except Exception as e:
            logger.error(f"Error validating PAT: {e}")
            raise
    
    @staticmethod
    def get_stored_pat() -> Optional[str]:
        """Retrieve stored PAT (from DB or memory).
        
        Returns None if in username-only mode.
        """
        # Check if in username-only mode
        if _memory_token_store.get('username_mode', False):
            return None
        
        # Check memory store first
        if 'current_pat' in _memory_token_store:
            return _memory_token_store['current_pat']
        
        # Check database
        auth_token = AuthToken.query.first()
        if auth_token and auth_token.store_mode == "encrypted":
            encryption = TokenEncryption(current_app.config['SECRET_KEY'])
            return encryption.decrypt(auth_token.encrypted_token)
        
        return None
    
    @staticmethod
    def get_stored_username() -> Optional[str]:
        """Retrieve stored username for unauthenticated mode."""
        if 'github_login' in _memory_token_store:
            return _memory_token_store['github_login']
        return None
    
    @staticmethod
    def is_username_only_mode() -> bool:
        """Check if currently in username-only (unauthenticated) mode."""
        return _memory_token_store.get('username_mode', False)
    
    @staticmethod
    def get_user_info() -> Optional[Dict]:
        """Get stored user info without exposing PAT."""
        # Check memory store first
        if 'github_login' in _memory_token_store:
            is_username_mode = _memory_token_store.get('username_mode', False)
            return {
                "login": _memory_token_store['github_login'],
                "id": int(_memory_token_store['github_id']),
                "store_mode": "username_only" if is_username_mode else "memory",
                "authenticated": not is_username_mode
            }
        
        # Check database
        auth_token = AuthToken.query.first()
        if auth_token:
            return {
                "login": auth_token.github_user_login,
                "id": auth_token.github_user_id,
                "store_mode": auth_token.store_mode,
                "authenticated": True
            }
        
        return None
    
    @staticmethod
    def clear_all_data():
        """Wipe all stored data including PAT."""
        # Clear memory store
        _memory_token_store.clear()
        
        # Clear database - include all models
        from app.models import Repository, Contributor, DailyStats, TeamMember, Settings, ExternalCommit
        
        AuthToken.query.delete()
        DailyStats.query.delete()
        Contributor.query.delete()
        Repository.query.delete()
        TeamMember.query.delete()
        Settings.query.delete()
        ExternalCommit.query.delete()
        
        db.session.commit()
        logger.info("All data cleared")

