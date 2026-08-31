from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user

from backend.app.modules.users.models.user import User
from backend.app.modules.vocabulary.models.vocabulary_learning_content import VocabularyLearningContent
from backend.app.modules.vocabulary.models.user_vocabulary import UserVocabulary

from backend.app.modules.vocabulary.schemas.vocabulary_schema import TodayVocabularyResponse, UserVocabularyResponse, VocabularyReviewCreate
from backend.app.modules.vocabulary.models.vocabulary import Vocabulary
from backend.app.modules.vocabulary.models.vocabulary_review import VocabularyReview


router = APIRouter(
    prefix="/vocabularies",
    tags=["Vocabulary"]
)


SRS_INTERVALS = {
    1: 1,
    2: 3,
    3: 7,
    4: 14,
    5: 30,
    6: 60,
    7: 90,
    8: 1000,
}


@router.post(
    "/{learning_content_id}/save",
    response_model=UserVocabularyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def save_vocabulary(
    learning_content_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check learning content exists
    learning_content = (
        db.query(VocabularyLearningContent)
        .filter(
            VocabularyLearningContent.id == learning_content_id
        )
        .first()
    )

    if not learning_content:
        raise HTTPException(
            status_code=404,
            detail="Vocabulary learning content not found",
        )

    # Check if user already saved this vocabulary
    existing_vocabulary = (
        db.query(UserVocabulary)
        .filter(
            UserVocabulary.user_id == user.id,
            UserVocabulary.learning_content_id == learning_content_id,
        )
        .first()
    )

    if existing_vocabulary:
        raise HTTPException(
            status_code=409,
            detail="Vocabulary already saved",
        )

    # Initial SRS state
    now = datetime.now(timezone.utc)

    initial_stage = 1
    next_review_at = now + timedelta(
        days=SRS_INTERVALS[initial_stage]
    )

    user_vocabulary = UserVocabulary(
        user_id=user.id,
        learning_content_id=learning_content_id,
        stage=initial_stage,
        next_review_at=next_review_at,
        last_review_at=None,
        status="active",
    )

    db.add(user_vocabulary)

    try:
        db.commit()
        db.refresh(user_vocabulary)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save vocabulary",
        )

    return user_vocabulary

 #get todays vocabulary




@router.get(
    "/today",
    response_model=list[TodayVocabularyResponse],
)
async def get_today_vocabularies(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)

    vocabularies = (
        db.query(
            UserVocabulary.id,
            UserVocabulary.stage,
            UserVocabulary.next_review_at,
            Vocabulary.word,
            VocabularyLearningContent.bangla_meaning,
            VocabularyLearningContent.example_context,
        )
        .join(
            VocabularyLearningContent,
            UserVocabulary.learning_content_id
            == VocabularyLearningContent.id,
        )
        .join(
            Vocabulary,
            VocabularyLearningContent.vocabulary_id
            == Vocabulary.id,
        )
        .filter(
            UserVocabulary.user_id == user.id,
            UserVocabulary.status == "active",
            UserVocabulary.next_review_at <= now,
        )
        .order_by(
            UserVocabulary.next_review_at.asc()
        )
        .all()
    )

    return vocabularies
 


@router.get("/my", response_model=list[TodayVocabularyResponse])
async def get_my_vocabularies(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (db.query(UserVocabulary.id, UserVocabulary.stage, UserVocabulary.next_review_at, Vocabulary.word, VocabularyLearningContent.bangla_meaning, VocabularyLearningContent.example_context)
        .join(VocabularyLearningContent, UserVocabulary.learning_content_id == VocabularyLearningContent.id)
        .join(Vocabulary, VocabularyLearningContent.vocabulary_id == Vocabulary.id)
        .filter(UserVocabulary.user_id == user.id, UserVocabulary.status == "active")
        .order_by(UserVocabulary.next_review_at.asc()).all())

@router.post(
    "/my/{user_vocabulary_id}/review",
)
async def review_vocabulary(
    user_vocabulary_id: UUID,
    review_data: VocabularyReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user_vocabulary = (
        db.query(UserVocabulary)
        .filter(
            UserVocabulary.id == user_vocabulary_id,
            UserVocabulary.user_id == user.id,
        )
        .with_for_update()
        .first()
    )

    if not user_vocabulary:
        raise HTTPException(
            status_code=404,
            detail="Vocabulary not found",
        )

    if user_vocabulary.status == "mastered":
        raise HTTPException(
            status_code=400,
            detail="Vocabulary is already mastered",
        )

    now = datetime.now(timezone.utc)

    stage_before = user_vocabulary.stage

    if review_data.action == "MASTER":

        user_vocabulary.status = "mastered"
        user_vocabulary.next_review_at = None

        stage_after = stage_before

    else:
        if stage_before < 8:
            stage_after = stage_before + 1
        else:
            stage_after = 8

        interval_days = SRS_INTERVALS[stage_after]

        user_vocabulary.stage = stage_after
        user_vocabulary.next_review_at = (
            now + timedelta(days=interval_days)
        )

    user_vocabulary.last_review_at = now

    review = VocabularyReview(
        user_vocabulary_id=user_vocabulary.id,
        action=review_data.action,
        stage_before=stage_before,
        stage_after=stage_after,
        reviewed_at=now,
    )

    db.add(review)

    try:
        db.commit()
        db.refresh(user_vocabulary)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to review vocabulary",
        )

    return user_vocabulary

from pydantic import BaseModel

class ReadingVocabularySave(BaseModel):
    word: str
    bangla_meaning: str
    example_context: str
    reading_id: UUID

@router.post("/from-reading", response_model=UserVocabularyResponse, status_code=status.HTTP_201_CREATED)
async def save_vocabulary_from_reading(
    data: ReadingVocabularySave,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    word = data.word.strip()
    if not word:
        raise HTTPException(status_code=400, detail="Vocabulary word is required")

    vocabulary = db.query(Vocabulary).filter(Vocabulary.word.ilike(word)).first()
    if not vocabulary:
        vocabulary = Vocabulary(word=word)
        db.add(vocabulary)
        db.flush()

    learning_content = (
        db.query(VocabularyLearningContent)
        .filter(
            VocabularyLearningContent.vocabulary_id == vocabulary.id,
            VocabularyLearningContent.source_type == "reading",
            VocabularyLearningContent.source_id == data.reading_id,
        )
        .first()
    )
    if not learning_content:
        learning_content = VocabularyLearningContent(
            vocabulary_id=vocabulary.id,
            bangla_meaning=data.bangla_meaning,
            example_context=data.example_context,
            source_type="reading",
            source_id=data.reading_id,
        )
        db.add(learning_content)
        db.flush()

    existing = (
        db.query(UserVocabulary)
        .filter(UserVocabulary.user_id == user.id, UserVocabulary.learning_content_id == learning_content.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Vocabulary already saved")

    now = datetime.now(timezone.utc)
    user_vocabulary = UserVocabulary(
        user_id=user.id, learning_content_id=learning_content.id, stage=1,
        next_review_at=now + timedelta(days=SRS_INTERVALS[1]), last_review_at=None, status="active"
    )
    db.add(user_vocabulary)
    db.commit()
    db.refresh(user_vocabulary)
    return user_vocabulary
