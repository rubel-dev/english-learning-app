
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.app.modules.listening.models.listening import ListeningLevel, ListeningType

class ListeningQuestionResponse(BaseModel):
    id:int
    question:str
    options:list[str]

class ListeningSegmentResponse(BaseModel):
    id:int
    start:float
    end: float

class ListeningResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str | None
    embedded_link:str
    type: ListeningType
    level: ListeningLevel | None
    questions: list[ListeningQuestionResponse] | None
    segments : list[ListeningSegmentResponse] | None

class ListeningListResponse(BaseModel):
    items: list[ListeningResponse]
    page: int
    limit: int
    total: int