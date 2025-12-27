import json
from typing import List, Dict

def parse_patient(file_path: str) -> List[Dict]:
    records = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                pat = json.loads(line)
            except json.JSONDecodeError:
                continue

            if pat.get("resourceType") != "Patient":
                continue

            name = pat.get("name", [{}])[0]
            address = pat.get("address", [{}])[0]

            records.append({
                "patient_id": pat.get("id"),
                "name": f"{' '.join(name.get('given', []))} {name.get('family', '')}".strip(),
                "gender": pat.get("gender"),
                "birth_date": pat.get("birthDate"),
                "city": address.get("city"),
                "state": address.get("state"),
                "postal_code": address.get("postalCode"),
                "country": address.get("country")
            })

    return records
