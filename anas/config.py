from __future__ import annotations

import os
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    provider: str = field(default_factory=lambda: os.getenv("ANAS_PROVIDER", "together"))
    model: str = field(default_factory=lambda: os.getenv("ANAS_MODEL", "meta-llama/Llama-3.3-70B-Instruct-Turbo"))
    output_dir: Path = field(default_factory=lambda: Path(os.getenv("ANAS_OUTPUT_DIR", "output")))
    request_timeout: int = field(default_factory=lambda: int(os.getenv("ANAS_REQUEST_TIMEOUT", "45")))
    llm_delay_seconds: float = field(default_factory=lambda: float(os.getenv("ANAS_LLM_DELAY_SECONDS", "0.2")))

