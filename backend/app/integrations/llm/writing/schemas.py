from pydantic import BaseModel, Field


class WritingCorrection(BaseModel):
    original: str
    correction: str
    explanation: str


class WritingTakeaway(BaseModel):
    phrase: str
    meaning: str
    example: str


class WritingEvaluationCreate(BaseModel):
    score: int = Field(ge=0, le=100)
    corrections: list[WritingCorrection]
    alternative: str
    takeaways: list[WritingTakeaway]