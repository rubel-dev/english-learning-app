def vocabulary_explanation_prompt(
        selected_text: str,
        context: str | None,
):
    prompt = f"""
    You are an English learning assistant.
    
    The user selected the word:
    
    "{selected_text}"
    
    The word appears in this sentence:
    
    "{context}"
    
    Give the most appropriate Bangla meaning of the word according to this context.
    
    Also give one short Bangla explanation to clarify the contextual meaning.
    
    Do NOT provide unrelated meanings.
    Keep the response concise.
    
    Return ONLY valid JSON.
    Do not use markdown.
    Do not use ```json.
    Do not add any text outside the JSON.
    
    Use exactly this structure:
    
    {{
        "bangla_meaning": "...",
        "bangla_explanation": "..."
    }}
    """
    return prompt


def sentence_explanation_prompt(
        selected_text: str
):
    prompt = f"""
    You are an English learning assistant.

    The user selected this sentence:

    "{selected_text}"

    Help the learner understand this sentence easily.

    Return:
    1. A natural Bangla meaning of the whole sentence.
    2. Break the sentence into meaningful chunks.
    3. Give a simple Bangla meaning for each chunk.

    Do NOT explain every word individually.
    Do NOT create unnecessary chunks.
    Focus on helping the learner understand the sentence structure and meaning.

    Return ONLY valid JSON.
    Do not use markdown.
    Do not use ```json.
    Do not add any text outside the JSON.

    Use exactly this structure:

    {{
        "bangla_meaning": "...",
        "breakdown": [
            {{
                "part": "...",
                "meaning": "..."
            }}
        ]
    }}
    """
    return prompt