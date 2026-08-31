
from enum import IntEnum, StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict , Field

class ReadingQuestion(BaseModel):
    question_id: str
    question: str
    options: list[str]
    correct_answer:str
class ReadingCreate(BaseModel):
    title: str = Field(max_length=100)
    passage: str
    reading_level: str
    topic: str = Field(max_length=100)
    estimated_reading_time: int = Field(gt = 0)
    quiz: list[ReadingQuestion] = Field(min_length=5, max_length=5)

class ReadingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    passage: str | None = Field(default=None, min_length=1)
    reading_level: str | None = None
    topic: str | None = Field(default=None, min_length=1, max_length=100)
    estimated_reading_time: int | None = Field(default=None, gt = 0)
    quiz: list[ReadingQuestion] | None = Field(
        default=None,
        min_length=5,
        max_length=5
    )
 

class ReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    passage: str
    reading_level: str
    topic: str
    estimated_reading_time: int
    quiz: list[ReadingQuestion]

class ReadingQuestionResponse(BaseModel):
    question_id: str
    question: str
    options: list[str]

class ReadingUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    passage: str
    reading_level: str
    topic: str
    estimated_reading_time: int
    quiz: list[ReadingQuestionResponse]

class ReadingAnswerCreate(BaseModel):
    session_id: UUID
    question_id: str
    selected_answer:str

class ReadingSubmitCreate(BaseModel):
    session_id: UUID
    
class ReadingStatusCreate(BaseModel):
    status: str
class ReviewDays(IntEnum):
    THREE = 3
    SEVEN = 7
    FOURTEEN = 14
    THIRTY = 30

class TextTypes(StrEnum):
    VOCABULARY = "vocabulary"
    SENTENCE = "sentence"
    PASSAGE = "passage"




