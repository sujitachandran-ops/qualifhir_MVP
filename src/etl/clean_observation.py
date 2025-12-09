import json

def parse_observation(file_path):
    extracted = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                obs = json.loads(line)
            except json.JSONDecodeError:
                continue  # skip bad lines

            # ensure this is an Observation resource
            if obs.get("resourceType") != "Observation":
                continue

            # extract core fields safely
            coding = (
                obs.get("code", {})
                   .get("coding", [{}])[0]
            )

            value_quantity = obs.get("valueQuantity", {})

            record = {
                "id": obs.get("id"),
                "loinc_code": coding.get("code"),
                "loinc_display": coding.get("display"),
                "value": value_quantity.get("value"),
                "unit": value_quantity.get("unit"),
                "effectiveDateTime": obs.get("effectiveDateTime"),
                "patient_id": obs.get("subject", {}).get("reference", "").replace("Patient/", ""),
                "encounter_id": obs.get("encounter", {}).get("reference", "").replace("Encounter/", "")
            }

            extracted.append(record)

    return extracted


if __name__ == "__main__":
    path = "resources/fhir_raw/Observation.ndjson"
    data = parse_observation(path)
    print("Total observations extracted:", len(data))
    #print(data[:5])  # preview first 5
    print(json.dumps(data[:5], indent=4))