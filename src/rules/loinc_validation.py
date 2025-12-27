def is_valid_loinc(code: str) -> bool:
    if not code:
        return False
    return "-" in code and code.split("-")[1].isdigit()

def is_standard_unit(unit: str) -> bool:
    return unit not in ["{score}", None, ""]
