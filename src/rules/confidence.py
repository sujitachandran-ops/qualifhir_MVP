def calculate_confidence(
    loinc_candidates: list,
    original_loinc: str,
    unit: str
) -> float:
    # 1️⃣ Retrieval score
    best_distance = loinc_candidates[0]["score"]
    retrieval_score = 1 / (1 + best_distance)

    # 2️⃣ LOINC agreement score
    loinc_codes = [c["loinc_num"] for c in loinc_candidates]

    if original_loinc == loinc_codes[0]:
        loinc_match_score = 1.0
    elif original_loinc in loinc_codes:
        loinc_match_score = 0.7
    else:
        loinc_match_score = 0.4

    # 3️⃣ Unit quality score
    if unit in [None, ""]:
        unit_score = 0.3
    elif unit == "{score}":
        unit_score = 0.6
    else:
        unit_score = 1.0

    confidence = (
        0.6 * retrieval_score +
        0.2 * loinc_match_score +
        0.2 * unit_score
    )

    return round(confidence, 3)
