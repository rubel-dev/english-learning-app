
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from uuid import UUID
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from backend.app.modules.users.models.user import User

security = HTTPBearer()
def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db:Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms = [settings.algorithm]
        )
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail = "invalid credentials"
            )
        user_id = UUID(user_id)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail = 'user not found'
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail = 'Invalid Credentials'
        )

def require_roles(allowed_roles: list[str]):
    def checker(
            current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized user"
            )
        return current_user
    return checker