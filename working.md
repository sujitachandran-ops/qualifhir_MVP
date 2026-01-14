
# 🧠 Overall Flow of QualiFHIR

This section explains **how QualiFHIR works end-to-end**, starting with a **high-level mental model** and then walking through the **detailed execution flow**.

The goal is to make it clear:
- What happens at each stage
- Where AI is used
- Where AI is deliberately NOT used
- Why the system is clinically safe and explainable

---

## 🧩 Core Philosophy

> **QualiFHIR never blindly fixes data.**  
> It validates first, retrieves context only when needed, and uses AI to *explain*, not to override.

QualiFHIR behaves like a **careful clinical reviewer**, not an AI autopilot.

---

## 🧠 Intuitive Mental Model (Visual Thinking)

Think of QualiFHIR as a layered decision system:

```text
Is the clinical data already correct?
↓
Yes → Leave it unchanged
↓
No → Look up similar clinical concepts
↓
Explain the best correction + confidence
```

This mental model applies to **every observation** processed by the system.

---

## 🔁 High-Level Flow (Bird’s-Eye View)

```text
                 ┌──────────────────────────┐
                 │   Raw FHIR Observations   │
                 │        (NDJSON)           │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │   ETL & Structuring       │
                 │ (Extract core fields)     │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │  Rule-Based Validation    │
                 │  (LOINC, Units, Format)  │
                 └─────────────┬────────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐     ┌─────────────────────┐
        │  Data Is Valid    │     │ Enhancement Needed  │
        │  (No AI Used)     │     │ (RAG Triggered)     │
        └─────────┬────────┘     └─────────┬───────────┘
                  │                          │
                  ▼                          ▼
   ┌──────────────────────────┐   ┌──────────────────────────┐
   │ Preserve Original Data   │   │ Semantic Retrieval (RAG)  │
   │ Confidence = 1.0         │   │ FAISS + Embeddings        │
   └─────────────┬────────────┘   └─────────┬────────────────┘
                 │                              │
                 ▼                              ▼
   ┌──────────────────────────┐   ┌──────────────────────────┐
   │        Final Output       │   │ Plain-Text Context        │
   │ (No Modification)        │   │ (Top LOINC Candidates)    │
   └──────────────────────────┘   └─────────┬────────────────┘
                                              │
                                              ▼
                                 ┌──────────────────────────┐
                                 │     LLM Reasoning         │
                                 │  (Explanation Only)      │
                                 └─────────┬────────────────┘
                                              │
                                              ▼
                                 ┌──────────────────────────┐
                                 │   Confidence Scoring      │
                                 │  (Deterministic Rules)   │
                                 └─────────┬────────────────┘
                                              │
                                              ▼
                                 ┌──────────────────────────┐
                                 │    Enhanced Output        │
                                 │ Explainable + Auditable   │
                                 └──────────────────────────┘
```

---

## 🟢 Step 1: Raw Input (FHIR NDJSON)

QualiFHIR starts with **raw FHIR resources**, typically generated by:
- Synthea
- EHR systems
- External data feeds

Examples:
- `Observation.ndjson`
- `Patient.ndjson`

At this stage:
- Codes may be missing or wrong
- Units may be non-standard
- Some data may already be perfect

No assumptions are made.

---

## 🟢 Step 1.2: Vector File Creation (Embedding Index)

Before any semantic matching occurs, QualiFHIR prepares a **vector representation of reference vocabularies** (e.g., LOINC).

### 🔹 Source Data
Structured reference files such as:
- LOINC Json

Each record typically contains:
- Code (e.g., LOINC number)
- Long common name
- Component
- System
- Other descriptive attributes

---

### 🔹 Document Construction

Structured fields are converted into **natural-language documents** by concatenating key attributes.

Example format:
```text
LOINC: <code> | Name: <long_common_name> | Component: <component> | System: <system>
```

This preserves **clinical context** and relationships between fields.

---

### 🔹 Embedding Generation

Each document is passed through a **sentence embedding model** (e.g., `all-MiniLM-L6-v2`) to generate a **dense numerical vector**.

Key properties:
- Fixed-length vector (384 dimensions)
- Encodes semantic meaning
- Similar concepts → closer vectors

---

