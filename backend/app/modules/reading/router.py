from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.integrations.llm.reading.explanation import generate_sentence_explanation, generate_vocabulary_explanation
from backend.app.modules.reading.schemas.reading_schema import ReadingAnswerCreate, ReadingExplanationResponse, ReadingStatusCreate, ReadingSubmitCreate, ReadingUserResponse, ReviewDays, TextTypes
from app.db.session import get_db
from app.api.deps import get_current_user
from backend.app.modules.users.models.user import User
from backend.app.modules.assessment.models.assessment_result import AssessmentResult
from backend.app.modules.reading.models.reading import Reading
from backend.app.modules.reading.models.reading_result import ReadingResult
from backend.app.modules.reading.models.reading_session import ReadingSession
from uuid import UUID

from backend.app.modules.reading.models.reading_answer import ReadingAnswer
 
from backend.app.modules.reading.models.global_ai_explanation import GlobalAiExplanation
from openai import OpenAI
from app.core.config import settings
from app.utils.text import extract_sentence

router = APIRouter(
    prefix="/readings",
    tags=["Reading"]
)

@router.get("",response_model = ReadingUserResponse )
async def get_user_reading(
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    assessment_result = db.query(AssessmentResult).filter(
        AssessmentResult.user_id == user.id
    ).first()
    current_level = user.current_level
    print(user.name)
    completed_readings = (
        db.query(ReadingResult.reading_id).filter(
            ReadingResult.user_id == user.id,
            ReadingResult.status.in_([
                "fully_completed",
                "spaced_repetition"
            ])
        ).subquery()
    )
    reading = (
        db.query(Reading)
        .filter(
            Reading.reading_level == current_level,
            ~Reading.id.in_(completed_readings)
        )
        .order_by(func.random())
        .first()
    )
    if not reading:
        raise HTTPException(
            status_code=404,
            detail="No available reading for your level"
        )
    return reading

@router.post('/{reading_id}/start')
async def start_reading(
    reading_id: UUID,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user) 
):
    reading = db.query(Reading).filter(
        Reading.id == reading_id,
        Reading.reading_level == user.current_level
    ).first()
    if not reading:
        raise HTTPException(
            status_code=404,
            detail = "reading not found"
        )
    reading_session = ReadingSession(
        user_id = user.id,
        reading_id = reading.id,
        started_at = datetime.now(timezone.utc)
    
    )
    db.add(reading_session)
    db.commit()
    db.refresh(reading_session)
    return {
        "session_id": reading_session.id,
        "reading_id": reading_session.reading_id,
        "started_at": reading_session.started_at,
        "time_limit":600
    }

