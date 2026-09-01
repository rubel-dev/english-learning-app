from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.modules.users.models.user import User
from backend.app.modules.listening.models.listening import ListeningLevel, ListeningType
from app.modules.listening import service
from backend.app.modules.listening.schemas import ListeningListResponse, ListeningResponse

router = APIRouter(
    prefix="/listenings",
    tags=["Listening"]
)


@router.get(
        "",
        response_mode=ListeningListResponse
        )
async def get_listenings(
    type: ListeningType | None = None,
    level: ListeningLevel | None = None,
    page: int = Query(1, ge = 1),
    limit: int = Query(10, ge = 1, le = 100),
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    return service.get_list(
        db=db,
        type=type,
        level=level,
        page=page,
        limit=limit
    )

@router.get(
    "/{listening_id}",
    response_model=ListeningResponse
)
def get_listeing(
    listening_id: UUID,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    return service.get_by_id(db = db, listening_id = listening_id)