
# FastAPI import
from fastapi import FastAPI
import os
import sys
from dotenv import load_dotenv
# Ensure /app is in sys.path for Docker
sys.path.insert(0, "/app")
from shared.redis_utils import get_token, atomic_increment_usage

load_dotenv()

app = FastAPI()

DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DB', 'ppv'),
    'user': os.getenv('POSTGRES_USER', 'ppvuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'ppvpass'),
    'host': os.getenv('POSTGRES_HOST', 'db'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
}

SECRET_KEY = os.getenv('FASTAPI_SECRET_KEY', 'changeme')

# Simulate signed URL generation
def generate_signed_url(file_url, token):
    # In production, use S3 pre-signed URLs
    return f"{file_url}?token={token}"

@app.get("/access/{token}")
def access_content(token: str):
    # Try Redis first
    token_data = get_token(token)
    if not token_data:
        # Fallback to DB
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()
            cur.execute("""
                SELECT t.token, t.user_id, t.content_id, t.expires_at, t.max_uses, t.used_count, t.is_active, c.file_url
                FROM core_accesstoken t
                JOIN core_content c ON t.content_id = c.id
                WHERE t.token = %s
            """, (token,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                raise HTTPException(status_code=404, detail="Token not found")
            token_data = {
                'token': str(row[0]),
                'user_id': row[1],
                'content_id': row[2],
                'expires_at': row[3].isoformat(),
                'max_uses': row[4],
                'used_count': row[5],
                'is_active': row[6],
                'file_url': row[7],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Get file_url from DB if not present
        if 'file_url' not in token_data:
            try:
                conn = psycopg2.connect(**DB_PARAMS)
                cur = conn.cursor()
                cur.execute("SELECT file_url FROM core_content WHERE id = %s", (token_data['content_id'],))
                row = cur.fetchone()
                cur.close()
                conn.close()
                token_data['file_url'] = row[0] if row else None
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    # Validate
    if not token_data['is_active']:
        raise HTTPException(status_code=403, detail="Token inactive")
    if datetime.fromisoformat(token_data['expires_at']) < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Token expired")
    if token_data['used_count'] >= token_data['max_uses']:
        raise HTTPException(status_code=403, detail="Token usage exceeded")
    # Atomic increment usage
    used_count = atomic_increment_usage(token)
    if used_count > token_data['max_uses']:
        raise HTTPException(status_code=403, detail="Token usage exceeded (race)")
    # Optionally, update DB used_count (out of band)
    # Generate signed URL
    signed_url = generate_signed_url(token_data['file_url'], token)
    return JSONResponse({
        "access": "granted",
        "content_url": signed_url
    })

@app.get("/health")
def health():
    return {"status": "ok"}
