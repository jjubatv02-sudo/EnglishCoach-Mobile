from datetime import datetime
from sqlalchemy.orm import Session
from .models import PatternMastery


def update_mastery(db: Session, pattern_id: int, success: bool, first_try: bool, hint_level: int):
    m = db.query(PatternMastery).filter(PatternMastery.pattern_id == pattern_id).first()
    if not m:
        m = PatternMastery(pattern_id=pattern_id, attempt_count=0, first_try_success=0, success_count=0, hint_count=0, mastery_stage="NEW")
        db.add(m)
    m.attempt_count += 1
    if success:
        m.success_count += 1
    if first_try and success:
        m.first_try_success += 1
    if hint_level > 0:
        m.hint_count += 1
    m.last_seen = datetime.utcnow()
    if m.attempt_count >= 5 and m.first_try_success / max(m.attempt_count, 1) >= 0.8:
        m.mastery_stage = "RETRIEVABLE"
    elif m.success_count >= 3:
        m.mastery_stage = "GUIDED"
    elif m.attempt_count >= 1:
        m.mastery_stage = "FAMILIAR"
    db.commit()
