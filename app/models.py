from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from .database import Base


class Pattern(Base):
    __tablename__ = "patterns"
    id = Column(Integer, primary_key=True)
    code = Column(String(40), unique=True, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    canonical_form = Column(String(120), nullable=False)
    function = Column(String(80), nullable=False)


class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), nullable=False)
    prompt_ko = Column(String(300), nullable=False)
    reference_answer = Column(String(300), nullable=False)
    hint_1 = Column(String(300), nullable=False)
    hint_2 = Column(String(300), nullable=False)
    difficulty = Column(Float, default=1.0)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    current_index = Column(Integer, default=0)
    exercise_ids = Column(Text, nullable=False)


class Attempt(Base):
    __tablename__ = "attempts"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    user_answer = Column(Text, nullable=False)
    result = Column(String(40), nullable=False)
    error_code = Column(String(80), nullable=True)
    hint_level = Column(Integer, default=0)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PatternMastery(Base):
    __tablename__ = "pattern_mastery"
    id = Column(Integer, primary_key=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id"), unique=True, nullable=False)
    attempt_count = Column(Integer, default=0)
    first_try_success = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    hint_count = Column(Integer, default=0)
    mastery_stage = Column(String(30), default="NEW")
    last_seen = Column(DateTime, nullable=True)
