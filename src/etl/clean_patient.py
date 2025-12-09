import json

def parse_patient(file_path):
    extracted = []

    # FIX: Force UTF-8 decoding (Windows default cp1252 fails)
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                pat = json.loads(line)
            except json.JSONDecodeError:
                continue

            if pat.get("resourceType") != "Patient":
                continue

            # name extraction
            name = pat.get("name", [{}])[0]
            full_name = " ".join(name.get("given", [])) + " " + name.get("family", "")

            # address
            address = pat.get("address", [{}])[0]

            record = {
                "id": pat.get("id"),
                "name": full_name.strip(),
                "gender": pat.get("gender"),
                "birthDate": pat.get("birthDate"),
                "city": address.get("city"),
                "state": address.get("state"),
                "postalCode": address.get("postalCode"),
                "country": address.get("country")
            }

            extracted.append(record)

    return extracted


if __name__ == "__main__":
    path = "resources/fhir_raw/Patient.ndjson"  # update if needed
    data = parse_patient(path)
    print("Total patients extracted:", len(data))
    #print(data[:5])
    print(json.dumps(data[:5], indent=4))