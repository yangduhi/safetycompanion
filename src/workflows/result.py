from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WorkflowResult:
    artifacts: list[Path] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    output_text: str | None = None
    success: bool = True
