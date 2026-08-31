import json

from app.integrations.llm.client import client 

def get_response(prompt):
    response = client.chat.completions.create(
                model="gemini-3.6-flash",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        
    raw_content = response.choices[0].message.content
    raw_content = raw_content.strip()

    if raw_content.startswith("```json"):
        raw_content = raw_content[7:]

    if raw_content.endswith("```"):
        raw_content = raw_content[:-3]

    raw_content = raw_content.strip()

    data = json.loads(raw_content)
     
    data = json.loads(raw_content)
    return data