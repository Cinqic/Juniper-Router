from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SFTConfig:
    model_path: str
    train_path: Path
    output_dir: Path
    method: str = "full"
    prompt_mode: str = "full"
    target_serialization: str = "ordered-v1"
    sequence_length: int = 512
    learning_rate: float = 2e-5
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    max_steps: int = 100
    seed: int = 42
    save_every: int = 50
    eval_path: Path | None = None
    eval_every: int = 25
    eval_limit: int = 32
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05

    def __post_init__(self) -> None:
        if self.method not in {"full", "lora"}:
            raise ValueError("method must be full or lora")
        if self.prompt_mode not in {"full", "compact"}:
            raise ValueError("prompt_mode must be full or compact")
        if self.target_serialization not in {"ordered-v1", "sorted-keys-v1"}:
            raise ValueError("target_serialization must be ordered-v1 or sorted-keys-v1")
        if self.sequence_length not in {512, 1024, 2048, 8192}:
            raise ValueError("sequence_length must be a declared experiment value")
        if (
            self.learning_rate <= 0
            or not 1 <= self.batch_size <= 16
            or not 1 <= self.gradient_accumulation_steps <= 16
            or self.max_steps < 1
            or self.save_every < 1
            or self.eval_every < 1
            or self.eval_limit < 1
            or self.lora_r < 1
            or self.lora_alpha < 1
            or not 0 <= self.lora_dropout < 1
        ):
            raise ValueError("invalid training budget")
