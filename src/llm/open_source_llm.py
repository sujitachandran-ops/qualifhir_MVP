from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

MAX_INPUT_TOKENS = 480  # leave buffer for safety

def generate_answer(observation: dict, loinc_matches: list) -> str:
    context = "\n".join(
        [
            f"{m['loinc_num']} - {m['long_common_name'][:60]}"
            for m in loinc_matches
        ]
    )

    prompt = f"""
FHIR Observation:
Test: {observation['original_display'][:80]}
Value: {observation['value']} {observation['unit']}

Candidate LOINC Codes:
{context}

Task:
Select the best LOINC code and explain briefly.
"""

    # Tokenize with truncation
    tokens = tokenizer(
        prompt,
        truncation=True,
        max_length=MAX_INPUT_TOKENS,
        return_tensors="pt"
    )

    # Generate with model
    output_ids = model.generate(
        tokens["input_ids"],
        max_new_tokens=256,
        num_beams=1
    )

    return tokenizer.decode(output_ids[0], skip_special_tokens=True)