@router.post('/{reading_id}/answer')
async def reading_answer(
    reading_id: UUID,
    data: ReadingAnswerCreate, 
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    reading_session = db.query(ReadingSession).filter(
        ReadingSession.id == data.session_id,
        ReadingSession.reading_id == reading_id,
        ReadingSession.user_id == user.id

    ).first()

    if not reading_session:
        raise HTTPException(
            status_code=404,
            detail="reading_session is not found"
        )
    
    now = datetime.now(timezone.utc)
    if now - reading_session.started_at >= timedelta(minutes = 10):
        raise HTTPException(
            status_code=400,
            detail='Reading time has expired'
        )
    question = None 
    for q in reading_session.reading.quiz:
        if q["question_id"] == data.question_id:
            question = q
            break
    if not question:
        raise HTTPException(
            status_code = 404,
            detail = "Question not found"
        )
    if data.selected_answer not in question['options']:
        raise HTTPException(
            status_code=400,
            detail="Invalid answer option"
        )
    
    answer = db.query(ReadingAnswer).filter(
        ReadingAnswer.session_id == data.session_id,
        ReadingAnswer.question_id == data.question_id
    ).first()
    if answer:
        answer.selected_answer = data.selected_answer
    else:
        answer = ReadingAnswer(
            session_id=data.session_id,
            question_id=data.question_id,
            selected_answer=data.selected_answer
        )
        db.add(answer)
    db.commit()


@router.post('/{reading_id}/submit')
async def reading_submit(
    data: ReadingSubmitCreate,
    reading_id: UUID,
    db:Session = Depends(get_db),
    user:User  = Depends(get_current_user),

):
    reading_session = (
        db.query(ReadingSession).filter(
            ReadingSession.id == data.session_id,
            ReadingSession.user_id == user.id,
            ReadingSession.reading_id == reading_id
        ).first()
    )
    if not reading_session:
        raise HTTPException(
            status_code=404,
            detail='Reading session not found'
        )

    reading = db.query(Reading).filter(
        Reading.id == reading_id,
    ).first()

    if not reading:
        raise HTTPException(
            status_code=404,
            detail="reading not found"
        )
    answers = db.query(ReadingAnswer).filter(
        ReadingAnswer.session_id == data.session_id
    ).all()

    correct_count = 0
    
    for answer in answers:
        for x in  reading.quiz:
            if x['question_id'] == answer.question_id:
                if x['correct_answer'] == answer.selected_answer:
                    correct_count+=1 
                break

    reading_result = db.query(ReadingResult).filter(
        ReadingResult.user_id == user.id,
        ReadingResult.reading_id == reading_id
    ).first()
    if reading_result:
        if reading_result.highest_score < correct_count:
            reading_result.highest_score = correct_count
    else: 
        reading_result = ReadingResult(
            user_id = user.id,
            reading_id = reading_id,
            highest_score = correct_count,
            status = 'spaced_repetition',
            first_completed_at = datetime.now(timezone.utc)

        )
        db.add(reading_result) 
    db.commit()
    db.refresh(reading_result)

    result_details = []
    for x in reading.quiz:
        ok = True
        for answer in answers:
            if x['question_id'] == answer.question_id:
                status = "wrong"
                if x['correct_answer'] == answer.selected_answer:
                    status = "correct"
                result_details.append({
                    "question_id":x['question_id'],
                    "answer":x['correct_answer'],
                    "selected_answer": answer.selected_answer,
                    "status":status 
                })
                ok = False
                break
        if ok:
            result_details.append({
                "question_id":x['question_id'],
                "answer":x['correct_answer'],
                "selected_answer":None,
                "status":"unanswered" 
            })  
    return{
        "current_score":correct_count,
        "highest_score":reading_result.highest_score,
        "correct_answer":result_details
    }


#fully completed handle
@router.patch('/review/{reading_id}/mark_complete')
async def reading_status_updated(
    reading_id:UUID,
    data: ReadingStatusCreate,
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    reading_result = db.query(ReadingResult).filter(
        ReadingResult.reading_id == reading_id,
        ReadingResult.user_id == user.id
    ).first()
    if not reading_result:
        raise HTTPException(
            status_code=404,
            detail="reading not found"
        )
    reading_result.status = data.status
    db.commit()
    db.refresh(reading_result)
    return reading_result


#spaced repetition part
@router.get('/review/', response_model=ReadingUserResponse)
async def get_reviews(
    days:ReviewDays, # need to add security here for(3, 7, 30)
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    now = datetime.now(timezone.utc)
    if days == ReviewDays.THREE:
        start = now - timedelta(days = 7)
        end = now - timedelta(days = 3)
    elif days == ReviewDays.SEVEN:
        start = now - timedelta(days = 14)
        end = now - timedelta(days = 7)
    elif days == ReviewDays.FOURTEEN:
        start = now - timedelta(days = 30)
        end = now - timedelta(days = 14)
    else:
        end = now - timedelta(days = 30)
        start = None

    reviews = db.query(ReadingResult.reading_id).filter(
        ReadingResult.user_id == user.id,
        ReadingResult.status =='spaced_repetition', 
        ReadingResult.first_completed_at <= end,
        ReadingResult.first_completed_at > start

    )
    review = db.query(Reading).filter(
        Reading.id.in_(reviews)
    ).order_by(func.random()).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="No review reading at your level"
        )
    return review


#ai explanatioon part started

@router.get("/{reading_id}/explanation", response_model= ReadingExplanationResponse)
async def get_ai_explanations(
    reading_id:UUID,
    selected_text:str,
    type:TextTypes,
    start_position:int = Query(ge = 0),
    end_position:int = Query(ge = 0), 
    db:Session = Depends(get_db),
    user:User = Depends(get_current_user)
):
    
    explanation = db.query(GlobalAiExplanation).filter(
        GlobalAiExplanation.reading_id == reading_id,
        GlobalAiExplanation.type == type,
        GlobalAiExplanation.start_position == start_position,
        GlobalAiExplanation.end_position == end_position
    ).first() 
    if not explanation:
        try:  
            reading = db.query(Reading).filter(
                Reading.id == reading_id
            ).with_for_update().first()

            if not reading:
                raise HTTPException(
                    status_code=404,
                    detail="reading not found"
                )
            explanation = (
                db.query(GlobalAiExplanation)
                .filter(
                    GlobalAiExplanation.reading_id == reading_id,
                    GlobalAiExplanation.type == type,
                    GlobalAiExplanation.start_position == start_position,
                    GlobalAiExplanation.end_position == end_position,
                )
                .first()
            )

        
            if explanation:
                return {
                    "selected_text": explanation.selected_text,
                    "type": explanation.type,
                    "result": explanation.result,
                }
            passage = reading.passage
            if not (start_position < end_position <= len(passage)):
                raise HTTPException(
                    status_code = 400,
                    detail = "Invalid postion range"
                )
            if not (passage[start_position:end_position] == selected_text):
                raise HTTPException(
                    status_code=400,
                    detail="selected text does not macth the given position"
                )
            context = extract_sentence(passage, start_position, end_position) 
            if type =='sentence':
                result = generate_sentence_explanation( 
                    selected_text,
                    
                ) 
            else:
                result = generate_vocabulary_explanation( 
                    selected_text,
                    context
                ) 
                 
            
            ai_explanation = GlobalAiExplanation(
                reading_id=reading_id,
                start_position=start_position,
                end_position=end_position,
                selected_text=selected_text,
                type=type,
                result=result.model_dump()
            )
            db.add(ai_explanation)
            db.commit()
            db.refresh(ai_explanation)
            return ReadingExplanationResponse(
                selected_text=ai_explanation.selected_text,
                type=ai_explanation.type,
                result=ai_explanation.result
            )
        except HTTPException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail = "Falied to generate explanation"
            )
        
    return ReadingExplanationResponse(
        selected_text=explanation.selected_text,
        type=explanation.type,
        result=explanation.result
    )



from pydantic import BaseModel

class UserLevelUpdate(BaseModel):
    level: str

@router.patch("/level")
async def update_reading_level(
    data: UserLevelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    allowed_levels = {"A1", "A2", "B1", "B2"}
    if data.level not in allowed_levels:
        raise HTTPException(status_code=400, detail="Level must be A1, A2, B1, or B2")
    user.current_level = data.level
    db.commit()
    db.refresh(user)
    return {"level": user.current_level}
