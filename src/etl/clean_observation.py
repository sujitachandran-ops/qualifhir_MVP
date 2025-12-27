import json
from typing import List, Dict

def parse_observation(file_path):
    records = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            obs = json.loads(line)

            if obs.get("resourceType") != "Observation":
                continue

            coding = obs.get("code", {}).get("coding", [{}])[0]
            value = obs.get("valueQuantity", {})

            records.append({
                "observation_id": obs.get("id"),
                "original_loinc_code": coding.get("code"),
                "original_display": coding.get("display"),
                "value": value.get("value"),
                "unit": value.get("unit"),
                "ucum_code": value.get("code"),
                "effective_datetime": obs.get("effectiveDateTime"),
                "raw_observation": obs  # full traceability
            })

    return records
