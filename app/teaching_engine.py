from .schemas import EvaluationResult


def decide(ev: EvaluationResult, attempt_number: int, hint1: str, hint2: str, reference: str):
    if ev.meaning_status == "full_match" and ev.grammar_status == "correct" and ev.target_status == "correct":
        return {"result": "pass", "message": "좋아요.", "retry_required": False, "hint_level": 0}
    if ev.target_status == "alternative_valid":
        return {"result": "pass_note", "message": "자연스럽고 의미도 맞아요. 오늘 목표 표현과 다른 좋은 표현을 사용했습니다.", "retry_required": False, "hint_level": 0}
    if attempt_number == 1:
        return {"result": "retry", "message": hint1, "retry_required": True, "hint_level": 1}
    if attempt_number == 2:
        return {"result": "retry", "message": hint2, "retry_required": True, "hint_level": 2}
    return {"result": "retry", "message": f"정답 예시: {reference}\n이제 정답을 보지 않고 직접 다시 입력해보세요.", "retry_required": True, "hint_level": 3}
