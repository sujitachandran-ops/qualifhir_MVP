"""
RAG pipeline
Module: LOINC Vector Index Builder (QualiFHIR - Phase 2)
--------------------------------------------------------
This script serves as the foundation for the semantic search engine (RAG Pipeline). 
Its primary function is to transform the static LOINC catalog (text) into a 
vector database (mathematical representation) to enable context-aware similarity searches.

Execution Flow:
1.  Data Ingestion: Loads the master LOINC CSV file defined in configuration.
2.  Enrichment: Concatenates 'Common Name' with 'LOINC Code' to generate 
    embeddings with richer semantic context.
3.  Vectorization: Uses the 'all-MiniLM-L6-v2' model (Sentence-Transformers) 
    to convert each entry into a 384-dimensional vector.
4.  Indexing (FAISS): Organizes these vectors into an optimized structure (IndexFlatL2) 
    for high-speed similarity retrieval.
5.  Persistence: 
    - Saves the physical index (.faiss) for mathematical operations.
    - Serializes metadata (.pkl) to map results back to human-readable medical information (Code, Name, System).

Outputs (Artifacts):
- vectorstore/loinc_index.faiss
- vectorstore/loinc_metadata.pkl
"""


import pandas as pd
import numpy as np
import faiss
import yaml
import os
from pathlib import Path
import pickle
from sentence_transformers import SentenceTransformer

# ==========================================================================
# Global variables
# ==========================================================================
config = {}

project_root = Path(__file__).resolve().parent.parent.parent
yaml_configs = project_root / 'resources/config/paths.yaml'


# ==========================================================================
# Functions
# ==========================================================================
def load_config():
    global config

    # Open and load YAML configs
    try:
        with open(yaml_configs, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            print(f'Configuration succcessfull')
            print(project_root)
    except FileNotFoundError:
        print(f'Error: YAML file was not found {yaml_configs}')


def build_loinc_index():
    # Load YAML configurations
    load_config()

    print('--- STARTING VECTOR ENGINE BUILD FOR LOINC CODES ---')
    
    # Load the LOINC master catalog
    loinc_path = project_root / config['references']['loinc']
    print(f'Reading master catalog from: {loinc_path}')
    
    # Assume CSV has standard LOINC columns. All data is treated as strings to avoid type issues.
    df = pd.read_csv(loinc_path, dtype=str).fillna('')
    
    # Create a list of text documents to vectorize.
    # Concatenating common name with the code provides better context for the model.
    documents = (df['LONG_COMMON_NAME'] + ' (' + df['LOINC_NUM'] + ')').tolist()
    
    # Initialize the Embedding Model. This model converts text into 384-dimensional numerical vectors
    print('Loading AI model (all-MiniLM-L6-v2)...')
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate Vectors (Embeddings)
    print(f'Generating embeddings for {len(documents)} codes (this may take a while)...')
    embeddings = model.encode(documents, show_progress_bar=True)
    
    # Convert to float32, which is required by FAISS
    embeddings_np = np.array(embeddings).astype('float32')

    # Create FAISS Index
    dimension = embeddings_np.shape[1] # 384 dimensions
    index = faiss.IndexFlatL2(dimension) # L2 = Euclidean Distance (standard search)
    index.add(embeddings_np)
    
    print(f'Index built with {index.ntotal} vectors.')

    # Save Artifacts
    output_dir = os.path.dirname(project_root / config['vector_store']['index_loinc_path'])
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the mathematical index (FAISS file)
    faiss_path = project_root / config['vector_store']['index_loinc_path']
    faiss.write_index(index, str(faiss_path))
    print(f'Index for LOINC codes saved to: {faiss_path}')
    
    # Save metadata (ID -> Real Code Mapping). Essential to map Vector ID to human-readable LOINC Code
    metadata_path = os.path.join(output_dir, 'loinc_metadata.pkl')
    metadata = df[['LOINC_NUM', 'LONG_COMMON_NAME', 'COMPONENT', 'SYSTEM']].to_dict('records')
    
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    print(f'Metadata for LOINC codes saved to: {metadata_path}') 
    print(f'--- PROCESS COMPLETED FOR LOINC CODES ---')


# ==========================================================================
# Handler
# ==========================================================================
if __name__ == '__main__':
    build_loinc_index()