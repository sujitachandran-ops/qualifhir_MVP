# Confidence Score Calculation

This document explains how the **confidence score** is calculated for LOINC mapping using
vector similarity, LOINC agreement, and unit validation.

---

## Overview

The confidence score is a normalized value between **0.0 and 1.0** that represents how reliable
a recommended LOINC mapping is.

The score is derived from three independent signals:

1. **Vector retrieval similarity**
2. **LOINC code agreement**
3. **Unit quality validation**

Each signal contributes a weighted portion to the final confidence.

---

## Inputs

| Parameter | Description |
|--------|------------|
| `loinc_candidates` | List of candidate LOINC mappings returned from vector search, ordered by similarity |
| `original_loinc` | Original or existing LOINC code (if available) |
| `unit` | Unit associated with the observation |

---

## 1. Vector Retrieval Score (60%)

### What it measures
Semantic similarity between the observation text and LOINC descriptions using embeddings.

The vector search returns a **distance value**, where:

- **Lower distance = higher semantic similarity**
- Distance is typically **cosine distance**, but the logic is metric-agnostic

---

### Distance normalization

To convert distance into a bounded similarity score, the following formula is used:

\[
\text{retrieval\_score} = \frac{1}{1 + \text{distance}}
\]

#### Properties
- Output range: `(0, 1]`
- Monotonically decreasing
- Works for cosine, Euclidean, or other distance metrics

#### Example

| Distance | Retrieval Score |
|--------|----------------|
| 0.00 | 1.000 |
| 0.10 | 0.909 |
| 0.30 | 0.769 |
| 0.50 | 0.667 |

---

## 2. LOINC Agreement Score (20%)

### What it measures
Symbolic consistency between the recommended LOINC codes and the original LOINC.

### Scoring logic

| Condition | Score |
|--------|------|
| Original LOINC equals top candidate | 1.0 |
| Original LOINC appears in candidate list | 0.7 |
| Original LOINC not present | 0.4 |

This protects against over-reliance on embeddings and reinforces coding stability.

---

## 3. Unit Quality Score (20%)

### What it measures
Clinical validity of the unit associated with the observation.

### Scoring logic

| Unit Condition | Score |
|--------------|------|
| Missing or empty unit | 0.3 |
| Generic unit (`{score}`) | 0.6 |
| Valid clinical unit | 1.0 |

Incorrect or missing units significantly reduce mapping reliability.

---

## Final Confidence Formula

The final confidence score is calculated as a weighted sum of the three components:

\[
\text{confidence} =
0.6 \times \text{retrieval\_score} +
0.2 \times \text{loinc\_match\_score} +
0.2 \times \text{unit\_score}
\]

The result is rounded to three decimal places.

---

## Example Calculation

**Inputs**
- Vector distance: `0.15`
- Original LOINC matches top candidate
- Unit is valid (`/min`)

**Scores**
- Retrieval score = `1 / (1 + 0.15)` = `0.870`
- LOINC agreement score = `1.0`
- Unit score = `1.0`

**Final confidence**

```text
0.6 × 0.870 + 0.2 × 1.0 + 0.2 × 1.0 = 0.922
```

---

## Interpretation Guidelines

| Confidence Range | Meaning |
|----------------|--------|
| ≥ 0.90 | High confidence — safe to auto-accept |
| 0.75 – 0.89 | Moderate confidence — review recommended |
| < 0.75 | Low confidence — manual validation required |

---

## Summary

- Vector distance provides semantic similarity (lower is better)
- LOINC agreement ensures symbolic consistency
- Unit validation enforces clinical correctness
- Weighted combination yields a robust, interpretable confidence score

This approach balances **semantic intelligence** with **clinical safety**.
