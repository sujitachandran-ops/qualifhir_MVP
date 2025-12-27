import json
import random

INPUT = "resources/fhir_raw/Observation.ndjson"
OUTPUT = "resources/fhir_raw/Observation_sample.ndjson"

glucose = []
vitals = []
pain = []

with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        obs = json.loads(line)
        display = obs.get("code", {}).get("coding", [{}])[0].get("display", "").lower()

        if "glucose" in display:
            glucose.append(obs)
        elif "height" in display or "weight" in display:
            vitals.append(obs)
        elif "pain" in display:
            pain.append(obs)

# Pick small samples
sample = (
    random.sample(glucose, min(3, len(glucose))) +
    random.sample(vitals, min(3, len(vitals))) +
    random.sample(pain, min(2, len(pain)))
)

# 🔥 INTENTIONALLY BREAK some glucose records
for obs in sample:
    display = obs.get("code", {}).get("coding", [{}])[0].get("display", "").lower()
    if "glucose" in display:
        obs["code"]["coding"][0]["code"] = "XXXX-INVALID"
        obs["code"]["coding"][0]["display"] = "Blood sugar level"

# Write NDJSON
with open(OUTPUT, "w", encoding="utf-8") as f:
    for obs in sample:
        f.write(json.dumps(obs) + "\n")

print(f"✅ Sample file created with {len(sample)} observations:")
print(f"➡ {OUTPUT}")
