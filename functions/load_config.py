import json
import os
from globals import Globals


def load_config():
    globals_instance = Globals()

    config_file_name = "config.json"
    config_path = None

    if globals_instance.app_data_dir:
        # Construct the full path using the app_data_dir
        config_path = os.path.join(globals_instance.app_data_dir, config_file_name)
        print(f"Attempting to load config from: {config_path}")  # For debugging
    else:
        print(
            f"Warning: app_data_dir is not set in Globals. Falling back to current directory for {config_file_name}."
        )
        # Fallback if app_data_dir is not set (e.g., if sidecar was run directly for testing)
        config_path = config_file_name

    try:
        if config_path:  # Ensure config_path was successfully determined
            with open(config_path, "r") as f:
                return json.load(f)
        else:
            # This case should ideally not be hit if config_path is properly handled
            print(
                "Error: Could not determine config file path. Returning default config."
            )
            return {
                "resumeModel": "gpt-4o-mini",
                "condensaModel": "gpt-4o-mini",
                "resumeChunkSize": 10000,
                "ragModel": "gpt-4o-mini",
                "ragSearchType": "mmr",
                "ragSearchK": 5,
                "ragChunkSize": 1000,
                "useWhisper": "no",
            }

    except Exception as e:
        print(
            f"An unexpected error occurred while loading config from '{config_path}': {e}. Returning default configuration."
        )
        return {
            "resumeModel": "gpt-4o-mini",
            "condensaModel": "gpt-4o-mini",
            "resumeChunkSize": 10000,
            "ragModel": "gpt-4o-mini",
            "ragSearchType": "mmr",
            "ragSearchK": 5,
            "ragChunkSize": 1000,
            "useWhisper": "no",
        }