from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserVocabularyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    learning_content_id: UUID
    stage: int
    next_review_at: datetime
    last_review_at: datetime | None
    status: str
 

class TodayVocabularyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    word: str
    bangla_meaning: str
    example_context: str

    stage: int
    next_review_at: datetime
    
class VocabularyReviewCreate(BaseModel):
    action: Literal["MASTER", "NOT_MASTER"]