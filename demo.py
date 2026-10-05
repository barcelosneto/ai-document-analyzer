import json
from pathlib import Path
from app.providers import MockProvider

if __name__ == "__main__":
    for path in sorted(Path("samples").glob("*.txt")):
        print(json.dumps({"document": path.name, "provider": "mock", "analysis": MockProvider().analyze(path.read_text(encoding="utf-8")).model_dump()}, ensure_ascii=False, indent=2))
