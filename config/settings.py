import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

config = load_config()

# Usage examples
GROQ_API_KEY = config["groq_api_key"]
MODEL_NAME = config["model"]