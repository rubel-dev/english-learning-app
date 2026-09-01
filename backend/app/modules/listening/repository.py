from sqlalchemy import func, select

from app.modules.listening.models.listening import Listening


def create_listening(listeing, db):
    db.add(listeing)
    db.commit()
    db.refresh(listeing)
    return listeing

def get_list(
        db,
        type=None,
        level=None,
        offset=0,
        limit=10
):
    query = select(Listening)
    if type is not None:
        query = query.where(Listening.type == type)
    if level is not None:
        query = query.where(Listening.type == level)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(count_query) or 0
    query = (
        query
        .order_by(Listening.id)
        .offset(offset)
        .limit(limit) 
    )
    items = list(db.scalars(query).all())
    return items, total

    

def get_by_id(db, listening_id):
    query = select(Listening).where(
        Listening.id == listening_id
    )
    return db.scalar(query)