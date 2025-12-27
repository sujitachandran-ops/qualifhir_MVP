import json
from src.etl.clean_observation import parse_observation
from src.pipeline.enhance_observations import enhance_observation

INPUT = "resources/fhir_raw/Observation_sample.ndjson"
OUTPUT = "outputs/enhanced_observations_sample.json"


observations = parse_observation(INPUT)
#observations = parse_observation(INPUT)[:10]


enhanced_records = []

for obs in observations:
    enhanced = enhance_observation(obs)
    enhanced_records.append(enhanced)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(enhanced_records, f, indent=2)

print(f"✅ Enhanced observations saved to {OUTPUT}")
