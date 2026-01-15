import hashlib
from database import get_user

def verify_password(username, password):
    """Verify if the provided password matches the stored hash."""
    user = get_user(username)
    if not user:
        return False, None
    
    # Simple SHA256 for demonstration. Use bcrypt/argon2 for production.
    input_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if input_hash == user['password_hash']:
        return True, user
    return False, None
