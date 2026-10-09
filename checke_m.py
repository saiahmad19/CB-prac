from dotenv import load_dotenv
import os
import requests

load_dotenv()
my_key = os.environ.get("GROQ_API_KEY")

url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {my_key}"}
response = requests.get(url, headers=headers)
print(response.json())
