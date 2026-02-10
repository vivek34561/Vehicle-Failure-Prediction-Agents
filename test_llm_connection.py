
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.responses.create(
    input="Explain the importance of fast language models",
    model="openai/gpt-oss-20b",
    max_output_tokens=512
)

out = getattr(response, "output_text", None)
if not out and isinstance(response, dict):
    out = response.get("output_text") or str(response)

print(out)