### 🔹 Vector Index Storage

Generated vectors are stored in a **vector index** (e.g., FAISS / Chroma) along with metadata:
- Code
- Display name
- Component
- System

---

### 🔹 Outcome

At the end of this step:
- Reference vocabularies are vectorized
- Semantic similarity search is enabled
- No patient data is embedded

This step is executed **once per vocabulary version** and reused across pipelines.

---

## 🟢 Step 2: ETL – Extract & Structure

**Purpose:**  
Convert raw FHIR JSON into structured, analyzable records.

What happens:
- Each NDJSON line is parsed
- Core clinical fields are extracted:
  - Observation text
  - LOINC code (if present)
  - Value and unit
  - Effective date/time
- The full original FHIR resource is preserved for traceability

Outcome:
- Structured observation objects
- No data is modified at this stage

---

## 🟢 Step 3: Rule-Based Validation (Safety Layer)

**Purpose:**  
Decide whether AI is even allowed to participate.

Rules check:
- Is the LOINC code syntactically valid?
- Is the unit a standard UCUM unit?
- Is this observation already trustworthy?

Mental question:
> “Do we already trust this data?”

### If the answer is YES:
- No AI is used
- No retrieval is done
- Observation is passed through unchanged
- Confidence score = **1.0**

This prevents:
- Hallucinations
- Accidental corruption of valid data

---

## 🟢 Step 4: Decision Point – Is Enhancement Needed?

At this point, each observation follows **one of two paths**.

### Path A: No Enhancement Required
- Valid LOINC
- Valid unit
- Clear semantics

Result:
- Original data preserved
- AI skipped entirely
- Fully explainable outcome

---

### Path B: Enhancement Required
Triggered when:
- LOINC is missing or invalid
- Unit is irregular (e.g. `{score}`)
- Observation text is free-form or ambiguous

Only in this case does QualiFHIR proceed to RAG.

---

## 🟢 Step 5: Retrieval Phase (RAG – Retrieval Only)

**Purpose:**  
Find **relevant clinical concepts**, not to make decisions.

What happens:
- Observation text is converted into a vector embedding
- FAISS searches a vector index of LOINC concepts
- Top semantically similar LOINC entries are retrieved

Important boundaries:
- Embeddings are used **only for search**
- Embeddings are **never passed to the LLM**
- Retrieval does not decide — it only provides context

Output:
- A small list of candidate LOINC codes with descriptions

---

## 🟢 Step 6: Context Construction (Plain Text)

The retrieved candidates are converted into **human-readable text**.

At this point:
- All vector data is discarded
- Only plain text remains
- This text forms the context for the LLM

This step ensures transparency and traceability.

---

## 🟢 Step 7: LLM Reasoning (Explanation Layer)

**Purpose:**  
Explain which candidate best matches the observation — and why.

The LLM:
- Sees the observation text
- Sees a small set of candidate LOINC descriptions
- Produces a short, natural-language explanation

What the LLM does NOT do:
- It does not see embeddings
- It does not search the database
- It does not invent new codes

The LLM is an **explainer**, not an authority.

---

## 🟢 Step 8: Confidence Scoring (Reality Check)

**Purpose:**  
Quantify how reliable the enhancement is.

Confidence is based on:
- Semantic similarity strength
- Alignment with original code (if any)
- Unit consistency

Result:
- A numeric confidence score (0–1)
- Clear signal for downstream systems
- Low confidence implies review is recommended

This step is deterministic and explainable.

---

## 🟢 Step 9: Final Output (Auditable Result)

Each enhanced observation contains:
- Original data (unchanged)
- Recommended LOINC (if applicable)
- Confidence score
- Explanation
- Flag indicating whether enhancement was applied

Nothing is overwritten.  
Everything is traceable.

---

## 🧠 Why This Flow Is Clinically Safe

- Rules run before AI
- Valid data is never modified
- AI is used only when needed
- Every decision is explainable
- Confidence scores surface uncertainty

This design mirrors **real-world clinical data governance practices**.

---

## ✅ One-Line Summary

```text
Rules protect → Retrieval grounds → LLM explains → Confidence warns
```

This flow ensures QualiFHIR is **accurate, explainable, and production-ready**.

