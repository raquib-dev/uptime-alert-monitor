from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

SECRET_KEY = "your_secret_key_here"  # You should load this from .env
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
