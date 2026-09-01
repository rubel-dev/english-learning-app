 
from app.modules.listening.models.listening import Listening
from app.modules.listening import repository

def listening_create(db, data):

    listening = Listening(
        title = data.title,
        description = data.description,
        embedded_link = data.embedded_link,
        type = data.type,
        level = data.level,
        questions = [
            question.model_dump() for question in data.questions
        ] if data.questions else None,
        segments = [
            segment.model_dump()
            for segment in data.segments 
        ] if data.segments else None,

    )
    return repository.create_listening(listening = listening, db = db)


def get_list(
        db,
        type = None,
        level = None,
        page = 1,
        limit = 10
):
    offset = (page - 1) * limit
    items, total = repository.get_listenings(
        db=db,
        type=type,
        level=level,
        offset=offset,
        limit=limit
    )
    return {
        "items":items,
        "page":page,
        "limit": limit,
        "total": total
    }

def get_by_id(db, listening_id):
    listening = repository.get_by_id(db = db, listening_id= listening_id)
    if not listening:
        raise ValueError("Listening not found")
    return  listening