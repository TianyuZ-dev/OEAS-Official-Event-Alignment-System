#!/usr/bin/env python3
from __future__ import annotations

import getpass
import os
from pathlib import Path


SECRET_PATH = Path("config/api_keys.txt")

FIELDS = [
    ("TOGETHER_API_KEY", "Together AI API key"),
    ("FIREWORKS_API_KEY", "Fireworks AI API key"),
    ("GEMINI_API_KEY", "Gemini API key (optional)"),
    ("CEREBRAS_API_KEY", "Cerebras API key (optional)"),
]


def main() -> int:
    path = SECRET_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                key, value = line.split("=", 1)
                existing[key.strip()] = value.strip()

    values = {}
    print("Enter API keys. Press Enter to keep existing values or leave optional keys blank.")
    for key, label in FIELDS:
        current = existing.get(key, "")
        suffix = " [already set]" if current else ""
        entered = getpass.getpass(f"{label}{suffix}: ").strip()
        values[key] = entered or current

    values["ANAS_PROVIDER"] = existing.get("ANAS_PROVIDER", "together")
    values["ANAS_MODEL"] = existing.get("ANAS_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo")
    values["ANAS_OUTPUT_DIR"] = existing.get("ANAS_OUTPUT_DIR", "output")

    content = ["# ANAS local API keys. Do not commit this file."]
    for key, value in values.items():
        content.append(f"{key}={value}")
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    print(f"{path} saved with permissions 600.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
