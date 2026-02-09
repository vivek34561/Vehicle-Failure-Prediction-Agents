
import sys
import importlib

packages = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic_ai", # Note: package name might differ from import name
    "griffe",
    "google.generativeai",
    "dotenv"
]

results = []

for pkg in packages:
    try:
        importlib.import_module(pkg)
        results.append(f"{pkg}: OK")
    except ImportError as e:
        results.append(f"{pkg}: FAILED ({e})")
    except Exception as e:
        results.append(f"{pkg}: ERROR ({e})")

with open("env_check_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
