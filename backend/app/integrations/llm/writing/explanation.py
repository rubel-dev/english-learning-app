

from sqlalchemy import text

from app.integrations.llm.helpers import get_response
from app.integrations.llm.writing.prompts import writing_evaluation_prompt
from app.integrations.llm.writing.schemas import WritingEvaluationCreate

def generate_writing_evaluation(
        answer:text,
        prompt_text:text
):
    prompt = writing_evaluation_prompt(
        answer = answer,
        prompt_text = prompt_text
    )
    data = get_response(prompt)
    schema = WritingEvaluationCreate
    return schema.model_validate(data)
