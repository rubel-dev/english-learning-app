from fastapi import APIRouter, Depends, status

from app.db.session import get_db
from app.modules.listening.schemas.listening import ListeningImport
from sqlalchemy.orm import Session

from app.modules.listening import service

router = APIRouter(
    prefix="/admin/listenings",
    tags=["Admin - Listening"]
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_listening(
    data: ListeningImport,
    db:Session = Depends(get_db)
):
    return service.listening_create(db = db, data = data)