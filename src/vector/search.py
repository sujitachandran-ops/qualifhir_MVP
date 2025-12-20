"""
Module: LOINC Semantic Search Engine (QualiFHIR - Phase 2)
----------------------------------------------------------
This module provides the interface to query the vector database created in the build phase.
It implements a "Retrieval" mechanism using FAISS and Sentence-Transformers to find 
clinically relevant LOINC codes based on semantic similarity, rather than exact text matching.

Key Features:
- Singleton Pattern: Loads the heavy AI model and Index into memory only once.
- Vectorization: Converts raw input text (e.g., "fasting sugar") into embeddings.
- Similarity Search: Queries the FAISS index using Euclidean distance (L2).
- Metadata Mapping: Resolves abstract vector IDs back to human-readable LOINC details.

Usage:
    from src.vector.search import search_loinc
    results = search_loinc("blood glucose fasting", top_k=5)
"""

import faiss
import pickle
import numpy as np
import yaml
import os
from sentence_transformers import SentenceTransformer


# ==========================================================================
# Global variables for Singleton pattern (caching resources in memory)
# ==========================================================================
_index = None
_metadata = None
_model = None
_config = None


# ==========================================================================
# Functions
# ==========================================================================
def _load_config():
    """
    Loads the project configuration. 
    Tries to find paths.yaml relative to the execution context.
    """
    global _config

    if _config is not None:
        return _config

    # Standard path assumption
    possible_paths = [
        "resources/config/paths.yaml",
        "../resources/config/paths.yaml",
        os.path.join(os.path.dirname(__file__), "../../resources/config/paths.yaml")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                _config = yaml.safe_load(f)
            return _config
            
    # Fallback default configuration if yaml is missing
    print("Warning: Config file not found. Using default paths.")
    return {
        'vector_store': {'index_path': 'vectorstore/loinc_index.faiss'}
    }

def load_resources():
    """
    Initializes the Search Engine by loading the required artifacts into memory.
    
    Resources loaded:
    1. FAISS Index (.faiss): The mathematical vector space.
    2. Metadata (.pkl): The dictionary mapping Vector IDs to LOINC Data.
    3. AI Model (all-MiniLM-L6-v2): The neural network for text embedding.
    
    Raises:
        FileNotFoundError: If the index or metadata files do not exist.
    """
    global _index, _metadata, _model
    
    # Avoid reloading if already in memory
    if _index is not None and _metadata is not None and _model is not None:
        return

    config = _load_config()
    index_path = config['vector_store']['index_loinc_path']
    
    # Verify file existence
    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"FAISS index not found at '{index_path}'. Please run 'src/vector/build_loinc_index.py' first."
        )

    # 1. Load FAISS Index
    print(f"Loading FAISS index from: {index_path}...")
    # cast to str() is required for Windows compatibility in some FAISS versions
    _index = faiss.read_index(str(index_path))

    # 2. Load Metadata
    # We assume metadata is in the same directory with .pkl extension
    metadata_path = index_path.replace('index_loinc_path.faiss', 'loinc_metadata.pkl')
    
    # Fallback check if the name differs slightly
    if not os.path.exists(metadata_path):
         metadata_path = os.path.join(os.path.dirname(index_path), "loinc_metadata.pkl")

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found at '{metadata_path}'")

    print(f"Loading metadata from: {metadata_path}...")
    with open(metadata_path, 'rb') as f:
        _metadata = pickle.load(f)

    # 3. Load AI Model
    if _model is None:
        print("Loading AI Model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')

    print("--- Search Engine Ready ---")

def search_loinc(query_text: str, top_k: int = 5) -> list:
    """
    Performs a semantic search against the LOINC index.

    Args:
        query_text (str): The clinical text to search for (e.g., "glucose lvl").
        top_k (int): The number of closest matches to return. Defaults to 5.

    Returns:
        list[dict]: A list of dictionaries representing the found LOINC codes.
                    Each dict contains: 'score', 'loinc_num', 'long_common_name', etc.
    """
    # Ensure all resources are loaded
    load_resources()
    
    # 1. Vectorize the input query
    # Encode returns a list of vectors, we take the first one since we have 1 query
    query_vector = _model.encode([query_text])
    
    # Convert to float32 (required by FAISS)
    query_vector = np.array(query_vector).astype('float32')
    
    # 2. Search in FAISS
    # D: Distances (Similarity scores), I: Indices (Row IDs in the database)
    distances, indices = _index.search(query_vector, top_k)
    
    results = []
    
    # 3. Process results
    # We iterate over the first row of results (indices[0])
    for i, idx in enumerate(indices[0]):
        if idx == -1: 
            continue # FAISS returns -1 if not enough neighbors found
        
        # Retrieve the real data using the index ID
        record = _metadata[idx]
        score = distances[0][i]
        
        # Build the result object
        # Note: We check multiple keys to support both CSV and JSON origin schemas
        result_entry = {
            'score': float(score), # Lower L2 distance = Better match
            'loinc_num': record.get('LOINC_NUM', 'N/A'),
            'long_common_name': record.get('LONG_COMMON_NAME'),
            'system': record.get('SYSTEM', 'N/A'),
            'component': record.get('COMPONENT', 'N/A')
        }
        results.append(result_entry)
        
    return results


# ==========================================================================
# Handler
# ==========================================================================
if __name__ == "__main__":
    # This block only runs if you execute the script directly: python src/vector/search.py
    # This process is only for TESTING PURPOSES
    test_query = "fasting blood sugar"
    print(f"\nExample Query: '{test_query}'")
    
    try:
        matches = search_loinc(test_query, top_k=5)
        
        print(f"\nFound {len(matches)} matches:")
        for m in matches:
            print("-" * 40)
            print(f"Score : {m['score']:.4f}")
            print(f"Code  : {m['loinc_num']}")
            print(f"Name  : {m['long_common_name']}")
            print(f"System: {m['system']}")
            
    except Exception as e:
        print(f"\nERROR during search: {e}")