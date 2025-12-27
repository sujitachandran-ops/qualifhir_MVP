from src.vector.search import search_loinc
from src.llm.open_source_llm import generate_answer
from src.rules.confidence import calculate_confidence
from src.rules.loinc_validation import is_valid_loinc

def enhance_observation(obs: dict) -> dict:
    enhanced = obs.copy()

    original_loinc = obs.get("original_loinc_code")
    unit = obs.get("unit")

    # 🛑 GUARDRAIL 1: valid LOINC + valid unit → do NOTHING
    if is_valid_loinc(original_loinc) and unit not in [None, "", "{score}"]:
        enhanced.update({
            "recommended_loinc": original_loinc,
            "confidence_score": 1.0,
            "enhancement_required": False,
            "loinc_candidates": [],
            "llm_explanation": "Original LOINC code and unit are valid. No enhancement required."
        })
        return enhanced

    # 🧠 Only now use RAG
    obs_text = (obs.get("original_display") or "")[:80]

    query = f"""
    Observation: {obs_text}
    Value: {obs.get('value')} {unit}
    """

    loinc_candidates = search_loinc(query, top_k=3)

    explanation = generate_answer(obs, loinc_candidates)

    confidence = calculate_confidence(
        loinc_candidates=loinc_candidates,
        original_loinc=original_loinc,
        unit=unit
    )

    enhanced.update({
        "recommended_loinc": loinc_candidates[0]["loinc_num"],
        "confidence_score": confidence,
        "enhancement_required": True,
        "loinc_candidates": loinc_candidates,
        "llm_explanation": explanation
    })

    return enhanced
