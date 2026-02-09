
import asyncio
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Copying config from agents_final.py
FIXED_API_KEY = "ff79bbc8103b418ca138a15734256bab.cf3FccbTvaGzs4PXIz8AHblp"

model = OpenAIModel(
    model_name="x-ai/grok-3-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=FIXED_API_KEY
)

agent = Agent(model, system_prompt="You are a helpful assistant.")

async def main():
    print(f"Testing model {model.model_name} with base_url {model.base_url}")
    print(f"Key (first 5 chars): {FIXED_API_KEY[:5]}...")
    try:
        result = await agent.run("Hello, are you working?")
        print("Success!")
        print(result.data)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
