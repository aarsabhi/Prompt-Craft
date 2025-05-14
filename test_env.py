import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Azure OpenAI environment variables
print("Checking Azure OpenAI Environment Variables:")
print("-" * 50)

# Check API Key
api_key = os.getenv("AZURE_OPENAI_KEY")
print(f"AZURE_OPENAI_KEY: {'✓ Set' if api_key else '✗ Not Set'}")
if api_key:
    print(f"Key value: {api_key}")

# Check API Base/Endpoint
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
print(f"AZURE_OPENAI_ENDPOINT: {'✓ Set' if api_base else '✗ Not Set'}")
if api_base:
    print(f"Endpoint value: {api_base}")

# Check Deployment Name
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
print(f"AZURE_OPENAI_DEPLOYMENT: {'✓ Set' if deployment else '✗ Not Set'}")
if deployment:
    print(f"Deployment value: {deployment}")

# Check API Version
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
print(f"AZURE_OPENAI_API_VERSION: {'✓ Set' if api_version else '✗ Not Set'}")
if api_version:
    print(f"API Version value: {api_version}")

print("\nExpected Values:")
print("-" * 50)
print("API Key: d2fc3cb33a1046b5936b9d9995322f2d")
print("Endpoint: https://idpoai.openai.azure.com/")
print("Deployment: gpt-4o")
print("API Version: 2024-02-15-preview") 