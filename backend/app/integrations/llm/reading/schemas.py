#llm validation schema
from enum import StrEnum

from pydantic import BaseModel

class TextTypes(StrEnum):
    VOCABULARY = "vocabulary"
    SENTENCE = "sentence"
    PASSAGE = "passage"
    
class ReadingExplanationBreakdown(BaseModel):
    part:str
    meaning:str

class ReadingSentenceExplanation(BaseModel):
    bangla_meaning: str
    breakdown:list[ReadingExplanationBreakdown]

class ReadingVocabularyExplanation(BaseModel):
    bangla_meaning: str
    bangla_explanation: str
class ReadingExplanationResponse(BaseModel):
    selected_text: str
    type: TextTypes
    result: ReadingVocabularyExplanation | ReadingSentenceExplanation
