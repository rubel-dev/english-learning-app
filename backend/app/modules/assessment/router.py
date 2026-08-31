﻿﻿﻿﻿﻿from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from backend.app.modules.users.models.user import User
from backend.app.modules.assessment.models.assessment import Assessment
from backend.app.modules.assessment.models.assessment_answer import AssessmentAnswer
from backend.app.modules.assessment.schemas.assessment_result import AssessmentAnswerCreate
from backend.app.modules.assessment.models.assessment_session import AssessmentSession
from backend.app.modules.assessment.models.assessment_result import AssessmentResult
router = APIRouter()

def finalize_assessment(
        db:Session,
        user_id,
        assessment: Assessment
):
    answers = (
        db.query(AssessmentAnswer).filter(
            AssessmentAnswer.user_id == user_id
        )
        .all()
    )
    correct_count = 0
    for answer in answers:
        for page in assessment.content['pages']:
            question = page['question']
            if question['id'] == answer.question_id:
                if question['correct_answer'] == answer.selected_answer:
                    correct_count += 1
                break
    if correct_count <= 1:
        level = 'A1'
    elif correct_count == 2:
        level = 'A2'
    elif correct_count <= 4:
        level = 'B1'
    else:
        level = 'B2'

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.current_level = level

    result = AssessmentResult(
        user_id=user_id,
        assessment_id=assessment.id,
        score=correct_count,
        level=level,
        status='completed'
    )
    db.add(result)

    session = (
        db.query(AssessmentSession).filter(
            AssessmentSession.user_id == user_id,
            AssessmentSession.assessment_id ==assessment.id
        ).first()
    )
    if session:
        db.delete(session)
    db.commit()
    db.refresh(result)
    return result


@router.get("/assessment")
async def get_assessment(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    assessment = db.query(Assessment).first()

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found"
        )

    content = assessment.content

    response = {
        "title": content["title"],
        "pages": []
    }

    for page in content["pages"]:

        question = page["question"]

        page_data = {
            "page_number": page["page_number"],
            "question": {
                "id": question["id"],
                "type": question["type"],
                "passage": question["passage"],
                "question": question["question"],
                "options": question["options"]
            }
        }

        response["pages"].append(page_data)

    return response

@router.get("/assessment/status")
async def assessment_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    result = db.query(AssessmentResult).filter(AssessmentResult.user_id == user.id).first()
    if not result:
        return {"completed": False, "level": None, "status": None}
    return {"completed": True, "level": result.level, "status": result.status}

@router.post('/assessment/start')
async def start_assessment(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    assessment = db.query(Assessment).first()
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail='Assessment not found'
        )
    existing_result = (
        db.query(AssessmentResult).filter(
            AssessmentResult.user_id == user.id,
            AssessmentResult.assessment_id ==assessment.id
        ).first()
    )
    if existing_result:
        raise HTTPException(
            status_code=409,
            detail = "Assessment already completed or skipped"
        )
    old_session = (
        db.query(AssessmentSession).filter(
            AssessmentSession.user_id == user.id,
            AssessmentSession.assessment_id == assessment.id
        ).first()
    )
    if old_session:
        db.delete(old_session)
        db.query(AssessmentAnswer).filter(
            AssessmentAnswer.user_id == user.id
        ).delete()
        db.commit()
    session = AssessmentSession(
        user_id=user.id,
        assessment_id=assessment.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {
        "message":"Assessment started",
        "started_at":session.started_at,
        "duration_minutes":20
    }


@router.post("/assessment/skip")
async def skip_assessment(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    assessment = db.query(Assessment).first()

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found"
        )

     
    existing_result = (
        db.query(AssessmentResult)
        .filter(
            AssessmentResult.user_id == user.id,
            AssessmentResult.assessment_id == assessment.id
        )
        .first()
    )

    if existing_result:
        raise HTTPException(
            status_code=409,
            detail="Assessment already completed or skipped"
        )

    result = AssessmentResult(
        user_id=user.id,
        assessment_id=assessment.id,
        score=None,
        level="A1",
        status="skipped"
    )

    db.add(result)
    user.current_level = "A1"

     
    db.query(AssessmentAnswer).filter(
        AssessmentAnswer.user_id == user.id
    ).delete()

     
    session = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.user_id == user.id,
            AssessmentSession.assessment_id == assessment.id
        )
        .first()
    )

    if session:
        db.delete(session)

    db.commit()

    return {
        "message": "Assessment skipped",
        "level": "A1",
        "status": "skipped"
    }

@router.post("/assessment/answer")
async def submit_answer(
    result_info: AssessmentAnswerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    # Get assessment
    assessment = db.query(Assessment).first()

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Assessment not found"
        )

    # Check active session
    session = (
        db.query(AssessmentSession)
        .filter(
            AssessmentSession.user_id == user.id,
            AssessmentSession.assessment_id == assessment.id
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=400,
            detail="Assessment has not been started"
        )

    # Check timer
    expiry_time = session.started_at + timedelta(minutes=20)

    current_time = datetime.now(session.started_at.tzinfo)

    if current_time >= expiry_time:

        result = finalize_assessment(
            db=db,
            user_id=user.id,
            assessment=assessment
        )

        return {
            "message": "Assessment time expired",
            "score": result.score,
            "level": result.level,
            "status": result.status
        }

    # Check question exists
    question_exists = any(
        page["question"]["id"] == result_info.question_id
        for page in assessment.content["pages"]
    )

    if not question_exists:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    # Check duplicate answer
    existing_answer = (
        db.query(AssessmentAnswer)
        .filter(
            AssessmentAnswer.user_id == user.id,
            AssessmentAnswer.question_id == result_info.question_id
        )
        .first()
    )

    if existing_answer:
        raise HTTPException(
            status_code=409,
            detail="You have already answered this question"
        )

    # Save answer
    assessment_answer = AssessmentAnswer(
        user_id=user.id,
        question_id=result_info.question_id,
        selected_answer=result_info.selected_answer
    )

    db.add(assessment_answer)
    db.commit()
    db.refresh(assessment_answer)

    # If this is question 5 â†’ finish assessment
    if result_info.question_id == 5:

        result = finalize_assessment(
            db=db,
            user_id=user.id,
            assessment=assessment
        )

        return {
            "message": "Assessment completed",
            "score": result.score,
            "level": result.level,
            "status": result.status
        }

    return {
        "message": "Answer submitted successfully",
        "next_question": result_info.question_id + 1
    }

