
from typing import Literal

from pydantic import BaseModel


class AssessmentAnswerCreate(BaseModel):
    question_id:int
    selected_answer: Literal["a", "b","c", "d"]
    