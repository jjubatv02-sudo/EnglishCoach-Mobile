import json, random
from sqlalchemy.orm import Session as DBSession
from .models import Exercise, Session


def create_session(db: DBSession, size: int = 15):
    exercises = db.query(Exercise).all()
    selected = random.sample(exercises, min(size, len(exercises)))
    s = Session(exercise_ids=json.dumps([x.id for x in selected]), current_index=0)
    db.add(s)
    db.commit(); db.refresh(s)
    return s


def current_exercise(db: DBSession, s: Session):
    ids = json.loads(s.exercise_ids)
    if s.current_index >= len(ids):
        return None
    return db.query(Exercise).filter(Exercise.id == ids[s.current_index]).first()
