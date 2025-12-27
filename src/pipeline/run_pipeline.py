import yaml
from src.etl.clean_patient import parse_patient
from src.etl.clean_observation import parse_observation
from src.vector.search import search_loinc
from src.llm.open_source_llm import generate_answer

def main():
    with open("resources/config/paths.yaml") as f:
        config = yaml.safe_load(f)

    patients = parse_patient(config["raw_data"]["patients"])
    observations = parse_observation(config["raw_data"]["observations"])

    print(f"Patients loaded: {len(patients)}")
    print(f"Observations loaded: {len(observations)}")

    query = "fasting blood glucose"
    loinc_matches = search_loinc(query, top_k=5)

    response = generate_answer(query, loinc_matches)
    print("\n=== FINAL RAG OUTPUT ===\n")
    print(response)

if __name__ == "__main__":
    main()
