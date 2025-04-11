import requests
from openai import OpenAI
from openai import AzureOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from the .env file present in the code.
load_dotenv("../code/.env")

# Azure OpenAI configuration
api_version = os.getenv("OPENAI_API_VERSION")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")


client = AzureOpenAI(api_version=api_version, azure_endpoint=azure_endpoint,api_key=api_key,)

prompt = f"""
        Hello, OpenAI!
        """
res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear and concise summaries.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
        top_p=0.6,
        frequency_penalty=0.7,
    )

print(res.choices[0].message.content)