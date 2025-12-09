# qualifhir_MVP
QualiFHIR is an AI-powered enhancement to our existing data processing pipeline that intelligently analyzes, validates, and standardizes clinical data — including identifying and correcting missing or inaccurate clinical data before they are consumed & distributed to downstream applications. This ensures high-quality, interoperable, and reliable data for all downstream applications / consumers.
- Uses LLMs + context-aware algorithms to detect and fix errors
- Automatically corrects wrong/missing clinical data
- Understands semantic meaning of each instance (Observation – Lab data, Procedure – CPT codes, etc) to infer the right mapping
- Provides explainable corrections with a confidence score for every adjustment
- Ensures all data entering the ecosystem is accurate, interoperable, and FHIR-compliant
- Converts raw, fragmented inputs into clean, trustworthy, analytics-ready data for downstream apps

---

# Detailed Workflow

<img width="3848" height="9092" alt="image" src="https://github.com/user-attachments/assets/a934ad77-25f5-4dbe-934a-bbc35f716652" />

---

# Repo Structure

```text
QualiFHIR_MVP/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── resources/
│   ├── config/
│   │   ├── paths.yaml            # file paths (input/output)
│   │   ├── llm.yaml              # LLM model configs
│   │   ├── loinc.yaml            # LOINC rules / mappings
│   │   └── postal.yaml           # ZIP code validation rules
│   │
│   ├── fhir_raw/                 # Raw Synthea NDJSON data
│   │   ├── Patient.ndjson
│   │   ├── Observation.ndjson
│   │   ├── Condition.ndjson
│   │   └── ... (any others)
│   │
│   ├── loinc/
│   │   └── loinc_reference.csv   # LOINC master file
│   │
│   └── postal/
│       └── zipcode_master.csv    # ZIP reference list
│
├── src/
│   ├── etl/                      # Extract + Transform
│   │   ├── clean_patient.py      # NDJSON → Clean patient fields
│   │   ├── clean_observation.py  # NDJSON → Clean observation fields
│   │   ├── clean_condition.py    # optional
│   │   ├── join_data.py          # Join Observation + Patient
│   │   └── save_utils.py         # Save as CSV/Parquet
│   │
│   ├── preprocess/               # Domain-specific cleanup
│   │   ├── normalize_loinc.py    # normalize codes, map irregular LOINC
│   │   ├── fix_zipcodes.py       # validate/correct postal codes
│   │   └── validate_units.py     # optional unit normalization
│   │
│   ├── vector/                   
│   │   ├── build_loinc_index.py  # build FAISS index using loinc.csv
│   │   └── search.py             # vector similarity search
│   │
│   ├── llm/
│   │   ├── llm_client.py         # unified LLM client (OpenAI or local)
│   │   ├── correction_agent.py   # LLM agent for data correction
│   │   └── prompts/
│   │       ├── loinc_cleaning.txt
│   │       ├── observation_cleaning.txt
│   │       └── zipcode_cleaning.txt
│   │
│   ├── rules/                    # Rule-based validation
│   │   ├── loinc_rules.py
│   │   └── postal_rules.py
│   │
│   └── pipeline/
│       ├── pipeline_config.yaml
│       └── run_pipeline.py       # 🚀 MAIN ENTRYPOINT
│
├── vectorstore/
│   └── loinc_index.faiss         # Vector DB artifacts
│
├── outputs/                      # Cleaned final data
│   ├── cleaned_patients.csv
│   ├── cleaned_observations.csv
│   ├── cleaned_conditions.csv
│   └── joined_observation_patient.csv
│
├── scripts/
│   ├── preview_patient.py        # quick debug scripts
│   ├── preview_observation.py
│   └── load_sample_data.py
│
└── tests/
    ├── test_etl.py
    ├── test_loinc.py
    ├── test_zipcodes.py
    └── test_pipeline.py
```