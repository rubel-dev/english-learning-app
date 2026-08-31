import json

from app.integrations.llm.client import client
from app.integrations.llm.reading.prompts import(
    vocabulary_explanation_prompt,
    sentence_explanation_prompt,
)
from app.integrations.llm.helpers import get_response
from app.integrations.llm.reading.schemas import ReadingSentenceExplanation, ReadingVocabularyExplanation
 

def generate_vocabulary_explanation( 
        selected_text:str,
        context: str | None=None 
):
    prompt = vocabulary_explanation_prompt(selected_text=selected_text, context=context)
    data  = get_response(prompt = prompt)
    schema = ReadingVocabularyExplanation
    return schema.model_validate(data)


def generate_sentence_explanation( 
        selected_text:str, 
):
    prompt = sentence_explanation_prompt(selected_text=selected_text)
    data  = get_response(prompt = prompt)
    schema = ReadingSentenceExplanation
    return schema.model_validate(data)