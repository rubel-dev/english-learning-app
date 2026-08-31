from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db
from backend.app.modules.auth.schemas.auth import LoginRegister, RegisterRequest
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from backend.app.modules.users.models.user import User
from app.api.deps import require_roles
router = APIRouter()

@router.post('/auth/register')
async def register(
    user:RegisterRequest,
    db:Session = Depends(get_db)
):
    new_user = User(
        name = user.username,
        email = user.email,
        password_hash = hash_password(user.password),
        role = user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post('/auth/login')
async def login(
    user:LoginRegister,
    db:Session = Depends(get_db)
):
    user_db = db.query(User).filter(User.email == user.email).first()
    if user_db is None:
        raise HTTPException(
            status_code=404,
            detail = "user not found"
        )
    if not verify_password(user.password, user_db.password_hash):
        raise HTTPException(
            status_code=400,
            detail='Invalid Credentials'
        )
    token =  create_access_token({
        "user_id":str(user_db.id),
        "role":user_db.role
    })
    return {"access_token":token, "type":"bearer"}





@router.get('/test')
def admin_test(
    current_user:User = Depends(require_roles(['admin']))
):
    return {
        "message": "Admin access granted",
        "user_id": str(current_user.id),
        "role": current_user.role
    }