import os
from openai import AzureOpenAI
from src.config.env_config import load_env

# Load environment variables
load_env()

def setup_openai_client():
    """Initializes Azure OpenAI API client."""
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

client = setup_openai_client()
