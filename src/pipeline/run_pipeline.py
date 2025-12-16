"""
Pipeline Runner
----------------
This script is responsible for orchestrating the execution of the pipeline,
loading configurations and executing the transformations.
"""


import yaml
import os
import pandas as pd
from src.etl.clean_patient import parse_patient
from src.etl.clean_observation import parse_observation


# ==========================================================================
# Global variables
# ==========================================================================
config = {}
yaml_configs = "pipeline_config.yaml"


# ==========================================================================
# Functions
# ==========================================================================
def get_configuration():
    global config

    # Get run_pipeline.py path
    current_folder = os.path.dirname(os.path.abspath(__file__))
    
    # Create YAML file path
    yaml_path = os.path.join(current_folder, yaml_configs)

    # Open and load YAML configs
    try:
        with open(yaml_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            print(f"Configuration succcessfull")
    except FileNotFoundError:
        print(f"Error: YAML file was not found {yaml_path}")
    
def main():
    # Load YAML configurations
    get_configuration()

    # Get clean patients
    patients = parse_patient(config['raw_data']['patients'])
    if len(patients) > 0:
        # Create dataset to be saved
        df_patients = pd.DataFrame(patients)

        # TODO: implement logic to save cleaned data

    # Get clean observations
    observations = parse_observation(config['raw_data']['observations'])
    if len(observations) > 0:
        # Create dataset to be saved
        df_observations = pd.DataFrame(observations)

        # TODO: implement logic to save cleaned data


# ==========================================================================
# Handler
# ==========================================================================
if __name__ == "__main__":
    main()