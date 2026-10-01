from datetime import datetime
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as DBSession

from .database import Base, engine, SessionLocal, get_db
from .models import Attempt, Exercise, Pattern, PatternMastery, Session
from .schemas import AttemptRequest
from .seed import seed_database
from .evaluator import evaluate
from .teaching_engine import decide
from .mastery_engine import update_mastery
from .session_engine import create_session, current_exercise

app = FastAPI(title="EnglishCoach Mobile v0.2")
STATIC = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "app": "EnglishCoach_Mobile_v0.2"}


@app.post("/api/session/start")
def start(db: DBSession = Depends(get_db)):
    s = create_session(db)
    ex = current_exercise(db, s)
    return {"session_id": s.id, "exercise": exercise_payload(db, ex), "index": 1, "total": len(__import__('json').loads(s.exercise_ids))}


def exercise_payload(db, ex):
    p = db.query(Pattern).filter(Pattern.id == ex.pattern_id).first()
    return {"id": ex.id, "prompt_ko": ex.prompt_ko, "pattern": p.canonical_form, "pattern_code": p.code}


@app.post("/api/attempt")
def submit(req: AttemptRequest, db: DBSession = Depends(get_db)):
    s = db.query(Session).filter(Session.id == req.session_id).first()
    ex = db.query(Exercise).filter(Exercise.id == req.exercise_id).first()
    if not s or not ex:
        raise HTTPException(404, "Session or exercise not found")
    p = db.query(Pattern).filter(Pattern.id == ex.pattern_id).first()
    previous = db.query(Attempt).filter(Attempt.session_id == s.id, Attempt.exercise_id == ex.id).count()
    n = previous + 1
    ev = evaluate(req.answer, ex.reference_answer, p.code)
    teaching = decide(ev, n, ex.hint_1, ex.hint_2, ex.reference_answer)
    success = teaching["result"] in ("pass", "pass_note")
    att = Attempt(session_id=s.id, exercise_id=ex.id, attempt_number=n, user_answer=req.answer,
                  result=teaching["result"], error_code=ev.error_code, hint_level=teaching["hint_level"], success=success)
    db.add(att); db.commit()
    update_mastery(db, p.id, success, n == 1, teaching["hint_level"])
    return {"evaluation": ev.model_dump(), "teaching": teaching, "reference": ex.reference_answer if teaching["hint_level"] >= 3 else None}


@app.post("/api/session/{session_id}/next")
def next_exercise(session_id: int, db: DBSession = Depends(get_db)):
    s = db.query(Session).filter(Session.id == session_id).first()
    if not s:
        raise HTTPException(404, "Session not found")
    import json
    ids = json.loads(s.exercise_ids)
    s.current_index += 1
    if s.current_index >= len(ids):
        s.ended_at = datetime.utcnow(); db.commit()
        return {"done": True, "summary": summary_data(db, s)}
    db.commit()
    ex = current_exercise(db, s)
    return {"done": False, "exercise": exercise_payload(db, ex), "index": s.current_index + 1, "total": len(ids)}


def summary_data(db, s):
    attempts = db.query(Attempt).filter(Attempt.session_id == s.id).all()
    exercise_ids = {a.exercise_id for a in attempts}
    first_success = sum(1 for eid in exercise_ids if any(a.success and a.attempt_number == 1 for a in attempts if a.exercise_id == eid))
    recovered = sum(1 for eid in exercise_ids if any(a.success and a.attempt_number > 1 for a in attempts if a.exercise_id == eid))
    return {"attempts": len(attempts), "exercises": len(exercise_ids), "first_try_success": first_success, "hint_recovery": recovered}


@app.get("/api/progress")
def progress(db: DBSession = Depends(get_db)):
    rows = db.query(PatternMastery).all()
    out = []
    for m in rows:
        p = db.query(Pattern).filter(Pattern.id == m.pattern_id).first()
        out.append({"pattern": p.canonical_form, "stage": m.mastery_stage, "attempts": m.attempt_count, "successes": m.success_count})
    return out


@app.get("/api/debug/attempts")
def debug_attempts(db: DBSession = Depends(get_db)):
    rows = db.query(Attempt).order_by(Attempt.id.desc()).limit(50).all()
    return [{"id": a.id, "session": a.session_id, "exercise": a.exercise_id, "n": a.attempt_number,
             "answer": a.user_answer, "result": a.result, "error": a.error_code, "hint": a.hint_level} for a in rows]
