from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.modules.reading.schemas.reading_schema import ReadingCreate, ReadingResponse, ReadingUpdate
from backend.app.modules.users.models.user import User
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from backend.app.modules.reading.models.reading import Reading
app = APIRouter()

router = APIRouter(
    prefix="/admin/readings",
    tags=['Admin Reading']
)

@router.post("", status_code=201)
async def create_reading(
    data: ReadingCreate,
    current_user:User = Depends(require_roles(["admin"])),
    db:Session = Depends(get_db)
):
    reading = Reading(
        title=data.title,
        passage=data.passage,
        reading_level=data.reading_level,
        topic=data.topic,
        estimated_reading_time=data.estimated_reading_time,
        quiz=[question.model_dump() for question in data.quiz]

    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

@router.get("", response_model=list[ReadingResponse])
def get_readings(
    current_user: User = Depends(require_roles(["admin"])),
    db:Session = Depends(get_db)
):
    return db.query(Reading).all()

@router.get(
    "/{reading_id}",
    response_model=ReadingResponse

)
async def get_readings(
    reading_id: UUID,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    reading = (
        db.query(Reading)
        .filter(Reading.id ==reading_id)
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=404,
            detail = "Reading not found"
        )
    return reading

@router.put(
    "/{reading_id}",
    
    response_model=ReadingResponse
)
async def update_reading(
    reading_id: UUID,
    data: ReadingUpdate,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    reading = (
        db.query(Reading).filter(
            Reading.id == reading_id
        ).first()
    )
    if not reading:
        raise HTTPException(
            status_code = 404,
            detail='Reading not found'
        )
    update_data = data.model_dump(exclude_unset = True)
    if "quiz" in update_data:
        update_data["quiz"] = [
            question.model_dump()
            for question in data.quiz

        ]
    for field , value in update_data.items():
        setattr(reading, field, value)
    db.commit()
    db.refresh(reading)
    return reading

@router.delete(
    "/{reading_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reading(
    reading_id: UUID,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    reading = (
        db.query(Reading)
        .filter(Reading.id == reading_id)
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading not found",
        )

    db.delete(reading)
    db.commit()
