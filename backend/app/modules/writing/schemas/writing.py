from pydantic import BaseModel, Field


class WritingAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)