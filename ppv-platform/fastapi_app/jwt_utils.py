import os
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.getenv('FASTAPI_SECRET_KEY', 'changeme')

# JWT alternative for access tokens
def create_jwt_token(user_id, content_id, expires_in=86400, max_uses=1):
    payload = {
        'user_id': user_id,
        'content_id': content_id,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        'max_uses': max_uses,
        'used_count': 0,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
