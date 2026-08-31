from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import UTC, datetime, timedelta
from app.core.config import settings
pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
    )
def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(UTC)+timedelta(minutes=30)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    return encoded_jwt

