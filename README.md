# QualiFHIR_MVP

**QualiFHIR** is an AI-powered data quality and standardization layer for healthcare data pipelines.  
It intelligently analyzes, validates, and enhances clinical data (FHIR resources) before they are consumed by downstream systems.

QualiFHIR combines **rule-based validation**, **semantic vector search**, and **LLM reasoning** to ensure clinical data is:

- Accurate  
- Interoperable  
- Explainable  
- FHIR-compliant  
- Analytics-ready  

---

## 🚀 What Problems Does QualiFHIR Solve?

Healthcare data often suffers from:

- Missing or incorrect clinical codes (LOINC, CPT, etc.)
- Non-standard units (e.g. `{score}`)
- Free-text or ambiguous observations
- Inconsistent demographic / postal data
- Low explainability when automated corrections are applied

**QualiFHIR fixes these problems safely and transparently.**

---

## ✨ Key Capabilities

- 🔍 Detects missing, invalid, or inconsistent clinical data  
- 🧠 Uses semantic understanding (vector search + LLMs) instead of brittle string matching  
- 🧪 Applies rule-based guardrails to avoid corrupting valid data  
- 🤖 Uses LLMs only when needed (fallback, not override)  
- 📊 Produces explainable corrections with a confidence score  
- 🧾 Preserves original data for auditability  
- 🧱 Designed to scale to millions of records  

---

## 🧠 High-Level Architecture

```text
FHIR NDJSON (raw)
        ↓
ETL (clean + normalize)
        ↓
Rule-based validation
        ↓
Semantic retrieval (FAISS)
        ↓
LLM reasoning (only if needed)
        ↓
Enhanced + standardized output

```

> **Design Principle**  
> Rules first → RAG only when rules fail → LLM explains decisions.

---

## 📁 Repository Structure

```text
qualifhir_MVP/
│
├── README.md
├── requirements.txt
├── faiss_implementation.txt
│
├── resources/
│   ├── config/
│   │   ├── paths.yaml
│   │   └── pipeline.yaml
│   │
│   ├── fhir_raw/
│   │   ├── Patient.ndjson
│   │   ├── Observation.ndjson
│   │   └── Observation_sample.ndjson
│   │
│   ├── loinc/
│   │   └── loinc_output.json
│   │
│   ├── LoincTableCore.csv
│   └── zip_code_database.csv
│
├── src/
│   ├── etl/
│   │   ├── clean_observation.py
│   │   └── clean_patient.py
│   │
│   ├── ingestion/
│   │   └── fetch_loinc_catalog.py
│   │
│   ├── llm/
│   │   └── open_source_llm.py
│   │
│   ├── rules/
│   │   ├── loinc_validation.py
│   │   └── confidence.py
│   │
│   ├── vector/
│   │   ├── build_loinc_index.py
│   │   └── search.py
│   │
│   ├── pipeline/
│   │   ├── run_pipeline.py
│   │   ├── run_enhancement.py
│   │   └── enhance_observations.py
│   │
│   └── utils/
│       └── create_observation_sample.py
│
├── vectorstore/
│   ├── index_loinc_path.faiss
│   └── loinc_metadata.pkl
│
└── outputs/
    ├── enhanced_observations.json
    └── enhanced_observations_sample.json
```

---

## ⚙️ Setup Instructions

This section explains how to set up QualiFHIR locally from scratch and run the pipeline step by step.

---

## 1️⃣ Prerequisites

Before you begin, make sure you have:

- **Python 3.9 – 3.11** (recommended)
- Windows / macOS / Linux
- Minimum **8 GB RAM** (16 GB recommended for smoother LLM inference)
- Internet access (for first-time model downloads)

Check Python version:

```bash
python --version
```

## 2️⃣ Clone the Repository

```bash
git clone https://github.com/<your-org>/qualifhir_MVP.git
cd qualifhir_MVP
```

## 3️⃣ Create a Virtual Environment (Recommended)

Using a virtual environment avoids dependency conflicts.

Windows
```bash
python -m venv venv
venv\Scripts\activate
```
macOS / Linux
```bash
python -m venv venv
source venv/bin/activate
```

## 4️⃣ Install Dependencies

Upgrade pip and install required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Required Packages

```text
requests
pyyaml
pandas
numpy
faiss-cpu
sentence-transformers
transformers
torch
accelerate
```

- ⚠️ First install may take a few minutes due to torch and transformers.


## 5️⃣ Verify Installation (Optional but Recommended)

Run this quick sanity check:

```bash
python - <<EOF
import yaml, pandas, numpy, faiss, torch
from sentence_transformers import SentenceTransformer
print("✅ All core dependencies imported successfully")
EOF
```

## 6️⃣ Prepare Reference Data

Ensure the following files exist:

```text
resources/
├── fhir_raw/
│   └── Observation.ndjson
├── loinc/
│   └── loinc_output.json
```

- These are required for building the vector index and running the pipeline.

## 7️⃣ Build the LOINC Vector Index (ONE-TIME STEP)

QualiFHIR uses FAISS for semantic LOINC matching.

Run:
```bash
python src/vector/build_loinc_index.py
```

This generates:

```text
vectorstore/
└── loinc_index.faiss
```

- ℹ️ Re-run this step only if the LOINC reference file changes.


## 8️⃣ Create a Small Test Dataset (Recommended for Development)

Instead of processing 20k+ observations during testing, create a small controlled sample.
```bash
python src/utils/create_observation_sample.py
```

This creates:

```text
resources/fhir_raw/Observation_sample.ndjson
```

- The sample intentionally includes:
    - Valid observations (height, weight)
    - Irregular units (pain score)
    - Broken glucose LOINC codes (for testing corrections)


## 9️⃣ Run the Enhancement Pipeline (Main Execution)

From the project root:
```bash
python -m src.pipeline.run_enhancement
```

- What happens internally: 
    * Reads FHIR Observation NDJSON
    * Applies rule-based validation
    * Uses semantic search only when required
    * Invokes the LLM for explanation
    * Calculates a confidence score
    * Writes enhanced output

## 🔟 Output Location

The enhanced results are written to:
```text
outputs/
└── enhanced_observations.json
```
---
