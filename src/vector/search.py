import faiss
import yaml
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

_index = None
_metadata = None
_model = None

def load_resources():
    global _index, _metadata, _model

    if _index:
        return

    with open("resources/config/paths.yaml") as f:
        config = yaml.safe_load(f)

    _index = faiss.read_index(config["vector_store"]["index_path"])

    with open(config["vector_store"]["metadata_path"], "rb") as f:
        _metadata = pickle.load(f)

    _model = SentenceTransformer("all-MiniLM-L6-v2")

def search_loinc(query: str, top_k: int = 5):
    load_resources()

    query_vector = _model.encode([query])
    query_vector = np.array(query_vector).astype("float32")

    distances, indices = _index.search(query_vector, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        record = _metadata[idx]
        results.append({
            "score": float(distances[0][i]),
            "loinc_num": record["LOINC_NUM"],
            "long_common_name": record["LONG_COMMON_NAME"],
            "system": record["SYSTEM"],
            "component": record["COMPONENT"]
        })

    return results
