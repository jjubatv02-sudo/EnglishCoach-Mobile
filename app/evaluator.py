import re
from .schemas import EvaluationResult


def norm(text: str) -> str:
    text = text.strip().lower().replace("’", "'")
    text = re.sub(r"[.!?]+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def evaluate(answer: str, reference: str, pattern_code: str) -> EvaluationResult:
    a, r = norm(answer), norm(reference)
    if a == r:
        return EvaluationResult(meaning_status="full_match", grammar_status="correct", naturalness_status="natural", target_status="correct")

    # Small deterministic evaluator for Prototype A. AI replaces/augments this in the next build.
    rules = {
        "WANT_TO": (r"\bi want (?!to\b)", "MISSING_INFINITIVE_TO", "I want to + verb"),
        "NEED_TO": (r"\bi need (?!to\b)", "MISSING_INFINITIVE_TO", "I need to + verb"),
        "HAVE_TO": (r"\bi have (?!to\b)", "MISSING_HAVE_TO", "I have to + verb"),
    }
    if pattern_code in rules:
        rx, code, correction = rules[pattern_code]
        if re.search(rx, a):
            return EvaluationResult(meaning_status="mostly_match", grammar_status="needs_work", naturalness_status="awkward", target_status="incorrect", error_code=code, correction=correction)

    alternatives = {
        "WANT_TO": ["i'd like to", "i would like to"],
        "CAN": ["i'm able to", "i am able to"],
    }
    if any(a.startswith(x) for x in alternatives.get(pattern_code, [])):
        return EvaluationResult(meaning_status="full_match", grammar_status="correct", naturalness_status="natural", target_status="alternative_valid")

    # A few important modality/negation mismatches for the first prototype.
    if pattern_code == "WANT_TO" and (a.startswith("i have to") or a.startswith("i need to") or a.startswith("i don't want to")):
        return EvaluationResult(meaning_status="mismatch", grammar_status="correct", naturalness_status="natural", target_status="incorrect", error_code="MEANING_MISMATCH", correction=reference)
    if pattern_code == "HAVE_TO" and a.startswith("i want to"):
        return EvaluationResult(meaning_status="mismatch", grammar_status="correct", naturalness_status="natural", target_status="incorrect", error_code="MODALITY_MISMATCH", correction=reference)

    # Prototype fallback: not enough semantic intelligence yet, so mark for guided correction.
    return EvaluationResult(meaning_status="mostly_match", grammar_status="needs_work", naturalness_status="acceptable", target_status="incorrect", error_code="NEEDS_GUIDED_REVIEW", correction=reference)
