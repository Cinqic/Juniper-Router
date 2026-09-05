from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SFTConfig:
    model_path: str
    train_path: Path
    output_dir: Path
    sequence_length: int = 512
    learning_rate: float = 2e-5
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    max_steps: int = 100
    seed: int = 42
    save_every: int = 50

    def __post_init__(self) -> None:
        if self.sequence_length not in {512, 1024, 2048, 8192}:
            raise ValueError("sequence_length must be a declared experiment value")
        if (
            self.learning_rate <= 0
            or not 1 <= self.batch_size <= 16
            or not 1 <= self.gradient_accumulation_steps <= 16
            or self.max_steps < 1
            or self.save_every < 1
        ):
            raise ValueError("invalid training budget")
