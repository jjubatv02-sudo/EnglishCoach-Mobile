from typing import Literal, Optional
from pydantic import BaseModel, Field


class AttemptRequest(BaseModel):
    session_id: int
    exercise_id: int
    answer: str = Field(min_length=1, max_length=500)


class EvaluationResult(BaseModel):
    meaning_status: Literal["full_match", "mostly_match", "mismatch"]
    grammar_status: Literal["correct", "needs_work"]
    naturalness_status: Literal["natural", "acceptable", "awkward"]
    target_status: Literal["correct", "incorrect", "alternative_valid"]
    error_code: Optional[str] = None
    correction: Optional[str] = None
