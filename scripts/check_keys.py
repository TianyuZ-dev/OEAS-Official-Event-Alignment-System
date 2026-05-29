#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from anas.env import load_api_keys


REQUIRED = []
OPTIONAL = ["TOGETHER_API_KEY", "FIREWORKS_API_KEY", "GEMINI_API_KEY", "CEREBRAS_API_KEY"]


def masked(value: str) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"{value[:4]}...{value[-4:]}"


def main() -> int:
    load_api_keys()
    for key in REQUIRED + OPTIONAL:
        print(f"{key}: {masked(os.getenv(key, ''))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
