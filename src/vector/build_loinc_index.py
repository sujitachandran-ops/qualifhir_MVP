import json
import yaml
import os
import faiss
import pickle
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

def load_config():
    with open("resources/config/paths.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_loinc_index():
    config = load_config()
    loinc_path = config["loinc"]["catalog"]

    print(f"Loading LOINC catalog from: {loinc_path}")

    # 🔹 Load JSON
    with open(loinc_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if "Results" not in raw:
        raise ValueError("Invalid LOINC JSON format: 'Results' key not found")

    df = pd.DataFrame(raw["Results"])

    # 🔹 Keep only required columns
    df = df[[
        "LOINC_NUM",
        "LONG_COMMON_NAME",
        "COMPONENT",
        "SYSTEM"
    ]].dropna()

    print(f"Total LOINC records loaded: {len(df)}")

    # 🔹 Build embedding documents
    documents = (
    "LOINC: " + df["LOINC_NUM"] +
    " | Name: " + df["LONG_COMMON_NAME"] +
    " | Component: " + df["COMPONENT"] +
    " | System: " + df["SYSTEM"]
    ).tolist()

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings (this may take a few minutes)...")
    embeddings = model.encode(documents, show_progress_bar=True)

    vectors = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    os.makedirs("vectorstore", exist_ok=True)

    faiss.write_index(index, config["vector_store"]["index_path"])

    metadata = df.to_dict("records")
    with open(config["vector_store"]["metadata_path"], "wb") as f:
        pickle.dump(metadata, f)

    print("✅ LOINC FAISS index and metadata saved successfully")

if __name__ == "__main__":
    build_loinc_index()