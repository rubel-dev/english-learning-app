from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.modules.users.models.user import User
from backend.app.modules.writing.models.user_writing_state import UserWritingState
from backend.app.modules.writing.models.writing import Writing
from backend.app.modules.writing.models.writing_evaluation import WritingEvaluation
from backend.app.modules.writing.models.writing_submission import WritingSubmission
from backend.app.integrations.llm.writing.explanation import generate_writing_evaluation


router = APIRouter(
    prefix="/writing",
    tags=["Writing"],
)


class WritingAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)


@router.get("")
async def get_writing(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    completed_writings = db.query(
        UserWritingState.writing_id
    ).filter(
        UserWritingState.state == "completed",
        UserWritingState.user_id == user.id,
    ).subquery()

    writing = db.query(Writing).filter(
        Writing.level == user.current_level,
        ~Writing.id.in_(completed_writings),
    ).order_by(
        func.random()
    ).first()

    if not writing:
        if user.current_level == "B2":
            return "Congratulations! You have completed all writing exercises."

        return "All writings for your current level are completed. Try another level."

    return writing


@router.post("/{writing_id}/answer")
async def writing_answer(
    writing_id: UUID,
    payload: WritingAnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1. Check writing exists
    writing = db.query(Writing).filter(
        Writing.id == writing_id
    ).first()

    if not writing:
        raise HTTPException(
            status_code=404,
            detail="Writing not found",
        )

    # 2. Check level
    if writing.level != user.current_level:
        raise HTTPException(
            status_code=403,
            detail="This writing is not available",
        )

    # 3. Check user's writing state
    user_writing_state = db.query(UserWritingState).filter(
        UserWritingState.user_id == user.id,
        UserWritingState.writing_id == writing.id,
    ).first()

    if (
        user_writing_state
        and user_writing_state.state == "completed"
    ):
        raise HTTPException(
            status_code=409,
            detail="You have already completed this writing",
        )

    # 4. Save submission first
    answer_submission = WritingSubmission(
        user_id=user.id,
        writing_id=writing.id,
        answer=payload.answer,
    )

    db.add(answer_submission)
    db.commit()
    db.refresh(answer_submission)

    # 5. Mark writing as completed
    if user_writing_state:
        user_writing_state.state = "completed"
    else:
        user_writing_state = UserWritingState(
            user_id=user.id,
            writing_id=writing.id,
            state="completed",
        )
        db.add(user_writing_state)

    db.commit()

    # 6. LLM evaluation
    try:
        result = generate_writing_evaluation(
            answer=answer_submission.answer,
            prompt_text=writing.prompt,
        )

        # 7. Save evaluation
        evaluation = WritingEvaluation(
            writing_submission_id=answer_submission.id,
            score=result.score,
            corrections=[
                item.model_dump()
                for item in result.corrections
            ],
            alternative=result.alternative,
            takeaways=[
                item.model_dump()
                for item in result.takeaways
            ],
        )

        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        return {
            "submission": answer_submission,
            "evaluation": evaluation,
        }

    except Exception:
        db.rollback()

        return {
            "submission": answer_submission,
            "evaluation": None,
            "message": "Your answer was saved, but evaluation is temporarily unavailable.",
        }
    
